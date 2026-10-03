from ai.foundation.llm_client import LLMClient

class EmbeddingManager:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client

    async def get_embedding(self, text: str) -> list[float]:
        from ai.config import config

        return await self.client.embed(text, output_dimensionality=config.PINECONE_DIMENSION)

    async def get_batch_embeddings(self, texts: list[str]) -> list[list[float]]:
        from ai.config import config

        embeddings = []
        for text in texts:
            emb = await self.client.embed(text, output_dimensionality=config.PINECONE_DIMENSION)
            embeddings.append(emb)
        return embeddings