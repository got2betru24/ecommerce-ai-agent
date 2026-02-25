from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import json

from .agent import run_agent

app = FastAPI(root_path="/api")

# CORS - allows the frontend container to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# Health check endpoint
@router.get("/health")
async def health():
    return {"status": "healthy"}


# Streaming chat endpoint
@router.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    async def stream_response():
        """
        Wraps run_agent generator and yields Server-Sent Events (SSE).
        SSE format: each message is 'data: <content>\n\n'
        The frontend reads these events and appends text as it arrives.
        """
        try:
            # Stream text chunks as SSE events
            for chunk in run_agent(request.message, session_id):
                # Encode chunk as SSE data event
                payload = json.dumps({"type": "chunk", "text": chunk})
                yield f"data: {payload}\n\n"

            # Send session_id in a final event so frontend can store it
            payload = json.dumps({"type": "done", "session_id": session_id})
            yield f"data: {payload}\n\n"

        except Exception as e:
            payload = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            # Prevent buffering - critical for streaming to work
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


app.include_router(router)
