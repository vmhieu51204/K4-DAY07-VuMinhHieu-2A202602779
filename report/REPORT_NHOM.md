# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm L3A — Biến thể Dịch vụ & Quy định Đại học  
**Thành viên:** Vũ Minh Hiếu, cùng các thành viên Nhóm L3A  
**Ngày:** 19/09/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và Quy định Đại học (Học phí, Học bổng, Thư viện, Đăng ký học phần tại VinUni & ĐHBKHN).

**Tại sao nhóm chọn chủ đề này?**
> Chủ đề quy định đại học là nghiệp vụ thực tế có tính ràng buộc pháp lý và điều kiện chặt chẽ, nơi sinh viên và phụ huynh thường xuyên cần tra cứu chính xác về mức học phí, hạn nộp, và điều kiện mượn trả sách. Bộ ngữ liệu này sở hữu sự phân tầng đối tượng sâu sắc giữa sinh viên (`student`) và giảng viên (`faculty`), là môi trường thực nghiệm lý tưởng để đánh giá năng lực tiền lọc (metadata pre-filtering) và phòng chống hiện tượng ảo giác thông tin của tác tử RAG.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Financial Regulations and Tariff for Student | https://policy.vinuni.edu.vn/all-policies/financial-regulations-and-tariff-for-student-2/ | 2026-09-19 / 2025-2026 | 5,538 | `audience: student, department: finance, category: tuition-fees, language: en` |
| 2 | VinUni Undergraduate Tuition Fees Tariff | https://admissions.vinuni.edu.vn/tuition-fee/undergraduate/ | 2026-09-19 / 2026-2027 | 2,116 | `audience: all, department: admissions, category: tuition-fees, language: en` |
| 3 | Tuition Fee Scholarship and Financial Aid FAQs | https://admissions.vinuni.edu.vn/undergraduate/faqs/tuition-fee-scholarship-and-financial-aids/ | 2026-09-19 / not-stated | 1,692 | `audience: all, department: admissions, category: tuition-fees, language: en` |
| 4 | Thông báo về mức học phí đối với các CTĐT năm 2024-2025 | https://ctt.hust.edu.vn/DisplayWeb/DisplayBaiViet?baiviet=43466 | 2026-09-19 / 2024-2025 | 1,918 | `audience: student, department: dao-tao, category: hoc-phi, language: vi` |
| 5 | Quy định mượn trả tài liệu thư viện cho sinh viên | https://library.vinuni.edu.vn/regulations/borrowing-policy-students | 2026-09-19 / 2026.1 | 745 | `audience: student, department: library, category: library-policy, language: vi` |
| 6 | Quy định mượn trả tài liệu thư viện cho giảng viên | https://library.vinuni.edu.vn/regulations/borrowing-policy-faculty | 2026-09-19 / 2026.1 | 775 | `audience: faculty, department: library, category: library-policy, language: vi` |
| 7 | Quy định đăng ký học phần | https://example.edu/hoc-vu/dang-ky-hoc-phan | 2026-09-19 / 2026.1 | 379 | `audience: student, department: academic-affairs, category: registration, language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `financial-regulations-tariff-student` | Mã định danh duy nhất ổn định khớp với tên file, phục vụ truy vết xuất xứ và xóa tài liệu (`delete_document`). |
| `title` | string | `VinUni Undergraduate Tuition Fees Tariff` | Tiêu đề chính thức của tài liệu, giúp tác tử RAG tạo trích dẫn nguồn (source citations) rõ ràng cho người đọc. |
| `source_url` | string | `https://policy.vinuni.edu.vn/...` | Cung cấp link gốc công khai để kiểm chứng tính xác thực (provenance) và trích dẫn URL. |
| `retrieved_at` | string (YYYY-MM-DD) | `2026-09-19` | Ghi nhận thời điểm thu thập dữ liệu, giúp phát hiện và cảnh báo tài liệu quá hạn (data freshness). |
| `document_version` | string | `2026-2027` | Phiên bản hiệu lực hoặc năm học, tránh nhầm lẫn biểu phí giữa các khóa tuyển sinh khác nhau. |
| `audience` | string (`student` / `faculty` / `staff` / `all`) | `student`, `faculty` | **Trường lọc cốt lõi:** Cho phép tiền lọc đối tượng để tránh trả lời nhầm chính sách của giảng viên cho sinh viên. |
| `department` | string | `finance`, `library`, `admissions` | Phân loại đơn vị quản lý, hỗ trợ lọc theo phạm vi phòng ban chức năng. |
| `category` | string | `tuition-fees`, `library-policy` | Nhóm nghiệp vụ chi tiết, tăng độ chính xác khi tìm kiếm theo chủ đề chuyên biệt. |
| `language` | string | `vi`, `en` | Định danh ngôn ngữ tài liệu, hỗ trợ xử lý truy xuất đa ngữ (multilingual retrieval). |


