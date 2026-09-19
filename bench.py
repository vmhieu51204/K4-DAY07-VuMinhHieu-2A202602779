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
        "query": "Mức học phí niêm yết hàng năm của chương trình Bác sĩ Y khoa và Cử nhân Điều dưỡng tại VinUni là bao nhiêu?",
        "filter": None,
        "target_docs": ["undergraduate-tuition-fees-tariff", "tuition-scholarship-financial-aid-faq", "financial-regulations-tariff-student"],
        "gold_answer": "Cử nhân Điều dưỡng là 349,650,000 VND/năm; Bác sĩ Y khoa là 815,850,000 VND/năm (chưa trừ 35% hỗ trợ từ Founder).",
    },
    {
        "id": 2,
        "query": "Thời hạn mượn sách in tối đa là bao nhiêu ngày và được mượn bao nhiêu cuốn sách?",
        "filter": {"audience": "student"},
        "target_docs": ["library-services-student"],
        "gold_answer": "Sinh viên được mượn tối đa 05 cuốn sách in trong thời hạn 14 ngày (được gia hạn tối đa 02 lần). Cần filter audience=student để không lấy nhầm quy định giảng viên là 30 cuốn/180 ngày.",
    },
    {
        "id": 3,
        "query": "Sinh viên thanh toán học phí VinUni bằng những phương thức nào và nộp mấy lần trong năm?",
        "filter": None,
        "target_docs": ["tuition-scholarship-financial-aid-faq", "financial-regulations-tariff-student"],
        "gold_answer": "Nộp 2 lần/năm vào đầu mỗi học kỳ chính (kỳ Thu và kỳ Xuân). Có các phương thức: nộp trực tuyến qua cổng my.vinuni.edu.vn, nộp trực tiếp thẻ tại Phòng Kế toán hoặc chuyển khoản ngân hàng Techcombank.",
    },
    {
        "id": 4,
        "query": "Mức học phí của chương trình đào tạo kỹ sư chuyên sâu Trí tuệ nhân tạo tạo sinh GenAI tại ĐHBKHN được tính như thế nào?",
        "filter": None,
        "target_docs": ["hoc-phi-hust"],
        "gold_answer": "Chương trình kỹ sư chuyên sâu GenAI có mức học phí bằng mức học phí chương trình Khoa học dữ liệu và trí tuệ nhân tạo (IT-E10), tính theo số tín chỉ học phí của các học phần đăng ký.",
    },
    {
        "id": 5,
        "query": "Khi đăng ký học phần sinh viên cần lưu ý điều kiện gì và xử lý thế nào khi gặp lỗi trùng lịch?",
        "filter": {"audience": "student"},
        "target_docs": ["course-registration"],
        "gold_answer": "Cần kiểm tra điều kiện học phần tiên quyết trước khi xác nhận; khi trùng lịch phải điều chỉnh trước thời hạn công bố, yêu cầu ngoại lệ gửi qua kênh hỗ trợ học vụ chính thức.",
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
