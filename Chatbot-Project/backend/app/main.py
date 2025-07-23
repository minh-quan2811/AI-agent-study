from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .graph import graph
from uuid import uuid4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid4())
    config = {"configurable": {"thread_id": sid}}

    last_reply = None
    for event in graph.stream(
        {"messages": ("user", req.message)},
        config=config,
        stream_mode="values",
    ):
        msg = event["messages"][-1]
        last_reply = getattr(msg, "content", str(msg))

    return ChatResponse(session_id=sid, reply=last_reply)

app.include_router(router)