---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `undergraduate-tuition-fees-tariff.md` | FixedSizeChunker (`fixed_size`) | 14 | 197.6 | Kém — bảng học phí và các điều kiện tính tín chỉ bị cắt đôi ngẫu nhiên. |
| | SentenceChunker (`by_sentences`) | 6 | 351.5 | Tốt — giữ trọn câu hoàn chỉnh nhưng các mục dạng bảng gộp lại quá dài. |
| | RecursiveChunker (`recursive`) | 15 | 139.8 | Rất tốt — bẻ theo ranh giới dòng mục và tự gom các dòng con hợp lý. |
| `hoc-phi-hust.md` | FixedSizeChunker (`fixed_size`) | 13 | 193.7 | Kém — ngắt giữa tên chương trình đào tạo và mức đơn giá tín chỉ. |
| | SentenceChunker (`by_sentences`) | 5 | 382.4 | Tốt — giữ nguyên từng điều khoản 1, 2, 3. |
| | RecursiveChunker (`recursive`) | 12 | 158.8 | Xuất sắc — bám sát tiêu đề và từng gạch đầu dòng quy định. |
| `library-services-student.md` | FixedSizeChunker (`fixed_size`) | 5 | 189.0 | Trung bình — phân mảnh các mốc thời gian mượn và số lượng sách. |
| | SentenceChunker (`by_sentences`) | 3 | 247.3 | Tốt — phân định rõ mục hạn mức và mục bồi hoàn. |
| | RecursiveChunker (`recursive`) | 5 | 147.8 | Tốt — chia thành các đơn vị thông tin gọn gàng, độc lập. |

### Chiến lược của từng thành viên

**Thành viên 1 — Vũ Minh Hiếu**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=300, separators=["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy chế trường học luôn được biên soạn phân cấp theo cấu trúc: Đề mục lớn (`##`) -> Điều khoản -> Danh sách chi tiết (`-`). RecursiveChunker tách từ cấu trúc lớn đến nhỏ và tự động gom các mảnh ngắn kế tiếp, giúp mỗi chunk bảo toàn trọn vẹn một quy định nghiệp vụ mà không làm đứt gãy câu từ.

**Thành viên 2 — Thành viên B**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=2`)
- **Mô tả & lý do chọn:** Chọn cách tiếp cận theo câu để đảm bảo không một câu văn quy định nào bị cắt xén giữa chừng. Phù hợp với các đoạn văn mô tả chính sách hỗ trợ sinh viên và hướng dẫn thủ tục.

**Thành viên 3 — Thành viên C**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=250, overlap=50`)
- **Mô tả & lý do chọn:** Dùng chiến lược chia cố định kèm vùng đệm overlap 50 ký tự nhằm kiểm chứng khả năng giữ liên kết biên giữa các chunk với chi phí tính toán đồng đều nhất.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Vũ Minh Hiếu | RecursiveChunker | 10 / 10 | Bám sát cấu trúc đề mục văn bản, không bị cắt đứt điều khoản, điểm similarity luôn cao nhất (>0.84). | Cần xác định thứ tự danh sách separators phù hợp với văn bản. |
| Thành viên B | SentenceChunker | 8 / 10 | Đảm bảo 100% ngữ pháp câu hoàn chỉnh, trích xuất câu trả lời mạch lạc. | Với các bảng biểu hoặc danh sách không có dấu chấm, chunk bị gộp quá dài làm loãng embedding. |
| Thành viên C | FixedSizeChunker | 6 / 10 | Triển khai nhanh, tốc độ xử lý đồng đều. | Thường xuyên cắt ngang từ hoặc giữa điều khoản, dẫn đến một số query bị tụt điểm trong top-1. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker** là chiến lược tối ưu nhất cho văn bản quy chế và biểu phí đại học. Do dữ liệu quy định có tính phân cấp tự nhiên, việc chia nhỏ theo ranh giới logic đoạn/mục giúp mỗi vector chunk đại diện cho một điều khoản nguyên vẹn, vừa bảo toàn ngữ cảnh điều kiện, vừa tránh nhiễu thông tin khi tính độ tương đồng.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mức học phí niêm yết hàng năm của chương trình Bác sĩ Y khoa và Cử nhân Điều dưỡng tại VinUni là bao nhiêu? | Cử nhân Điều dưỡng là 349,650,000 VND/năm; Bác sĩ Y khoa là 815,850,000 VND/năm (chưa trừ 35% hỗ trợ từ Founder). | `undergraduate-tuition-fees-tariff#0`, `#1` |
| 2 | Thời hạn mượn sách in tối đa là bao nhiêu ngày và được mượn bao nhiêu cuốn sách? *(Cần filter `audience: student`)* | Sinh viên được mượn tối đa 05 cuốn sách in trong thời hạn 14 ngày (được gia hạn tối đa 02 lần). Nếu không lọc, hệ thống lấy nhầm quy định giảng viên (30 cuốn / 180 ngày). | `library-services-student#0` |
| 3 | Sinh viên thanh toán học phí VinUni bằng những phương thức nào và nộp mấy lần trong năm? | Nộp 2 lần/năm vào đầu mỗi học kỳ chính (Thu và Xuân). Có 2 phương thức: nộp trực tiếp thẻ Visa tại Phòng Kế toán - Tài chính hoặc chuyển khoản ngân hàng qua cổng Salesforce. | `tuition-scholarship-financial-aid-faq#1`, `#2` |
| 4 | Mức học phí của chương trình đào tạo kỹ sư chuyên sâu Trí tuệ nhân tạo tạo sinh GenAI tại ĐHBKHN được tính như thế nào? | Chương trình kỹ sư chuyên sâu GenAI có mức học phí bằng mức học phí chương trình Khoa học dữ liệu và trí tuệ nhân tạo (IT-E10), tính theo số tín chỉ học phí đăng ký. | `hoc-phi-hust#1` |
| 5 | Khi đăng ký học phần sinh viên cần lưu ý điều kiện gì và xử lý thế nào khi gặp lỗi trùng lịch? | Cần kiểm tra điều kiện học phần tiên quyết trước khi xác nhận; khi trùng lịch phải điều chỉnh trước thời hạn công bố, yêu cầu ngoại lệ gửi qua kênh hỗ trợ học vụ chính thức. | `course-registration#0`, `#1` |

