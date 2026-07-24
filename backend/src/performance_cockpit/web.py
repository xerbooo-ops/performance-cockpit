import html
from datetime import date
from pathlib import Path
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from performance_cockpit.database import (
    clear_database_caches,
    get_db,
    get_engine,
    initialize_database,
)
from performance_cockpit.services.csv_import import import_csv_text
from performance_cockpit.services.data_management import (
    import_history,
    reset_data,
    restore_backup,
    sqlite_database_path,
)
from performance_cockpit.services.file_import import import_xlsx_bytes
from performance_cockpit.services.metrics import (
    get_comparison,
    get_dashboard,
    get_dashboard_filters,
    measurement_query,
)
from performance_cockpit.watcher import FileWatchService, select_report_file

router = APIRouter(include_in_schema=False)
DatabaseSession = Annotated[Session, Depends(get_db)]
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_BACKUP_BYTES = 100 * 1024 * 1024

STYLES = """
:root{font-family:Inter,Segoe UI,sans-serif;color:#17352d;background:#f4f7f5}
*{box-sizing:border-box}body{margin:0}.topbar{background:#123d34;color:white;padding:1rem 5vw;
display:flex;justify-content:space-between;align-items:center}.topbar span{display:block;
color:#b9d9d0;
font-size:.85rem}main{width:min(1180px,92vw);margin:2rem auto}.hero,.panel,.card{background:white;
border:1px solid #dce7e2;border-radius:18px;box-shadow:0 16px 45px #1c3f3312}.hero{padding:2rem;
margin-bottom:1rem}.hero h1{font-size:clamp(2rem,5vw,4rem);margin:.2rem 0}.badge{color:#176c53;
font-weight:700}.panel{padding:1rem;margin:1rem 0}form{display:flex;flex-wrap:wrap;gap:.8rem;
align-items:end}label{display:grid;gap:.35rem;font-weight:700}input,select,button,.button{font:inherit;
padding:.7rem .9rem;border-radius:10px;border:1px solid #b8ccc5;background:white}button,.button{
background:#176c53;color:white;border:0;text-decoration:none;font-weight:700;cursor:pointer}.grid{
display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}.card{padding:1.2rem}
.card h3{font-size:.95rem;margin-top:0}.value{font-size:2rem;font-weight:800}.meta{color:#61776f;
font-size:.85rem}.notice{padding:.8rem 1rem;border-radius:10px;background:#def4eb;color:#176c53}
table{width:100%;border-collapse:collapse;background:white}th,td{padding:.75rem;text-align:left;
border-bottom:1px solid #e3ebe7}section{margin:2rem 0}h2{margin-bottom:.7rem}.actions{display:flex;
gap:.7rem;flex-wrap:wrap}.danger{background:#9a342d}.empty{padding:2rem;text-align:center;color:#61776f}
@media(max-width:650px){.topbar{align-items:flex-start;gap:1rem;flex-direction:column}}
"""


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _number(value: object, unit: str) -> str:
    try:
        rendered = f"{float(str(value)):.2f}".rstrip("0").rstrip(".").replace(".", ",")
    except ValueError:
        rendered = str(value)
    suffix = "%" if unit == "Prozent" else unit
    return f"{rendered} {suffix}".strip()


def _redirect(message: str) -> RedirectResponse:
    return RedirectResponse(url=f"/?{urlencode({'message': message})}", status_code=303)


