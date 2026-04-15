from typing import List, Dict
from app.services.vector_store import load_and_search
from app.services.llm_interface import answer_question  

class RAGChatChain:
    def __init__(self, max_history: int = 5):
        self.chat_history: List[Dict[str, str]] = []  # List of {"user": ..., "bot": ...}
        self.max_history = max_history

    def build_prompt(self, question: str, context_chunks: List[Dict[str, str]]) -> str:
        history_text = ""
        for turn in self.chat_history[-self.max_history:]:
            history_text += f"User: {turn['user']}\nBot: {turn['bot']}\n"

        context_text = "\n\n".join(chunk['text'] for chunk in context_chunks)

        prompt = (
            f"You are a helpful financial assistant chatbot. Use the following context and conversation history to answer the user's question.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Conversation history:\n{history_text}\n"
            f"User: {question}\nBot:"
        )
        return prompt

    def ask(self, question: str) -> str:
        context_chunks = load_and_search(question, top_k=5)
        prompt = self.build_prompt(question, context_chunks)
        answer = answer_question(prompt)

        self.chat_history.append({"user": question, "bot": answer})

        return answer

    def clear_history(self):
        self.chat_history = []
