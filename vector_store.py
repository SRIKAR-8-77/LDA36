# vector_store.py

import os
import google.generativeai as genai
import chromadb
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EMBEDDING_MODEL = 'models/text-embedding-004' 

chroma_client = chromadb.PersistentClient(path="./db")
collection = chroma_client.get_or_create_collection(name="user_documents")

def chunk_text(text: str, chunk_size_words: int = 200, chunk_overlap_words: int = 30):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size_words - chunk_overlap_words):
        chunks.append(" ".join(words[i:i + chunk_size_words]))
    return chunks

def add_document_to_vector_db(user_id: str, file_name: str, raw_text: str):
    text_chunks = chunk_text(raw_text)
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text_chunks,
            task_type="RETRIEVAL_DOCUMENT"
        )
        embeddings = result['embedding']
    except Exception as e:
        print(f"❌ Error creating Google embeddings: {e}")
        return

    ids = [f"{user_id}_{file_name}_chunk_{i}" for i in range(len(text_chunks))]
    metadatas = [
        {"user_id": user_id, "file_name": file_name} for _ in range(len(text_chunks))
    ]

    collection.add(
        embeddings=embeddings,
        documents=text_chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Successfully added document '{file_name}' to the vector store.")