@router.get("/", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    session: DatabaseSession,
    organizational_unit: str = "",
    date_from: date | None = None,
    date_to: date | None = None,
    metric_key: str = "",
    message: str = "",
) -> HTMLResponse:
    watcher: FileWatchService = request.app.state.file_watcher
    watch_state = watcher.status()
    filters = get_dashboard_filters(session)
    unit = organizational_unit or next(iter(filters.organizational_units), "")
    dashboard = get_dashboard(session, unit, date_from, date_to) if unit else None
    summaries = dashboard.summaries if dashboard else []
    selected_metric = metric_key or (summaries[0].metric_key if summaries else "")
    measurements = (
        list(session.scalars(measurement_query(selected_metric, unit, date_from, date_to)))
        if selected_metric and unit
        else []
    )
    comparison = None
    if selected_metric:
        metric = next(
            (item for item in summaries if item.metric_key == selected_metric),
            None,
        )
        if metric is not None:
            from performance_cockpit.models import MetricDefinition

            definition = session.get(MetricDefinition, selected_metric)
            if definition is not None:
                comparison = get_comparison(session, definition, date_from, date_to)

    unit_options = "".join(
        f'<option value="{_escape(item)}"{" selected" if item == unit else ""}>'
        f"{_escape(item)}</option>"
        for item in filters.organizational_units
    )
    metric_options = "".join(
        f'<option value="{_escape(item.metric_key)}"'
        f"{' selected' if item.metric_key == selected_metric else ''}>"
        f"{_escape(item.display_name)}</option>"
        for item in summaries
    )
    cards = "".join(
        f'<article class="card"><h3>{_escape(item.display_name)}</h3>'
        f'<div class="value">{_escape(_number(item.value, item.unit))}</div>'
        f'<p class="meta">{item.measurement_count} Messwerte</p></article>'
        for item in summaries
    )
    trend_rows = "".join(
        f"<tr><td>{_escape(item.period_start)}</td><td>{_escape(item.period_end)}</td>"
        f"<td>{_escape(item.value)}</td></tr>"
        for item in measurements
    )
    comparison_rows = "".join(
        f"<tr><td>{_escape(item.organizational_unit or '')}</td>"
        f"<td>{_escape(_number(item.value, comparison.unit))}</td></tr>"
        for item in (comparison.entries if comparison else [])
    )
    history_rows = "".join(
        f"<tr><td>{_escape(item.file_name)}</td><td>{_escape(item.status)}</td>"
        f"<td>{item.imported_rows}</td><td>{item.failed_rows}</td></tr>"
        for item in import_history(session)
    )
    query = {
        "organizational_unit": unit,
        **({"date_from": date_from.isoformat()} if date_from else {}),
        **({"date_to": date_to.isoformat()} if date_to else {}),
    }
    report_query = urlencode(query)
    notice = f'<p class="notice">{_escape(message)}</p>' if message else ""
    watched_name = Path(watch_state.file_path).name if watch_state.file_path else ""
    watch_status = (
        f"Aktiv: {_escape(watched_name)}"
        + (
            f" · zuletzt importiert {_escape(watch_state.last_imported_at)}"
            if watch_state.last_imported_at
            else ""
        )
        if watched_name
        else "Noch keine Datei zur automatischen Aktualisierung ausgewählt."
    )
    watch_error = (
        f'<p class="notice danger">{_escape(watch_state.last_error)}</p>'
        if watch_state.last_error
        else ""
    )
    content = f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="10">
