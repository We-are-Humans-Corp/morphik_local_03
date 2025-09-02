import logging
from typing import List, Tuple, Union

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
        # Use the configured Morphik Embedding API domain
        domain = self.settings.MORPHIK_EMBEDDING_API_DOMAIN
        
        # Choose appropriate API key based on endpoint
        if "huggingface" in domain:
            # Use HF_TOKEN for HuggingFace endpoints
            import os
            self.api_key = os.getenv("HF_TOKEN") or self.settings.MORPHIK_EMBEDDING_API_KEY
        elif "modal.run" in domain:
            # Modal doesn't require API key for public endpoints
            self.api_key = "not-required-for-modal"
        else:
            # Use Morphik Embedding API key from settings
            self.api_key = self.settings.MORPHIK_EMBEDDING_API_KEY
        
        if not self.api_key and "modal.run" not in domain:
            raise ValueError("API key must be set (HF_TOKEN for HuggingFace or MORPHIK_EMBEDDING_API_KEY)")
        # For RunPod endpoints, use /runsync instead of /embeddings
        if "runpod.ai" in domain:
            self.endpoint = f"{domain.rstrip('/')}/runsync"
        elif "huggingface" in domain:
            # HuggingFace endpoints don't need additional path
            self.endpoint = domain.rstrip('/')
        else:
            self.endpoint = f"{domain.rstrip('/')}/embeddings"

    async def embed_for_ingestion(self, chunks: Union[Chunk, List[Chunk]]) -> List[MultiVector]:
        # Normalize to list
        if isinstance(chunks, Chunk):
            chunks = [chunks]
        if not chunks:
            return []

        # Initialize result list with empty multivectors
        results: List[MultiVector] = [[] for _ in chunks]
        text_inputs, image_inputs = partition_chunks(chunks)

        # Batch image embeddings if needed
        if image_inputs:
            indices, inputs = zip(*image_inputs)
            data = await self.call_api(inputs, "image")
            for idx, emb in zip(indices, data):
                results[idx] = emb

        # Batch text embeddings if needed
        if text_inputs:
            indices, inputs = zip(*text_inputs)
            data = await self.call_api(inputs, "text")
            for idx, emb in zip(indices, data):
                results[idx] = emb

        return results

    async def embed_for_query(self, text: str) -> MultiVector:
        # Delegate to common API call helper for a single text input
        data = await self.call_api([text], "text")
        if not data:
            raise RuntimeError("No embeddings returned from Morphik Embedding API")
        return data[0]

    async def call_api(self, inputs, input_type) -> List[MultiVector]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # Для RunPod endpoints, используем их формат с contents/content_types
        if "runpod.ai" in self.endpoint:
            # Преобразуем input_type в список content_types для каждого элемента
            content_types = [input_type] * len(inputs)
            payload = {
                "input": {
                    "contents": inputs,
                    "content_types": content_types,
                    "batch_size": 8  # Оптимальный размер для RTX 4090
                }
            }
        elif "huggingface" in self.endpoint:
            # HuggingFace Inference Endpoints format
            payload = {
                "inputs": {
                    "contents": inputs,
                    "content_types": [input_type] * len(inputs),
                    "batch_size": 8
                }
            }
        else:
            payload = {"input_type": input_type, "inputs": inputs}
        
        timeout = Timeout(read=6000.0, connect=6000.0, write=6000.0, pool=6000.0)
        async with AsyncClient(timeout=timeout) as client:
            resp = await client.post(self.endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            
            # Modal returns npz file, not JSON
            if "modal.run" in self.endpoint:
                import numpy as np
                import io
                npz_data = np.load(io.BytesIO(resp.content))
                count = npz_data['count']
                embeddings = []
                for i in range(count):
                    emb = npz_data[f'emb_{i}'].tolist()
                    embeddings.append(emb)
                return embeddings
            else:
                data = resp.json()
        
        # RunPod возвращает результат в поле "output", другие API в "embeddings"
        if "runpod.ai" in self.endpoint:
            # RunPod может вернуть статус IN_QUEUE для холодного старта
            if data.get("status") == "IN_QUEUE":
                logger.warning("RunPod endpoint is starting up (cold start), embeddings may be empty")
                return []
            # RunPod возвращает embeddings прямо в output
            return data.get("output", {}).get("embeddings", data.get("output", []))
        elif "huggingface" in self.endpoint:
            # HuggingFace возвращает embeddings прямо в корне ответа
            return data.get("embeddings", data)
        else:
            return data.get("embeddings", [])
