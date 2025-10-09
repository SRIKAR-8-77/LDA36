import os
import google.generativeai as genai
from dotenv import load_dotenv
import pinecone
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "lda-vec44"  

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    print("✅ Pinecone connection successful.")
except Exception as e:
    print(f"❌ Error connecting to Pinecone: {e}")
    index = None

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EMBEDDING_MODEL = 'models/text-embedding-004'

def chunk_text(text: str, chunk_size_words: int = 200, chunk_overlap_words: int = 30):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size_words - chunk_overlap_words):
        chunks.append(" ".join(words[i:i + chunk_size_words]))
    return chunks

def add_document_to_vector_db(user_id: str, file_name: str, raw_text: str):
    if not index:
        raise ConnectionError("Pinecone index is not initialized.")

    text_chunks = chunk_text(raw_text)
    if not text_chunks:
        return

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

    vectors_to_upsert = []
    for i, chunk in enumerate(text_chunks):
        vector_id = f"{user_id}_{file_name}_chunk_{i}"
        metadata = {
            "user_id": user_id,
            "file_name": file_name,
            "text": chunk
        }
        vectors_to_upsert.append((vector_id, embeddings[i], metadata))

    index.upsert(vectors=vectors_to_upsert)
    
    print(f"✅ Successfully added document '{file_name}' to the Pinecone vector store.")