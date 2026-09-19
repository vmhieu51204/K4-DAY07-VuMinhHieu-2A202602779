from __future__ import annotations

from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base is currently empty. Please add documents before asking questions."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant information found in the knowledge base."

        context_blocks: list[str] = []
        for idx, item in enumerate(results, start=1):
            source = item.get("metadata", {}).get("source", item.get("id", f"doc-{idx}"))
            context_blocks.append(f"[{idx}] Source: {source}\n{item['content']}")

        context_str = "\n\n".join(context_blocks)
        prompt = (
            "You are a helpful and truthful assistant. Answer the question using ONLY the provided context. "
            "Cite the context sources using bracketed numbers like [1] or [2] when stating facts. "
            "If the answer cannot be determined from the context, state clearly that the information is unavailable.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        return self.llm_fn(prompt)