<title>Performance Cockpit</title>
<style>{STYLES}</style></head><body>
<header class="topbar"><div><strong>Performance Cockpit</strong>
<span>Python-only · EPA-Anonymisierung</span></div>
<form action="/web/import" method="post" enctype="multipart/form-data">
<label>Datei importieren<input name="file" type="file" accept=".csv,.xlsx" required></label>
<button type="submit">Importieren</button></form></header>
<main><section class="hero"><span class="badge">● vollständig lokal</span>
<h1>Leistung auf einen Blick.</h1><p>Ohne Node.js, TypeScript oder externe Dienste.</p></section>
{notice}
<section class="panel"><h2>Automatische Aktualisierung</h2>
<p>{watch_status}</p>{watch_error}<div class="actions">
<form action="/web/watch/select" method="post">
<button type="submit">Reportdatei auswählen</button></form>
<form action="/web/watch/check" method="post">
<button type="submit">Jetzt prüfen</button></form>
<form action="/web/watch/clear" method="post">
<button class="danger" type="submit">Überwachung beenden</button></form>
</div><p class="meta">Die lokale Datei wird alle 5 Sekunden geprüft. Das Dashboard aktualisiert
sich alle 10 Sekunden automatisch.</p></section>
<section class="panel"><form method="get" action="/">
<label>Organisationseinheit<select name="organizational_unit">{unit_options}</select></label>
<label>Von<input type="date" name="date_from" value="{date_from or ""}"></label>
<label>Bis<input type="date" name="date_to" value="{date_to or ""}"></label>
<label>Kennzahl<select name="metric_key">{metric_options}</select></label>
<button type="submit">Anwenden</button></form></section>
<section><h2>{_escape(unit or "Noch keine Daten")}</h2>
<div class="grid">{cards or '<div class="card empty">Noch keine Kennzahlen vorhanden.</div>'}</div>
</section>
<section><h2>Zeitverlauf</h2><table><thead><tr><th>Von</th><th>Bis</th><th>Wert</th></tr>
</thead><tbody>
{trend_rows or '<tr><td colspan="3">Keine Werte vorhanden.</td></tr>'}
</tbody></table></section>
<section><h2>Organisationseinheiten</h2><table><thead><tr><th>EPA</th><th>Wert</th></tr>
</thead><tbody>{comparison_rows or '<tr><td colspan="2">Keine Vergleichsdaten.</td></tr>'}</tbody>
</table></section>
<section><h2>Lokale Datenverwaltung</h2><div class="actions">
<a class="button" href="/api/v1/data/export.xlsx">Excel herunterladen</a>
<a class="button" href="/api/v1/data/export.csv">CSV herunterladen</a>
<a class="button" href="/api/v1/data/report.pdf?{_escape(report_query)}">PDF herunterladen</a>
<a class="button" href="/api/v1/data/backup">Backup speichern</a></div>
<div class="panel"><form action="/web/restore" method="post" enctype="multipart/form-data">
<label>Backup wiederherstellen<input name="file" type="file" accept=".db" required></label>
<button type="submit">Wiederherstellen</button></form></div>
<div class="panel"><form action="/web/reset" method="post">
<label>Zum Löschen DELETE eingeben<input name="confirmation" required></label>
<button class="danger" type="submit">Daten zurücksetzen</button></form></div></section>
<section><h2>Importhistorie</h2><table><thead><tr><th>Datei</th><th>Status</th>
<th>Importiert</th><th>Fehler</th></tr></thead><tbody>
{history_rows or '<tr><td colspan="4">Noch keine Importe vorhanden.</td></tr>'}
</tbody></table></section>
</main></body></html>"""
    return HTMLResponse(content)


@router.post("/web/watch/select")
def dashboard_watch_select(request: Request) -> RedirectResponse:
    selected = select_report_file()
    if selected is None:
        return _redirect("Dateiauswahl abgebrochen.")
    watcher: FileWatchService = request.app.state.file_watcher
    try:
        watcher.select_file(selected)
    except ValueError as error:
        return _redirect(str(error))
    return _redirect(f"{selected.name} wird jetzt automatisch überwacht.")


@router.post("/web/watch/check")
def dashboard_watch_check(request: Request) -> RedirectResponse:
    watcher: FileWatchService = request.app.state.file_watcher
    changed = watcher.check_once()
    return _redirect(
        "Dateiänderung importiert." if changed else "Keine neue Dateiänderung erkannt."
    )


@router.post("/web/watch/clear")
def dashboard_watch_clear(request: Request) -> RedirectResponse:
    watcher: FileWatchService = request.app.state.file_watcher
    watcher.clear()
    return _redirect("Automatische Dateiüberwachung beendet.")


@router.post("/web/import")
async def dashboard_import(
    session: DatabaseSession,
    file: Annotated[UploadFile, File()],
) -> RedirectResponse:
    suffix = file.filename.lower().rsplit(".", maxsplit=1)[-1] if file.filename else ""
    if suffix not in {"csv", "xlsx"}:
        return _redirect("Bitte eine CSV- oder XLSX-Datei auswählen.")
    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        return _redirect("Die Datei überschreitet 5 MB.")
    try:
        result = (
            import_xlsx_bytes(session, file.filename or "import.xlsx", payload)
            if suffix == "xlsx"
            else import_csv_text(
                session,
                file.filename or "import.csv",
                payload.decode("utf-8-sig"),
            )
        )
    except (OSError, ValueError, KeyError, UnicodeDecodeError):
        return _redirect("Die Datei konnte nicht gelesen werden.")
    return _redirect(f"{result.imported_rows} Zeilen importiert, {result.failed_rows} fehlerhaft.")


@router.post("/web/reset")
def dashboard_reset(
    session: DatabaseSession,
    confirmation: Annotated[str, Form()],
) -> RedirectResponse:
    if confirmation != "DELETE":
        return _redirect("Zurücksetzen abgebrochen: Bestätigung war nicht DELETE.")
    reset_data(session)
    return _redirect("Alle lokalen Daten wurden gelöscht.")


@router.post("/web/restore")
async def dashboard_restore(
    request: Request,
    session: DatabaseSession,
    file: Annotated[UploadFile, File()],
) -> RedirectResponse:
    if not file.filename or not file.filename.lower().endswith(".db"):
        return _redirect("Bitte ein Performance-Cockpit-Backup auswählen.")
    payload = await file.read(MAX_BACKUP_BYTES + 1)
    if len(payload) > MAX_BACKUP_BYTES:
        return _redirect("Das Backup überschreitet 100 MB.")
    try:
        database_path = sqlite_database_path(request.app.state.settings.database_url)
        session.close()
        get_engine().dispose()
        clear_database_caches()
        restore_backup(Path(database_path), payload)
        initialize_database(request.app.state.settings)
    except ValueError:
        return _redirect("Das Backup ist ungültig.")
    return _redirect("Backup wiederhergestellt.")
