import os
import google.generativeai as genai
import chromadb
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EMBEDDING_MODEL = 'models/text-embedding-004'
GENERATION_MODEL = 'gemini-2.5-pro'

chroma_client = chromadb.PersistentClient(path="./db")
collection = chroma_client.get_collection(name="user_documents")

def get_chatbot_response(user_id: str, user_question: str, chat_history: list) -> str:

    if chat_history:
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
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

    # 2. Securely Retrieve Documents
    question_embedding = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=standalone_question,
        task_type="RETRIEVAL_QUERY"
    )['embedding']
    
    # Search ChromaDB with the user_id filter
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3,
        where={"user_id": user_id}
    )
    
    retrieved_documents = "\n\n".join(results['documents'][0])

    final_prompt = f"""
    You are a helpful assistant. Answer the user's question based on the provided document snippets and the chat history.
    Chat History:
    {chat_history}
    Retrieved Document Snippets:
    ---
    {retrieved_documents}
    ---
    User Question: {user_question}
    """
    
    model = genai.GenerativeModel(GENERATION_MODEL)
    final_response = model.generate_content(final_prompt)
    
    return final_response.text