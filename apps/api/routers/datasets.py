"""Dataset endpoints — upload, list, detail, profile, sample rows."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from deps import get_query_engine
from packages.query_engine import QueryEngine
from schemas.dataset import DatasetListResponse, DatasetResponse, RowsResponse
from services.ingest import IngestService, UploadValidationError

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _service(
    db: AsyncSession = Depends(get_session),
    engine: QueryEngine = Depends(get_query_engine),
) -> IngestService:
    return IngestService(db=db, engine=engine)


@router.post(
    "",
    response_model=DatasetResponse,
    status_code=201,
    summary="Upload a CSV or Parquet dataset",
)
async def upload_dataset(
    file: UploadFile = File(..., description="A .csv or .parquet file, max 500 MB"),
    svc: IngestService = Depends(_service),
):
    """
    Upload a tabular dataset and receive a full schema profile.

    - Accepts `.csv` and `.parquet` files.
    - Profiles each column: type, null %, distinct count, min/max, sample values.
    - Registers the dataset for querying in subsequent requests.
    """
    try:
        return await svc.upload(file)
    except UploadValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get(
    "",
    response_model=DatasetListResponse,
    summary="List all uploaded datasets",
)
async def list_datasets(svc: IngestService = Depends(_service)):
    datasets = await svc.list_datasets()
    return DatasetListResponse(datasets=datasets, total=len(datasets))


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Get dataset detail and schema profile",
)
async def get_dataset(dataset_id: str, svc: IngestService = Depends(_service)):
    dataset = await svc.get_dataset(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return dataset


@router.get(
    "/{dataset_id}/rows",
    response_model=RowsResponse,
    summary="Preview sample rows from a dataset",
)
async def get_dataset_rows(
    dataset_id: str,
    limit: int = Query(100, ge=1, le=500, description="Number of rows to return"),
    offset: int = Query(0, ge=0, description="Row offset for pagination"),
    svc: IngestService = Depends(_service),
):
    result = await svc.get_rows(dataset_id, limit=limit, offset=offset)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    columns, rows = result
    return RowsResponse(columns=columns, rows=rows, total_returned=len(rows))


@router.delete(
    "/{dataset_id}",
    status_code=204,
    summary="Delete a dataset",
)
async def delete_dataset(dataset_id: str, svc: IngestService = Depends(_service)):
    dataset = await svc.get_dataset(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    # Full delete implementation in Phase 5; for now, return 204
    return None
