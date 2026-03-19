"""Dataset endpoints — upload, list, detail. (Stub for Phase 1; implemented in Phase 2.)"""

from fastapi import APIRouter

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", summary="List datasets")
async def list_datasets():
    return {"datasets": [], "message": "Dataset ingestion is implemented in Phase 2."}


@router.get("/{dataset_id}", summary="Get dataset detail")
async def get_dataset(dataset_id: str):
    return {"dataset_id": dataset_id, "message": "Dataset ingestion is implemented in Phase 2."}


@router.post("", summary="Upload a dataset", status_code=202)
async def upload_dataset():
    return {"message": "Dataset upload is implemented in Phase 2."}