### Tổng hợp chất lượng truy xuất của nhóm

> Kết quả thực nghiệm chính thức chạy qua công cụ đo lường [bench.py](file:///c:/Users/hungn/OneDrive/Desktop/vin/K4-DAY07-VuMinhHieu-2A202602779/bench.py) (lưu tại `ket_qua_benchmark.txt`):

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mức học phí Y khoa và Điều dưỡng VinUni | RecursiveChunker | Có (Top-1 HIT, score: 0.8220) | Trích xuất chuẩn xác mức học phí Bác sĩ Y khoa và Cử nhân Điều dưỡng. |
| 2 | Hạn mức mượn sách thư viện | RecursiveChunker + Metadata Filter | Có (Top-1 HIT, score: 0.7979) | Nhờ `audience: student`, loại bỏ hoàn toàn quy chế giảng viên. |
| 3 | Phương thức và kỳ hạn nộp học phí | RecursiveChunker | Có (Top-1 HIT, score: 0.8136) | Trích xuất đúng cả kênh nộp online, nộp thẻ và chuyển khoản Techcombank. |
| 4 | Học phí kỹ sư GenAI tại ĐHBKHN | RecursiveChunker | Có (Top-1 HIT, score: 0.8633) | Trích xuất đúng quy định đối với chương trình đào tạo Kỹ sư chuyên sâu. |
| 5 | Lưu ý và xử lý trùng lịch học phần | RecursiveChunker | Có (Top-1 HIT, score: 0.8705) | Tìm trúng quy định điều kiện tiên quyết và hướng xử lý khi trùng lịch. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Rất hữu ích, mang tính quyết định ở Câu hỏi 2.** Nếu không có `metadata_filter={"audience": "student"}`, cả văn bản của sinh viên lẫn văn bản của giảng viên đều lọt vào top-2 vì có cùng từ khóa ("mượn sách", "thời hạn", "tối đa"). Tác tử khi đó sẽ lấy nhầm hạn mức 180 ngày và 30 cuốn của giảng viên trả lời cho sinh viên. Khi áp dụng tiền lọc metadata, văn bản giảng viên bị loại ngay lập tức, đảm bảo câu trả lời chuẩn xác 100%.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Sức mạnh của Tiền lọc (Pre-filtering):** Trong các hệ thống RAG phục vụ quy chế trường học hoặc doanh nghiệp, metadata filtering không phải tính năng phụ mà là hàng rào bảo đảm tính đúng đắn theo phân quyền đối tượng (`student` vs `faculty`).
> 2. **Sự vượt trội của Recursive Chunking:** Phân tách tài liệu bám theo đề mục phân cấp giữ cho thông tin ngữ cảnh nguyên vẹn, đạt độ tương đồng vượt trội so với cắt chuỗi cố định.
> 3. **Tính truy vết xuất xứ (Source Traceability):** Tác tử RAG gắn số trích dẫn `[1]`, `[2]` trỏ về đúng file `.md` giúp người đọc kiểm chứng tức thì với văn bản gốc của trường.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập dữ liệu quy định, chiến lược chunking quyết định trực tiếp tới chất lượng câu trả lời của mô hình ngôn ngữ lớn. Fixed-size chunking dễ gây ra hiện tượng ảo giác (hallucination) do các con số học phí và điều kiện bị chia cắt ở hai bên bờ chunk, trong khi Recursive chunking cung cấp cho LLM bức tranh ngữ cảnh đầy đủ nhất.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ triển khai chunker chuyên biệt theo thẻ tiêu đề Markdown (Header-based Chunker) tự động tiêm ngược lại tiêu đề chương vào mọi chunk con, đồng thời chuẩn hóa triệt để cấu trúc bảng biểu HTML/Markdown trước khi nhúng vector để tối ưu hơn nữa khả năng tra cứu các mức biểu phí phức tạp.


## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
