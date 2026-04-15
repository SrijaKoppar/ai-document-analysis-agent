from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
import os
import shutil
from app.services.extractor import extract_transactions_from_csv, extract_text_from_pdf
from app.services.analyzer import (
    calculate_total_income,
    calculate_total_expense,
    calculate_net_savings,
    categorize_transactions,
    find_highest_expense,
)
from app.services.llm_interface import answer_question
from app.services.vector_store import VectorStore

# Import your memory_manager instance here
from app.services.memorymanager import memory_manager  

router = APIRouter()

# Base upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory dict to hold vector store instances per session
vector_stores = {}

def get_vector_store(session_id: str) -> VectorStore:
    if session_id not in vector_stores:
        vector_stores[session_id] = VectorStore()
    return vector_stores[session_id]

# New endpoint to create a new session_id
@router.post("/start_session", tags=["Session"])
async def start_session():
    session_id = memory_manager.create_session()
    return {"session_id": session_id}

@router.post("/analyze", tags=["Bank Statements"])
async def analyze_bank_statement(
    file: UploadFile = File(...),
    session_id: str = Query(..., description="Unique session ID for user"),
):
    if not file.filename.endswith((".pdf", ".csv")):
        return JSONResponse(status_code=400, content={"error": "Invalid file type. Only PDF and CSV allowed."})

    # Save file per session to avoid collisions
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)
    save_path = os.path.join(session_folder, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.endswith(".csv"):
            transactions = extract_transactions_from_csv(save_path)
        else:
            # Extract raw text then parse transactions from text
            transactions = extract_text_from_pdf(save_path)
        if not transactions:
            return JSONResponse(status_code=400, content={"error": "No transactions found to analyze."})

        # Perform analysis
        total_income = calculate_total_income(transactions)
        total_expense = calculate_total_expense(transactions)
        net_savings = calculate_net_savings(transactions)
        expense_categories, income_categories = categorize_transactions(transactions)
        highest_expense = find_highest_expense(transactions)

        if total_income > 0 and not income_categories:
            income_categories = {"Uncategorized Income": total_income}

        # Prepare summary texts for vector store
        summary_texts = [
            f"Total Income: ₹{total_income}",
            f"Total Expense: ₹{total_expense}",
            f"Net Savings: ₹{net_savings}",
            f"Expense Categories: {expense_categories}",
            f"Income Categories: {income_categories}",
            f"Highest Expense: {highest_expense}",
        ]

        # Get or create vector store for this session
        vector_store = get_vector_store(session_id)
        vector_store.clear()
        vector_store.add_texts(summary_texts)
        vector_store.save()

        # Add analysis summary to memory_manager session as system message
        summary_text = (
            f"Summary: Total Income ₹{total_income}, Total Expense ₹{total_expense}, "
            f"Net Savings ₹{net_savings}, Expense Categories {expense_categories}, "
            f"Income Categories {income_categories}, Highest Expense {highest_expense}"
        )
        memory_manager.add_message(session_id, "system", summary_text)

        return {
            "filename": file.filename,
            "status": "Analysis successful!",
            "summary": {
                "income_summary": {
                    "total_income": total_income,
                    "income_categories": income_categories,
                },
                "expense_summary": {
                    "total_expense": total_expense,
                    "expense_categories": expense_categories,
                    "highest_expense": highest_expense,
                },
                "savings_summary": {
                    "net_savings": net_savings
                },
            },
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Analysis failed: {str(e)}"})

@router.post("/ask_llm", tags=["LLM Assistance"])
async def ask_llm(
    question: str,
    session_id: str = Query(..., description="Unique session ID for user"),
):
    try:
        # Get chat history from memory manager
        chat_history = memory_manager.get_history(session_id)

        # Add user question to memory
        memory_manager.add_message(session_id, "user", question)

        vector_store = get_vector_store(session_id)
        retrieved_chunks = vector_store.search(question, top_k=3)
        context = "\n".join([item["text"] for item in retrieved_chunks])

        prompt = f"""
        Contextual financial data:\n{context}\n
        User's question: {question}
        """

        response = answer_question(prompt,session_id)

        # Add LLM response to memory
        memory_manager.add_message(session_id, "assistant", response)

        return {"status": "success", "response": response}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error generating LLM response: {str(e)}"})

@router.post("/clear_memory", tags=["LLM Assistance"])
async def clear_memory(session_id: str = Query(..., description="Unique session ID for user")):
    try:
        # Clear memory manager session data
        memory_manager.clear_session(session_id)

        vector_store = get_vector_store(session_id)
        vector_store.clear()

        return {"status": "success", "message": "Memory cleared successfully."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to clear memory: {str(e)}"})

