import csv
import re
import sys
import urllib.request
from bs4 import BeautifulSoup
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DOCS_META = [
    {
        "doc_id": "dieu-chinh-hoc-phi-sau-dai-hoc-giam-5",
        "url": "https://uet.vnu.edu.vn/dieu-chinh-hoc-phi-sau-dai-hoc-giam-5/",
        "title": "Điều chỉnh học phí sau đại học, giảm 5% - Trường Đại học Công Nghệ - Đại học Quốc Gia Hà Nội",
        "audience": "student",
        "department": "sau-dai-hoc",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "bao-cao-lo-trinh-thu-hoc-phi-cac-he-nam-hoc-2026-2027-19718",
        "url": "https://ussh.vnu.edu.vn/vi/gioi-thieu/ba-cong-khai/bao-cao-lo-trinh-thu-hoc-phi-cac-he-nam-hoc-2026-2027-19718.html",
        "title": "Báo cáo lộ trình thu học phí các hệ năm học 2026 - 2027",
        "audience": "staff",
        "department": "ke-hoach-tai-chinh",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "dinh-muc-hoc-phi-dao-tao-dai-hoc-nam-hoc-2024-2025",
        "url": "https://uet.edu.vn/dinh-muc-hoc-phi-dao-tao-dai-hoc-nam-hoc-2024-2025/",
        "title": "dinh-muc-hoc-phi-dao-tao-dai-hoc-nam-hoc-2024-2025",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "gia-han-thoi-gian-nop-hoc-phi-trong-hkii-nam-hoc-2025-2026",
        "url": "https://uet.edu.vn/gia-han-thoi-gian-nop-hoc-phi-trong-hkii-nam-hoc-2025-2026/",
        "title": "gia-han-thoi-gian-nop-hoc-phi-trong-hkii-nam-hoc-2025-2026",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "hoan-tra-hoc-phi-cho-sinh-vien-thuoc-chuong-trinh-chat-luong-cao-theo-thong-tu-23-2014-tt-bgddt-tot-nghiep-dot-xet-thang-03-nam-2026",
        "url": "https://uet.edu.vn/hoan-tra-hoc-phi-cho-sinh-vien-thuoc-chuong-trinh-chat-luong-cao-theo-thong-tu-23-2014-tt-bgddt-tot-nghiep-dot-xet-thang-03-nam-2026/",
        "title": "hoan-tra-hoc-phi-cho-sinh-vien-thuoc-chuong-trinh-chat-luong-cao-theo-thong-tu-23-2014-tt-bgddt-tot-nghiep-dot-xet-thang-03-nam-2026",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "neu-tuition-decision-985-2026-2027",
        "url": "https://fit.neu.edu.vn/post/hoc-phi-neu-nam-hoc-2026-2027-theo-quyet-dinh-985",
        "title": "neu-tuition-decision-985-2026-2027",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "neu-tuition-fees-2025-2026",
        "url": "https://fit.neu.edu.vn/post/neu-tuition-fees-2025-2026",
        "title": "neu-tuition-fees-2025-2026",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "tb-ve-viec-thu-hoc-phi-hoc-ky-ii-nam-hoc-2025-2026-chuong-trinh-dao-tao-trinh-do-dai-hoc-29249",
        "url": "https://usth.edu.vn/tb-ve-viec-thu-hoc-phi-hoc-ky-ii-nam-hoc-2025-2026-chuong-trinh-dao-tao-trinh-do-dai-hoc-29249/",
        "title": "tb-ve-viec-thu-hoc-phi-hoc-ky-ii-nam-hoc-2025-2026-chuong-trinh-dao-tao-trinh-do-dai-hoc-29249",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-19",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
    {
        "doc_id": "thong-bao-quy-dinh-muc-hoc-phi-chinh-thuc-ap-dung-cho-nam-hoc-2026-2027-33107",
        "url": "https://usth.edu.vn/thong-bao-quy-dinh-muc-hoc-phi-chinh-thuc-ap-dung-cho-nam-hoc-2026-2027-33107/",
        "title": "thong-bao-quy-dinh-muc-hoc-phi-chinh-thuc-ap-dung-cho-nam-hoc-2026-2027-33107",
        "audience": "student",
        "department": "dao-tao",
        "category": "tuition-fees",
        "language": "vi",
        "retrieved_at": "2026-09-20",
        "document_version": "not-stated",
        "license_or_permission": "public-source",
    },
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
out_dir = Path("data/university")
out_dir.mkdir(parents=True, exist_ok=True)

# Write urls.csv
urls_csv = Path("data/urls.csv")
with urls_csv.open("w", encoding="utf-8", newline="") as f:
    fields = ["url", "doc_id", "title", "audience", "department", "category", "language", "document_version", "license_or_permission"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for doc in DOCS_META:
        writer.writerow({k: doc.get(k, "") for k in fields})
print(f"Wrote {urls_csv}")

# Write sources.csv
manifest_records = []
for doc in DOCS_META:
    doc_id = doc["doc_id"]
    url = doc["url"]
    print(f"Fetching {doc_id} from {url}...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"]):
        tag.decompose()
        
    content = ""
    for sel in [".entry-content", ".panel-body", ".col-lg-9", ".bodytext", "article", "main"]:
        el = soup.select_one(sel)
        if el:
            txt = el.get_text(separator="\n", strip=True)
            if len(txt) > len(content):
                content = txt
    
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    body_text = "\n\n".join(lines)
    
    # Build markdown document with YAML front matter
    fm_lines = [
        "---",
        f"doc_id: \"{doc_id}\"",
        f"title: \"{doc['title']}\"",
        f"source_url: \"{doc['url']}\"",
        f"retrieved_at: \"{doc['retrieved_at']}\"",
        f"document_version: \"{doc['document_version']}\"",
        f"audience: \"{doc['audience']}\"",
        f"department: \"{doc['department']}\"",
        f"category: \"{doc['category']}\"",
        f"language: \"{doc['language']}\"",
        f"license_or_permission: \"{doc['license_or_permission']}\"",
        "---",
        "",
        f"# {doc['title']}",
        "",
        body_text
    ]
    md_content = "\n".join(fm_lines) + "\n"
    file_path = out_dir / f"{doc_id}.md"
    file_path.write_text(md_content, encoding="utf-8")
    print(f"Saved {file_path} ({len(body_text)} chars)")
    
    manifest_records.append({
        "doc_id": doc_id,
        "file_path": str(file_path),
        "title": doc["title"],
        "source_url": doc["url"],
        "retrieved_at": doc["retrieved_at"],
        "document_version": doc["document_version"],
        "license_or_permission": doc["license_or_permission"],
    })

manifest_path = out_dir / "sources.csv"
with manifest_path.open("w", encoding="utf-8", newline="") as f:
    fields = ["doc_id", "file_path", "title", "source_url", "retrieved_at", "document_version", "license_or_permission"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(manifest_records)
print(f"Wrote {manifest_path}")
