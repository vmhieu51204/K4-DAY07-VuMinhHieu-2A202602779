#!/usr/bin/env python3
"""
Benchmark script for Lab 07: Data Foundations (Embedding & Vector Store).

Executes 5 standardized benchmark queries on data/university corpus
using student's chunking and retrieval pipeline, and records results
to ket_qua_benchmark.txt.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import GeminiEmbedder, MockEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore

CORPUS_DIR = Path("data/university")
OUTPUT_FILE = Path("ket_qua_benchmark.txt")

BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Trường Đại học Công Nghệ gia hạn nộp học phí học kỳ II năm học 2025-2026 đến khi nào?",
        "filter": None,
        "target_docs": ["gia-han-thoi-gian-nop-hoc-phi-trong-hkii-nam-hoc-2025-2026"],
        "gold_answer": "26/05/2026",
    },
    {
        "id": 2,
        "query": "Hướng dẫn đóng học phí học kỳ II năm 2025-2026 qua hệ thống ERP của sinh viên USTH",
        "filter": None,
        "target_docs": ["tb-ve-viec-thu-hoc-phi-hoc-ky-ii-nam-hoc-2025-2026-chuong-trinh-dao-tao-trinh-do-dai-hoc-29249"],
        "gold_answer": "Đăng nhập hệ thống ERP: https://erp.usth.edu.vn/students -> Chọn mục Học phí, tra cứu hóa đơn -> Kiểm tra mức học phí phải nộp -> Quét mã QR để hoàn tất thanh toán -> Thanh toán được xác nhận khi trạng thái hóa đơn chuyển sang “Đã đóng”.",
    },
    {
        "id": 3,
        "query": "Đối với các khoá 2021 trở về trước thì học bằng kép ở Trường Đại học Công Nghệ năm học 2024-2025 hết bao nhiêu tiền 1 tín chỉ?",
        "filter": None,
        "target_docs": ["dinh-muc-hoc-phi-dao-tao-dai-hoc-nam-hoc-2024-2025"],
        "gold_answer": "450.000 đồng/tín chỉ",
    },
    {
        "id": 4,
        "query": "Chương trình định hướng ứng dụng POHE của NEU năm học 2025-2026 có học phí bao nhiêu?",
        "filter": None,
        "target_docs": ["neu-tuition-fees-2025-2026", "neu-tuition-decision-985-2026-2027"],
        "gold_answer": "Khoảng 45 — 55 triệu đồng/năm",
    },
    {
        "id": 5,
        "query": "Theo lộ trình được duyệt thì mức thu học phí đối với sinh viên quốc tế là bao nhiêu?",
        "filter": {"audience": "staff"},
        "target_docs": ["bao-cao-lo-trinh-thu-hoc-phi-cac-he-nam-hoc-2026-2027-19718"],
        "gold_answer": "45.000.000đ/năm học/SV",
    },
]


def load_corpus() -> list[Document]:
    """Load and chunk documents from data/university."""
    chunker = RecursiveChunker(chunk_size=700)
    docs: list[Document] = []

    for p in sorted(CORPUS_DIR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            raw_fm = dict(re.findall(r"^(\w+):\s*(.+)$", fm_text, re.M))
            fm = {k: v.split("#")[0].strip().strip("\"'") for k, v in raw_fm.items()}
        else:
            body = text.strip()
            fm = {}

        fm["doc_id"] = p.stem
        fm["source"] = p.name

        chunks = chunker.chunk(body)
        for idx, chunk in enumerate(chunks):
            doc_meta = {**fm, "chunk_id": f"{p.stem}#{idx}"}
            docs.append(Document(id=f"{p.stem}#{idx}", content=chunk, metadata=doc_meta))

    return docs


def run_benchmark() -> str:
    print(f"Loading corpus from {CORPUS_DIR}...")
    docs = load_corpus()
    print(f"Created {len(docs)} chunks from {len(list(CORPUS_DIR.glob('*.md')))} documents.")

    # Select embedding backend
    provider = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key and provider != "mock":
        try:
            print("Using GeminiEmbedder (provider=gemini)...")
            embedder = GeminiEmbedder()
        except Exception as e:
            print(f"GeminiEmbedder initialization failed ({e}), falling back to MockEmbedder.")
            embedder = _mock_embed
    else:
        print(f"Using MockEmbedder (provider={provider})...")
        embedder = _mock_embed

    store = EmbeddingStore(collection_name="university_benchmark", embedding_fn=embedder)
    store.add_documents(docs)

    def simple_llm(prompt: str) -> str:
        ctx = prompt.split("Context:\n")[1].split("\n\nQuestion:")[0].replace("\n", " ").strip()
        return f"[Agent Response based on {ctx[:120]}...]"

    agent = KnowledgeBaseAgent(store=store, llm_fn=simple_llm)

    output_lines: list[str] = [
        "============================================================",
        "KẾT QUẢ ĐÁNH GIÁ BENCHMARK TRUY XUẤT (LAB 07)",
        f"Corpus: {CORPUS_DIR} ({len(list(CORPUS_DIR.glob('*.md')))} files, {len(docs)} chunks)",
        f"Backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}",
        "============================================================\n",
    ]

    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        query = item["query"]
        mf = item["filter"]
        gold = item["gold_answer"]
        targets = item["target_docs"]

        output_lines.append(f"--- Câu hỏi {qid} ---")
        output_lines.append(f"Query: {query}")
        output_lines.append(f"Metadata filter: {mf}")
        output_lines.append(f"Tài liệu mục tiêu: {', '.join(targets)}")
        output_lines.append(f"Gold answer: {gold}")

        results = store.search_with_filter(query, top_k=3, metadata_filter=mf)
        top1_relevant = False

        output_lines.append("\nTop-3 Chunks retrieved:")
        for rank, res in enumerate(results, start=1):
            cid = res["id"]
            doc_id = res["metadata"].get("doc_id", "")
            aud = res["metadata"].get("audience", "")
            score = res["score"]
            snippet = res["content"][:140].replace("\n", " ")
            is_match = (doc_id in targets)
            if rank == 1 and is_match:
                top1_relevant = True
            output_lines.append(f"  [{rank}] {cid} (doc_id={doc_id}, aud={aud}, score={score:.4f}) [{'HIT' if is_match else 'MISS'}]")
            output_lines.append(f"      {snippet}...")

        output_lines.append(f"Đánh giá Top-1 Relevant: {'ĐÚNG' if top1_relevant else 'CHƯA ĐẠT'}")
        output_lines.append("-" * 60 + "\n")

    result_text = "\n".join(output_lines)
    print(result_text)

    OUTPUT_FILE.write_text(result_text, encoding="utf-8")
    print(f"Results saved to {OUTPUT_FILE}")
    return result_text


if __name__ == "__main__":
    run_benchmark()
