# Anforderungen und priorisierte Kennzahlen

## Ziel von Release 0.2

Release 0.2 schafft das technische Fundament. Die nachfolgenden Anforderungen bilden den fachlichen Rahmen für Datenmodell, API und MVP, ohne deren Umsetzung vorwegzunehmen.

## Kernanforderungen

| Priorität | Anforderung | Akzeptanzkriterium |
| --- | --- | --- |
| Muss | Kennzahlen zentral anzeigen | Eine freigegebene Kennzahl kann mit Wert, Zeitraum, Ziel und Datenstand dargestellt werden. |
| Muss | Zeiträume filtern | Nutzer können mindestens Tag, Woche und Monat auswählen. |
| Muss | Datenqualität sichtbar machen | Datenstand und Validierungsstatus werden pro Kennzahl angezeigt. |
| Muss | Berechnungen nachvollziehen | Definition, Quelle und Berechnungsregel sind dokumentiert und abrufbar. |
| Soll | Zielabweichungen erkennen | Abweichungen werden absolut und prozentual ausgewiesen. |
| Soll | Zeitverläufe vergleichen | Aktueller und vorheriger Zeitraum können verglichen werden. |
| Später | Rollenbasierte Sichten | Inhalte lassen sich nach Rolle oder Verantwortungsbereich begrenzen. |

## Erste Kennzahlen

Die fachlichen Zielwerte und Quellsysteme werden vor Release 0.3 mit den Stakeholdern verbindlich festgelegt.

| Kennzahl | Arbeitsdefinition | Einheit | Aggregation |
| --- | --- | --- | --- |
| Zielerreichung | Ist-Wert geteilt durch Zielwert | Prozent | Zeitraum und Organisationseinheit |
| Vorgangsvolumen | Anzahl abgeschlossener Vorgänge | Anzahl | Zeitraum und Organisationseinheit |
| Bearbeitungszeit | Durchschnittliche Dauer je abgeschlossenem Vorgang | Zeit | Zeitraum und Organisationseinheit |
| Qualitätsquote | Positiv bewertete Vorgänge geteilt durch bewertete Vorgänge | Prozent | Zeitraum und Organisationseinheit |

## Nichtfunktionale Anforderungen

- API-Antworten für Standardabfragen sollen unter Normalbelastung in höchstens 500 ms bereitstehen.
- Alle Kennzahlberechnungen müssen automatisiert testbar und versioniert sein.
- Geheimnisse und produktive Daten dürfen nicht im Repository liegen.
- Logs müssen maschinenlesbar sein und dürfen keine sensiblen Inhalte enthalten.
- Die Benutzeroberfläche soll responsiv und tastaturbedienbar entwickelt werden.
- Builds und Tests müssen in Continuous Integration reproduzierbar laufen.

## Offene fachliche Entscheidungen

- Verbindliche Eigentümer und Definitionen der Kennzahlen
- Priorisierte Datenquelle für den ersten Import
- Zielwerte und erlaubte Aggregationsstufen
- Umgang mit fehlenden, verspäteten oder korrigierten Daten
- Benötigte Rollen und Sichtbarkeitsregeln
