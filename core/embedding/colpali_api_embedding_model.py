import io
import logging
from typing import List, Optional, Tuple, Union

import numpy as np
from httpx import AsyncClient, Timeout  # replacing httpx.AsyncClient for clarity

from core.config import get_settings
from core.embedding.base_embedding_model import BaseEmbeddingModel
from core.models.chunk import Chunk

logger = logging.getLogger(__name__)

# Define alias for a multivector: a list of embedding vectors
MultiVector = List[List[float]]


def partition_chunks(chunks: List[Chunk]) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    text_inputs: List[Tuple[int, str]] = []
    image_inputs: List[Tuple[int, str]] = []
    for idx, chunk in enumerate(chunks):
        if chunk.metadata.get("is_image"):
            content = chunk.content
            if content.startswith("data:"):
                content = content.split(",", 1)[1]
            image_inputs.append((idx, content))
        else:
            text_inputs.append((idx, chunk.content))
    return text_inputs, image_inputs


class ColpaliApiEmbeddingModel(BaseEmbeddingModel):
    def __init__(self):
        self.settings = get_settings()
        # Use Morphik Embedding API key from settings
        self.api_key = self.settings.MORPHIK_EMBEDDING_API_KEY
        if not self.api_key:
            raise ValueError("MORPHIK_EMBEDDING_API_KEY must be set in settings")
        # Use the configured Morphik Embedding API domain
        domain = self.settings.MORPHIK_EMBEDDING_API_DOMAIN
        self.endpoint = f"{domain.rstrip('/')}/embeddings"
        # Batching is handled at a higher layer (streaming embed+store).
        # Here we issue at most one request per input type per batch.

    async def embed_for_ingestion(self, chunks: Union[Chunk, List[Chunk]], document_id: Optional[str] = None, start_index: int = 0) -> List[MultiVector]:
        # Normalize to list
        if isinstance(chunks, Chunk):
            chunks = [chunks]
        if not chunks:
            return []

        # Initialize result list with empty multivectors
        results: List[MultiVector] = [[] for _ in chunks]
        text_inputs, image_inputs = partition_chunks(chunks)

        # Image embeddings
        if image_inputs:
            indices, inputs = zip(*image_inputs)
            # Calculate chunk_ids for this batch
            chunk_ids = [start_index + idx for idx in indices] if document_id else None
            data = await self.call_api(list(inputs), "image", document_id=document_id, chunk_ids=chunk_ids)
            for idx, emb in zip(indices, data):
                results[idx] = emb

        # Text embeddings
        if text_inputs:
            indices, inputs = zip(*text_inputs)
            # Calculate chunk_ids for this batch
            chunk_ids = [start_index + idx for idx in indices] if document_id else None
            data = await self.call_api(list(inputs), "text", document_id=document_id, chunk_ids=chunk_ids)
            for idx, emb in zip(indices, data):
                results[idx] = emb

        return results

    async def embed_for_query(self, text: str) -> MultiVector:
        # Delegate to common API call helper for a single text input
        data = await self.call_api([text], "text")
        if not data:
            raise RuntimeError("No embeddings returned from Morphik Embedding API")
        return data[0]

    async def call_api(self, inputs, input_type, document_id=None, chunk_ids=None) -> List[MultiVector]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"input_type": input_type, "inputs": inputs}
        
        # Add document_id and chunk_ids if provided
        if document_id:
            payload["document_id"] = document_id
        if chunk_ids is not None:
            payload["chunk_ids"] = chunk_ids
            
        timeout = Timeout(read=6000.0, connect=6000.0, write=6000.0, pool=6000.0)

        # DEBUG: Добавлено логирование
        logger.info(f"🚀 Calling Modal API: {self.endpoint}")
        logger.info(f"📤 Payload: input_type={input_type}, inputs_count={len(inputs)}, document_id={document_id}, chunk_ids={chunk_ids}")
        async with AsyncClient(timeout=timeout) as client:
            resp = await client.post(self.endpoint, json=payload, headers=headers)
            resp.raise_for_status()

        # DEBUG: Логирование ответа
        logger.info(f"📥 Response status: {resp.status_code}")
        logger.info(f"📥 Response size: {len(resp.content)} bytes")

            # Load .npz from response content
            npz_data = np.load(io.BytesIO(resp.content))

            # Extract metadata
            count = int(npz_data["count"])
            returned_input_type = str(npz_data["input_type"])

            logger.debug(f"Received {count} embeddings for input_type: {returned_input_type}")

            # Extract embeddings in order
            embeddings = []
            for i in range(count):
                embedding_array = npz_data[f"emb_{i}"]
                # Convert numpy array to list of lists (MultiVector format)
                embeddings.append(embedding_array.tolist())

            return embeddings
