from langchain_ollama import OllamaLLM


class LLMService:
    def __init__(self, model: str = "gemma4:e4b"):
        self.model = model
        self.llm = OllamaLLM(
            model=model,
            temperature=0.2  # lower = more consistent output
        )

    def generate(self, prompt: str) -> str:
        """
        Generic LLM call
        """
        try:
            response = self.llm.invoke(prompt)
            return response.strip()
        except Exception as e:
            return f"LLM Error: {str(e)}"

    def generate_strict_json(self, prompt: str) -> str:
        """
        Use this when you need structured JSON output (like classifier)
        """
        strict_prompt = f"""
You must respond ONLY with valid JSON.
Do not include explanations.
Do not include markdown.

{prompt}
"""
        try:
            response = self.llm.invoke(strict_prompt)
            return response.strip()
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'


# Module-level singleton
# Import as: from app.services.llm import llm_service
# or as callable alias: from app.services.llm import llm
llm_service = LLMService()


def llm(prompt: str) -> str:
    """Callable alias for llm_service.generate() — used by skill modules."""
    return llm_service.generate(prompt)