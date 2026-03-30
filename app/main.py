from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse, ApprovalDecision
from app.orchestrator import handle_message


app = FastAPI(title="SupportDesk Copilot", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return handle_message(req.session_id, req.user_message)


@app.post("/approval")
def approval(decision: ApprovalDecision) -> dict[str, str]:
    # TODO: persist decision into DB / approval_requests table
    return {
        "approval_id": decision.approval_id,
        "decision": decision.decision,
        "reviewer": decision.reviewer,
    }
