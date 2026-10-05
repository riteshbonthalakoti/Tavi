from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Tavi Chatbot")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat_endpoint(message: dict):
    user_text = message.get("text", "")
    
    # TODO: Pass through NLP pipeline here
    # For now, echo a placeholder
    response_text = f"Tavi heard: {user_text}"
    
    return {"response": response_text}

if __name__ == "__main__":
    uvicorn.run("main_web:app", host="127.0.0.1", port=8000, reload=True)
