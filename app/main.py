from fastapi import FastAPI
from app.persistence import SQLiteStore
from app.schemas import ApprovalDecision, ApprovalReviewRecord, ChatRequest, ChatResponse
from app.orchestrator import handle_message


app = FastAPI(title="SupportDesk Copilot", version="0.1.0")
store = SQLiteStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return handle_message(req.session_id, req.user_message, store=store)


@app.post("/approval", response_model=ApprovalReviewRecord)
def approval(decision: ApprovalDecision, session_id: str) -> ApprovalReviewRecord:
    return store.record_approval_review(decision, session_id=session_id)
