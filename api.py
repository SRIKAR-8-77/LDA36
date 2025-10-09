from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import date
from contextlib import asynccontextmanager
from database import create_tables

from services import process_new_document, get_chat_reply, get_upcoming_events_for_user

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_id: str
    question: str
    history: List[ChatMessage]

class ChatResponse(BaseModel):
    response: str

class Event(BaseModel):
    date_id: int
    user_id: str
    file_name: str
    event_date: date
    event_description: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("Creating database tables...")
    create_tables()
    print("Tables created successfully.")
    yield

    print("Application shutting down...")

app = FastAPI(title="Document AI Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-document/")
async def upload_document(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        result = process_new_document(
            user_id=user_id,
            file_name=file.filename,
            file_content=file_content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    try:
        history_list = [msg.dict() for msg in request.history]
        response_text = get_chat_reply(
            user_id=request.user_id,
            question=request.question,
            history=history_list
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{user_id}", response_model=List[Event])
async def get_events(user_id: str):
    try:
        events = get_upcoming_events_for_user(user_id=user_id)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))