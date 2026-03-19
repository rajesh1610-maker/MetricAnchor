"""Question (Q&A) endpoints. (Stub for Phase 1; implemented in Phase 4.)"""

from fastapi import APIRouter

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", summary="List past questions")
async def list_questions():
    return {"questions": [], "message": "Q&A engine is implemented in Phase 4."}


@router.post("", summary="Ask a question", status_code=202)
async def ask_question():
    return {"message": "Q&A engine is implemented in Phase 4."}


@router.post("/{question_id}/feedback", summary="Submit feedback on an answer", status_code=202)
async def submit_feedback(question_id: str):
    return {"question_id": question_id, "message": "Feedback is implemented in Phase 4."}
