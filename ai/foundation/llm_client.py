from openai import AsyncOpenAI
from ai.config import config


class LLMClient:

    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.LLM_MODEL
        self.embedding_model = config.EMBEDDING_MODEL

    async def generate(self, prompt: str) -> str:
        """Prompt se response text generate karta hai"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content

    async def classify(self, text: str, categories: list[str]) -> str:
        """Input text ko given categories mein categorize karta hai"""
        prompt = (
            f"Classify the following text into one of these categories:"
            f" {', '.join(categories)}.\nText: {text}\nCategory:"
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()

    async def embed(self, text: str) -> list[float]:
        """Text ki vector embeddings return karta hai"""
        response = await self.client.embeddings.create(
            model=self.embedding_model, input=text
        )
        return response.data[0].embedding