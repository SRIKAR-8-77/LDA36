import os
from datetime import date
from teserract import ocr_from_pdf
from gemini_analyzer import analyze_document_with_gemini
from vector_store import add_document_to_vector_db
from chatbot import get_chatbot_response
from database import SessionLocal, ImportantDate

def process_new_document(user_id: str, file_name: str, file_content: bytes):
    temp_file_path = f"./temp_{file_name}"
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)

        extracted_text = ocr_from_pdf(temp_file_path)
        if not extracted_text:
            raise ValueError("OCR extraction failed or document is empty.")

        structured_data = analyze_document_with_gemini(extracted_text)
        if "error" in structured_data:
            raise ValueError(f"Gemini analysis failed: {structured_data['error']}")
        
        add_document_to_vector_db(
            user_id=user_id,
            file_name=file_name,
            raw_text=extracted_text
        )

        db = SessionLocal()
        try:
            for event in structured_data.get("important_dates", []):
                new_date = ImportantDate(
                    user_id=user_id,
                    file_name=file_name,
                    event_date=date.fromisoformat(event['date']),
                    event_description=event['event']
                )
                db.add(new_date)
            db.commit()
        finally:
            db.close()

        return {
            "user_id": user_id,
            "file_name": file_name,
            "extracted_text": extracted_text,
            "structured_data": structured_data
        }

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def get_chat_reply(user_id: str, question: str, history: list):
    response_text = get_chatbot_response(
        user_id=user_id,
        user_question=question,
        chat_history=history
    )
    return response_text

def get_upcoming_events_for_user(user_id: str):
    db = SessionLocal()
    try:
        events = db.query(ImportantDate).filter(
            ImportantDate.user_id == user_id,
            ImportantDate.event_date >= date.today()
        ).order_by(ImportantDate.event_date.asc()).all()

        return [
            {
                "date_id": event.date_id,
                "user_id": event.user_id,
                "file_name": event.file_name,
                "event_date": event.event_date.isoformat(),
                "event_description": event.event_description
            } for event in events
        ]
    finally:
        db.close()
