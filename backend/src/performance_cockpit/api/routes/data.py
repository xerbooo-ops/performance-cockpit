from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from performance_cockpit.database import (
    clear_database_caches,
    get_db,
    get_engine,
    initialize_database,
)
from performance_cockpit.schemas import DataActionResult, ImportBatchRead, ResetRequest
from performance_cockpit.services.data_management import (
    create_backup,
    export_dashboard_pdf,
    export_measurements_csv,
    export_measurements_xlsx,
    import_history,
    reset_data,
    restore_backup,
    sqlite_database_path,
)

router = APIRouter(prefix="/data", tags=["data management"])
DatabaseSession = Annotated[Session, Depends(get_db)]
MAX_BACKUP_BYTES = 100 * 1024 * 1024


def _local_database_path(request: Request):
    try:
        return sqlite_database_path(request.app.state.settings.database_url)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get("/imports", response_model=list[ImportBatchRead])
def list_imports(
    session: DatabaseSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ImportBatchRead]:
    return import_history(session, limit)


@router.get("/export.csv")
def export_csv(session: DatabaseSession) -> Response:
    content = export_measurements_csv(session)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="performance-cockpit-{timestamp}.csv"'
        },
    )


@router.get("/export.xlsx")
def export_xlsx(session: DatabaseSession) -> Response:
    content = export_measurements_xlsx(session)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="performance-cockpit-{timestamp}.xlsx"'
        },
    )


@router.get("/report.pdf")
def export_pdf(
    session: DatabaseSession,
    organizational_unit: Annotated[str, Query(min_length=1, max_length=120)],
    date_from: date | None = None,
    date_to: date | None = None,
) -> Response:
    content = export_dashboard_pdf(session, organizational_unit, date_from, date_to)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="performance-cockpit-{timestamp}.pdf"'
        },
    )


@router.get("/backup")
def download_backup(request: Request) -> Response:
    content = create_backup(_local_database_path(request))
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return Response(
        content=content,
        media_type="application/x-sqlite3",
        headers={
            "Content-Disposition": f'attachment; filename="performance-cockpit-{timestamp}.db"'
        },
    )


@router.post("/restore", response_model=DataActionResult)
async def restore_database(
    request: Request,
    session: DatabaseSession,
    file: Annotated[UploadFile, File(description="Performance Cockpit SQLite backup")],
) -> DataActionResult:
    if not file.filename or not file.filename.lower().endswith(".db"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="A Performance Cockpit DB backup is required",
        )
    content = await file.read(MAX_BACKUP_BYTES + 1)
    if len(content) > MAX_BACKUP_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Backup exceeds the 100 MB limit",
        )
    settings = request.app.state.settings
    database_path = _local_database_path(request)
    session.close()
    get_engine().dispose()
    clear_database_caches()
    try:
        restore_backup(database_path, content)
        initialize_database(settings)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    return DataActionResult(status="completed", message="Backup restored")


@router.post("/reset", response_model=DataActionResult)
def reset_database(request: ResetRequest, session: DatabaseSession) -> DataActionResult:
    if request.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Enter DELETE to confirm",
        )
    reset_data(session)
    return DataActionResult(status="completed", message="All local data deleted")
