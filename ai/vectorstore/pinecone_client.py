import logging
from typing import Any

from pinecone import Pinecone, ServerlessSpec

from ai.config import config

logger = logging.getLogger(__name__)


class PineconeClient:
    def __init__(self):
        self._client: Pinecone | None = None
        self._index = None

    def _get_client(self) -> Pinecone:
        if self._client is None:
            if not config.PINECONE_API_KEY:
                raise RuntimeError("PINECONE_API_KEY is missing.")
            self._client = Pinecone(api_key=config.PINECONE_API_KEY)
        return self._client

    def ensure_index(self) -> None:
        if not config.RAG_ENABLED:
            return
        if not config.PINECONE_API_KEY or not config.PINECONE_INDEX_NAME:
            raise RuntimeError("Pinecone config missing (PINECONE_API_KEY/PINECONE_INDEX_NAME)")
        client = self._get_client()
        try:
            if client.has_index(config.PINECONE_INDEX_NAME):
                return
            client.create_index(
                name=config.PINECONE_INDEX_NAME,
                dimension=config.PINECONE_DIMENSION,
                metric="cosine",
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
            )
            logger.info("Created Pinecone index %s (dim=%s)", config.PINECONE_INDEX_NAME, config.PINECONE_DIMENSION)
        except Exception:
            logger.exception("Failed to ensure Pinecone index exists")
            raise

    def get_index(self):
        if not config.RAG_ENABLED:
            raise RuntimeError("RAG is disabled")
        if not config.PINECONE_API_KEY:
            raise RuntimeError("PINECONE_API_KEY is missing.")
        if not config.PINECONE_INDEX_NAME:
            raise RuntimeError("PINECONE_INDEX_NAME is missing.")

        if self._index is None:
            client = self._get_client()
            self.ensure_index()
            self._index = client.Index(config.PINECONE_INDEX_NAME)
        return self._index

    def upsert_vectors(self, vectors: list[tuple[str, list[float], dict[str, Any]]]) -> None:
        if not config.RAG_ENABLED or not vectors:
            return
        idx = self.get_index()
        idx.upsert(vectors=vectors)

    def delete_vectors(self, ids: list[str]) -> None:
        if not config.RAG_ENABLED or not ids:
            return
        idx = self.get_index()
        idx.delete(ids=ids)


pinecone_client = PineconeClient()
