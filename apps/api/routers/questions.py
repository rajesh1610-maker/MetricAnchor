"""Question (Q&A) endpoints — trust-first analytics pipeline."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from deps import get_query_engine
from packages.query_engine import QueryEngine
from schemas.question import (
    FeedbackCreate,
    FeedbackResponse,
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
)
from services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])


def _service(
    db: AsyncSession = Depends(get_session),
    engine: QueryEngine = Depends(get_query_engine),
) -> QuestionService:
    return QuestionService(db=db, engine=engine)


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=201,
    summary="Ask a natural-language analytics question",
)
async def ask_question(
    payload: QuestionCreate,
    svc: QuestionService = Depends(_service),
):
    """
    Run the full trust-first analytics pipeline:

    1. Parse the question into structured intent (stub or LLM)
    2. Map intent to semantic model concepts
    3. Generate deterministic SQL from the mapping
    4. Validate and execute the SQL against DuckDB
    5. Return the answer with SQL, semantic mappings, assumptions, confidence, and provenance

    Requires `dataset_id`. Uses the most recently updated semantic model for the
    dataset unless `model_id` is specified.
    """
    try:
        return await svc.ask(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "",
    response_model=QuestionListResponse,
    summary="List past questions",
)
async def list_questions(
    dataset_id: str | None = Query(None, description="Filter by dataset ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: QuestionService = Depends(_service),
):
    return await svc.list(dataset_id=dataset_id, limit=limit, offset=offset)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get a question with its full answer and provenance",
)
async def get_question(
    question_id: str,
    svc: QuestionService = Depends(_service),
):
    q = await svc.get(question_id)
    if q is None:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")
    return q


@router.post(
    "/{question_id}/feedback",
    response_model=FeedbackResponse,
    status_code=201,
    summary="Submit feedback on an answer",
)
async def submit_feedback(
    question_id: str,
    payload: FeedbackCreate,
    svc: QuestionService = Depends(_service),
):
    """Submit thumbs-up/thumbs-down feedback. feedback_type: wrong | partial | correct."""
    result = await svc.submit_feedback(question_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")
    return result
