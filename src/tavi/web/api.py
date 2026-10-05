from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from tavi.conversation.engine import ConversationEngine
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Tavi Chatbot")
engine = ConversationEngine()

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    text: str
    session_id: str = "default_session"

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received message: {request.text}")
    response_text = engine.process_message(request.text, request.session_id)
    return {"response": response_text}
