"""
QuestionService — orchestrates the analytics pipeline for Q&A.
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from packages.llm_adapter import LLMAdapter
from packages.query_engine import QueryEngine, execute_pipeline

from config import get_settings
from models import Dataset, Feedback, Question, SemanticModel
from schemas.question import (
    FeedbackCreate,
    FeedbackResponse,
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
)


class QuestionService:
    def __init__(self, db: AsyncSession, engine: QueryEngine) -> None:
        self._db = db
        self._engine = engine
        settings = get_settings()
        self._llm = LLMAdapter(settings)
        self._settings = settings

    # ── Ask ────────────────────────────────────────────────────────────────────

    async def ask(self, payload: QuestionCreate) -> QuestionResponse:
        # Load dataset
        dataset = await self._load_dataset(payload.dataset_id)
        if dataset is None:
            raise ValueError(f"Dataset '{payload.dataset_id}' not found.")

        # Load semantic model
        sem_model = await self._load_model(payload.dataset_id, payload.model_id)

        # Persist question record early so we have an ID
        question_record = Question(
            dataset_id=payload.dataset_id,
            question_text=payload.question,
        )
        self._db.add(question_record)
        await self._db.commit()
        await self._db.refresh(question_record)

        if sem_model is None:
            result_dict = asdict(
                __import__(
                    "packages.query_engine.pipeline_types",
                    fromlist=["PipelineResult"],
                ).PipelineResult.no_model(dataset.name)
            )
            # Patch question field
            result_dict["question"] = payload.question
            await self._persist_result(question_record, result_dict)
            return _to_response(question_record)

        # Run pipeline
        from packages.query_engine.pipeline_types import PipelineResult  # noqa: PLC0415

        result: PipelineResult = await execute_pipeline(
            question=payload.question,
            view_name=dataset.name,
            model_definition=sem_model.definition,
            engine=self._engine,
            llm=self._llm,
            settings=self._settings,
        )

        result_dict = asdict(result)
        await self._persist_result(question_record, result_dict)
        return _to_response(question_record)

    async def _persist_result(self, record: Question, result_dict: dict) -> None:
        """Write pipeline result back to the Question row."""
        record.generated_sql = result_dict.get("sql") or None
        record.confidence = result_dict.get("confidence")
        record.result = {
            "answer": result_dict.get("answer"),
            "columns": result_dict.get("columns", []),
            "rows": result_dict.get("rows", []),
            "row_count": result_dict.get("row_count", 0),
            "chart_type": result_dict.get("chart_type"),
            "semantic_mappings": result_dict.get("semantic_mappings", []),
            "assumptions": result_dict.get("assumptions", []),
            "caveats": result_dict.get("caveats", []),
            "confidence_note": result_dict.get("confidence_note"),
            "clarifying_question": result_dict.get("clarifying_question"),
            "execution_ms": result_dict.get("execution_ms"),
            "error": result_dict.get("error"),
        }
        record.trust_info = result_dict.get("provenance", {})
        await self._db.commit()
        await self._db.refresh(record)

    # ── List / Detail ──────────────────────────────────────────────────────────

    async def list(
        self, dataset_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> QuestionListResponse:
        stmt = select(Question).order_by(Question.created_at.desc()).limit(limit).offset(offset)
        if dataset_id:
            stmt = stmt.where(Question.dataset_id == dataset_id)
        result = await self._db.execute(stmt)
        rows = result.scalars().all()

        # Total count
        from sqlalchemy import func  # noqa: PLC0415
        count_stmt = select(func.count()).select_from(Question)
        if dataset_id:
            count_stmt = count_stmt.where(Question.dataset_id == dataset_id)
        total = (await self._db.execute(count_stmt)).scalar_one()

        return QuestionListResponse(
            questions=[_to_response(q) for q in rows],
            total=total,
        )

    async def get(self, question_id: str) -> QuestionResponse | None:
        result = await self._db.execute(
            select(Question).where(Question.id == question_id)
        )
        q = result.scalar_one_or_none()
        return _to_response(q) if q else None

    # ── Feedback ───────────────────────────────────────────────────────────────

    async def submit_feedback(
        self, question_id: str, payload: FeedbackCreate
    ) -> FeedbackResponse | None:
        # Verify question exists
        result = await self._db.execute(
            select(Question).where(Question.id == question_id)
        )
        if result.scalar_one_or_none() is None:
            return None

        fb = Feedback(
            question_id=question_id,
            feedback_type=payload.feedback_type,
            note=payload.note,
        )
        self._db.add(fb)
        await self._db.commit()
        await self._db.refresh(fb)
        return FeedbackResponse(
            id=fb.id,
            question_id=fb.question_id,
            feedback_type=fb.feedback_type,
            note=fb.note,
            created_at=fb.created_at,
        )

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _load_dataset(self, dataset_id: str) -> Dataset | None:
        result = await self._db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

    async def _load_model(
        self, dataset_id: str, model_id: str | None
    ) -> SemanticModel | None:
        if model_id:
            result = await self._db.execute(
                select(SemanticModel).where(SemanticModel.id == model_id)
            )
            return result.scalar_one_or_none()
        # Most recently updated model for the dataset
        result = await self._db.execute(
            select(SemanticModel)
            .where(SemanticModel.dataset_id == dataset_id)
            .order_by(SemanticModel.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


# ── Conversion helper ──────────────────────────────────────────────────────────


def _to_response(q: Question) -> QuestionResponse:
    r = q.result or {}
    return QuestionResponse(
        id=q.id,
        dataset_id=q.dataset_id,
        question=q.question_text,
        answer=r.get("answer"),
        sql=q.generated_sql,
        columns=r.get("columns", []),
        rows=r.get("rows", []),
        row_count=r.get("row_count", 0),
        chart_type=r.get("chart_type"),
        semantic_mappings=r.get("semantic_mappings", []),
        assumptions=r.get("assumptions", []),
        caveats=r.get("caveats", []),
        confidence=q.confidence,
        confidence_note=r.get("confidence_note"),
        clarifying_question=r.get("clarifying_question"),
        provenance=q.trust_info,
        execution_ms=r.get("execution_ms"),
        error=r.get("error"),
        created_at=q.created_at,
    )
