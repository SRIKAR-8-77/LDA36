import os
import google.generativeai as genai
from dotenv import load_dotenv
from pinecone import Pinecone
from vector_store import index

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EMBEDDING_MODEL = 'models/text-embedding-004'
GENERATION_MODEL = 'gemini-2.5-pro'

def get_chatbot_response(user_id: str, user_question: str, chat_history: list) -> str:
    if not index:
        raise ConnectionError("Pinecone index is not initialized.")

    CONTEXT_WINDOW_SIZE = 16 
    recent_history = chat_history[-CONTEXT_WINDOW_SIZE:] 
    history_str = "" 

    if recent_history:
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])
        rephrase_prompt = f"""
        Chat History:{history_str}
        Human Question: {user_question}
        Rephrased Standalone Question:
        """
        model = genai.GenerativeModel(GENERATION_MODEL)
        rephrase_response = model.generate_content(rephrase_prompt)
        standalone_question = rephrase_response.text.strip()
    else:
        standalone_question = user_question

    print(f"Rephrased Question: {standalone_question}")

    question_embedding = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=standalone_question,
        task_type="RETRIEVAL_QUERY"
    )['embedding']

    query_results = index.query(
        vector=question_embedding,
        top_k=3,
        include_metadata=True,
        filter={"user_id": {"$eq": user_id}}
    )
    
    retrieved_documents = "\n\n".join([match['metadata']['text'] for match in query_results['matches']])
    
    final_prompt = f"""
    You are a helpful assistant. Answer the user's question based on the provided document snippets and the chat history.
    Chat History:
    {history_str} 
    Retrieved Document Snippets:
    ---
    {retrieved_documents}
    ---
    User Question: {user_question}
    """
    
    model = genai.GenerativeModel(GENERATION_MODEL)
    final_response = model.generate_content(final_prompt)
    
    return final_response.text