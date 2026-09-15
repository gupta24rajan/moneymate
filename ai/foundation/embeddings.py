from ai.foundation.llm_client import LLMClient

class EmbeddingManager:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client

    async def get_embedding(self, text: str) -> list[float]:
        return await self.client.embed(text)

    async def get_batch_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            emb = await self.client.embed(text)
            embeddings.append(emb)
        return embeddings