from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from performance_cockpit.database import get_db
from performance_cockpit.schemas import ImportResult
from performance_cockpit.services.csv_import import import_csv_text

router = APIRouter(prefix="/imports", tags=["imports"])
DatabaseSession = Annotated[Session, Depends(get_db)]
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/csv", response_model=ImportResult)
async def import_csv(
    session: DatabaseSession,
    file: Annotated[UploadFile, File(description="UTF-8 CSV file with KPI measurements")],
) -> ImportResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="A CSV file is required",
        )
    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="CSV file exceeds the 5 MB limit",
        )
    try:
        content = payload.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSV file must be UTF-8 encoded",
        ) from error
    return import_csv_text(session, file.filename, content)
