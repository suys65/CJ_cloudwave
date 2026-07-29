from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.router import classify_question, execute_route
from backend.incident_service import analyze_incident

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    category: str
    answer: str
    analysis: dict | None = None
    raw_data: dict | None = None

app = FastAPI(
    title="AWS Operations Copilot API",
    version="1.0.0",
)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        decision = classify_question(request.message)

        operational_data = execute_route(
            category=decision.category,
            time_range_minutes=decision.time_range_minutes,
        )

        analysis = analyze_incident(
            question=request.message,
            operational_data=operational_data,
        )

        return ChatResponse(
            category=decision.category,
            answer=analysis.summary,
            analysis=analysis.model_dump(),
            raw_data=operational_data,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
