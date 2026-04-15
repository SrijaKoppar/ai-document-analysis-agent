
from langchain_ollama import OllamaLLM
from app.services.vector_store import load_and_search  # 🔹 Import FAISS search
from app.services.memorymanager import memory_manager

# Initialize the LLM
llm = OllamaLLM(model="gemma4:e4b")

def answer_question(user_question: str, session_id: str) -> str:
    try:
        # Retrieve stored conversation history
        history = memory_manager.get_history(session_id)
        past_convo = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])

        # Retrieve relevant chunks from vector store
        retrieved_chunks = load_and_search(user_question, top_k=3)
        context = "\n\n".join(retrieved_chunks) if retrieved_chunks else ""

        prompt = f"""You are a helpful financial assistant.

Conversation History:
{past_convo}

Context from bank statement analysis:
{context}

User Question:
{user_question}

Answer concisely and helpfully:
"""

        response = llm(prompt)

        # Save current Q&A to memory
        memory_manager.add_message(session_id, "user", user_question)
        memory_manager.add_message(session_id, "assistant", response)

        return response.strip()

    except Exception as e:
        return f"LLM Error: {str(e)}"


