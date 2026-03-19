"""SQLAlchemy ORM models for app metadata."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_format: Mapped[str] = mapped_column(String, nullable=False)  # csv | parquet
    row_count: Mapped[int] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int] = mapped_column(Integer, nullable=True)
    profile: Mapped[dict] = mapped_column(JSON, nullable=True)  # schema profile JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    semantic_models: Mapped[list["SemanticModel"]] = relationship(back_populates="dataset")
    questions: Mapped[list["Question"]] = relationship(back_populates="dataset")


class SemanticModel(Base):
    __tablename__ = "semantic_models"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)  # parsed YAML as JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="semantic_models")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[str] = mapped_column(Text, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, nullable=True)
    trust_info: Mapped[dict] = mapped_column(JSON, nullable=True)
    confidence: Mapped[str] = mapped_column(String, nullable=True)  # high|medium|low|unsure
    flagged: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="questions")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="question")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), nullable=False)
    feedback_type: Mapped[str] = mapped_column(String, nullable=False)  # wrong|partial|correct
    note: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    question: Mapped["Question"] = relationship(back_populates="feedback")
