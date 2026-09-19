# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Minh Hiếu  
**Nhóm:** Nhóm L3A — Biến thể Truy xuất Dịch vụ/Quy định Đại học  
**MSSV:** 2A202602779  
**Ngày:** 19/09/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine đo góc giữa hai vector trong không gian đặc trưng đa chiều (nằm trong khoảng [-1, 1]). Độ tương tự cosine cao (tiến sát 1.0) biểu thị góc giữa hai vector rất nhỏ, nghĩa là hai đoạn văn bản hướng về cùng một phương ngữ nghĩa — tức có nội dung, chủ đề hoặc ý định ngữ nghĩa tương đồng cao dù câu từ hay độ dài khác biệt.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** "Sinh viên năm cuối cần hoàn thành khóa luận tốt nghiệp để được xét công nhận ra trường."
- **Câu B:** "Người học trong kỳ học cuối phải hoàn tất đồ án tốt nghiệp nhằm đáp ứng điều kiện nhận bằng cử nhân."
- **Tại sao tương đồng:** Hai câu sử dụng các từ vựng hoàn toàn khác nhau ("sinh viên năm cuối" vs "người học trong kỳ học cuối", "khóa luận" vs "đồ án", "xét công nhận ra trường" vs "nhận bằng cử nhân"), nhưng cùng truyền tải trọn vẹn một thông điệp và quy định học vụ. Mô hình embedding tốt sẽ nhận biết được sự đồng nghĩa tiềm ẩn (latent semantic) và ánh xạ chúng thành hai vector có hướng gần như trùng khít.

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** "Học phí học kỳ phải được nộp qua cổng thông tin sinh viên trước thời hạn quy định."
- **Câu B:** "Món phở bò tái lăn truyền thống cần nước dùng hầm liên tục từ xương ống trong 12 tiếng."
- **Tại sao khác:** Hai câu thuộc về hai lĩnh vực hoàn toàn không liên quan (quy định tài chính học đường đối chiếu với kỹ thuật nấu ăn ẩm thực), không có bất kỳ ngữ cảnh hay từ khóa tương quan nào. Các vector đại diện cho chúng sẽ có phương gần như trực giao (góc xấp xỉ 90 độ) hoặc cách xa nhau trong không gian vector.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid đo khoảng cách hình học tuyệt đối nên bị chi phối mạnh bởi độ lớn (magnitude/length) của vector — vốn bị ảnh hưởng bởi độ dài đoạn văn bản hoặc tần suất xuất hiện từ ngữ. Ngược lại, độ tương tự cosine chỉ quan tâm đến hướng góc ngữ nghĩa và bất biến với quy mô độ dài vector, giúp so sánh chính xác sự tương đồng nội dung giữa một câu ngắn với một đoạn văn bản dài mà không bị sai lệch.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> Áp dụng công thức:  
> `số lượng chunk = ceil((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`  
> `= ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23 chunks`  
> Bước dịch (stride/step) giữa các chunk là: `500 - 50 = 450` ký tự.  
> Các chunk bắt đầu lần lượt tại vị trí: 0, 450, 900, ..., 22 * 450 = 9900 (chunk thứ 23 cắt từ 9900 đến 10000, dài 100 ký tự).  
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước dịch giảm còn `500 - 100 = 400` ký tự.  
> Số lượng chunk mới: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks` (tăng thêm 2 chunks).  
> Chúng ta muốn tăng độ chồng chéo vì overlap tạo vùng đệm ngữ cảnh an toàn, ngăn việc các câu văn quan trọng, mệnh đề logic hay các điều khoản quy định bị cắt đôi tại ranh giới chia tách. Điều này giúp bộ truy xuất (retriever) không bị đứt đoạn thông tin và LLM nhận đủ ngữ cảnh liền mạch để trả lời chính xác.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy phân tách dựa trên kỹ thuật positive lookbehind `r"(?<=[.!?])(?:\s+|\n+)"` để ngắt câu ngay sau các dấu chấm, chấm than hoặc chấm hỏi mà không làm mất đi dấu câu ở cuối câu trước. Sau đó, gom các câu vào chunk với kích thước tối đa `max_sentences_per_chunk` và strip khoảng trắng thừa. Xử lý an toàn trường hợp chuỗi rỗng/khoảng trắng (trả về `[]`), đồng thời ghi nhận hạn chế đã biết: các chữ viết tắt học hàm/học vị ("TS.", "ThS.", "v.v.") hoặc số thập phân ("3.5") có thể bị nhận diện nhầm thành ranh giới kết thúc câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán hoạt động theo tư tưởng chia để trị (divide-and-conquer) với thứ tự ưu tiên các dấu phân cách từ cấu trúc văn bản lớn đến nhỏ `["\n\n", "\n", ". ", " ", ""]`. Base case gồm: văn bản rỗng trả `[]`, độ dài văn bản `<= chunk_size` trả `[current_text]`, và khi hết danh sách dấu phân cách (`remaining_separators == []`) thì fallback cắt trượt theo `chunk_size` để không rơi vào vòng lặp vô hạn. Thuật toán kết hợp cả 2 chiều: đệ quy xuống sâu để chia nhỏ các mảnh còn vượt ngưỡng, và gom lên (recombine) các đoạn ngắn kế tiếp nhau cho tới sát `chunk_size` nhằm tránh tạo ra các chunk quá vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ in-memory dưới dạng danh sách các dictionary (`self._store`), mỗi record lưu `id`, `content`, `metadata` (đảm bảo luôn có `doc_id` trỏ về tài liệu nguồn gốc) và vector `embedding`. Trong `search`, truy vấn được nhúng thành vector qua `self._embedding_fn`, sau đó tính độ tương tự thông qua tích vô hướng `_dot` với từng record (vì vector đã được chuẩn hóa L2 norm = 1, tích vô hướng chính là cosine similarity), sắp xếp giảm dần theo `score` và trả về `top_k` kết quả sau khi loại bỏ trường vector thô.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` bắt buộc thực hiện **tiền lọc (pre-filtering)**: lọc trước toàn bộ các chunk trong kho lưu trữ có `metadata` khớp với tất cả các cặp key-value trong `metadata_filter`, rồi mới tính điểm similarity trên tập ứng viên đã lọc. Nếu lọc sau (post-filtering), top-k có thể bị chiếm hết bởi các tài liệu sai đối tượng dẫn đến trả về rỗng dù tài liệu hợp lệ vẫn có trong store. `delete_document` lọc bỏ mọi chunk có `metadata['doc_id'] == doc_id` hoặc `id == doc_id`, cập nhật lại danh sách và trả về `True` nếu có phần tử bị xóa, ngược lại `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Kiểm tra store: nếu rỗng lập tức trả thông báo hướng dẫn thay vì gọi LLM vô ích. Với câu hỏi hợp lệ, agent gọi `store.search` lấy top-k chunk, định dạng ngữ cảnh có đánh số thứ tự trích dẫn và nguồn rõ ràng `[1] Source: ... \n Content`. Dựng prompt có nguyên tắc grounding nghiêm ngặt: chỉ cho phép trả lời dựa trên ngữ cảnh đã cung cấp, bắt buộc trích dẫn số `[1]`, `[2]` khi nêu sự kiện, và nêu rõ nếu thông tin không có trong tài liệu nhằm loại bỏ hiện tượng ảo giác (hallucination).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\hungn\OneDrive\Desktop\vin\K4-DAY07-VuMinhHieu-2A202602779\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\hungn\OneDrive\Desktop\vin\K4-DAY07-VuMinhHieu-2A202602779
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.11s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

*(Đánh giá sử dụng Google Gemini Embedding `gemini-embedding-001` và hàm `compute_similarity` chuẩn)*

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được phép đăng ký tối đa 20 tín chỉ trong một học kỳ chính. | Hạn mức tín chỉ cao nhất mà người học có thể ghi danh mỗi học kỳ là 20 tín chỉ. | cao | 0.9428 | Đúng |
| 2 | Quy định xét cấp học bổng khuyến khích học tập dựa trên điểm rèn luyện và GPA. | Thủ tục mượn giáo trình và tài liệu nghiên cứu tại thư viện trung tâm. | thấp | 0.6065 | Đúng |
| 3 | Ký túc xá đóng cửa sau 23h00 hàng ngày để đảm bảo an ninh. | Sinh viên nội trú phải có mặt tại phòng trước 11 giờ đêm. | cao | 0.8329 | Đúng |
| 4 | Học phí học kỳ được thanh toán trực tuyến qua cổng thông tin sinh viên. | Sinh viên có thể nộp học phí thông qua chuyển khoản ngân hàng số. | cao | 0.8016 | Đúng |
| 5 | Hạn nộp đơn phúc khảo bài thi kết thúc học phần là 7 ngày sau khi công bố điểm. | Hồ sơ xin cấp visa du học cần chuẩn bị chứng minh tài chính và hộ chiếu. | thấp | 0.5619 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là Cặp 2: dù hai câu nói về hai nghiệp vụ khác nhau (học bổng học vụ vs mượn sách thư viện), điểm số thực tế vẫn đạt 0.6065 — cao hơn mức thấp ngẫu nhiên (~0.0). Điều này cho thấy mô hình embedding biểu diễn ngữ nghĩa theo cụm phân cấp (hierarchical clusters): cả hai câu đều nằm trong miền khái niệm chung về "môi trường giáo dục đại học / sinh viên", nên vector của chúng vẫn có sự tương đồng nền nhất định trước khi phân tách chi tiết nghiệp vụ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src` (sử dụng chiến lược `RecursiveChunker`, embedding `gemini-embedding-001` trên bộ tài liệu dịch vụ/quy định đại học L3A):

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mức học phí niêm yết hàng năm của chương trình Bác sĩ Y khoa và Cử nhân Điều dưỡng tại VinUni là bao nhiêu? | `tuition-scholarship-financial-aid-faq#1`: Cử nhân Điều dưỡng 349,650,000 VND/năm; Bác sĩ Y khoa 815,850,000 VND/năm. | 0.8220 | Có (Relevant) | Cử nhân Điều dưỡng là 349,650,000 VND/năm; Bác sĩ Y khoa là 815,850,000 VND/năm (chưa trừ hỗ trợ 35% từ Founder). [1] |
| 2 | Thời hạn mượn sách in tối đa là bao nhiêu ngày và được mượn bao nhiêu cuốn sách? *(Filter: audience=student)* | `library-services-student#0`: Sinh viên mượn tối đa 05 cuốn sách in trong thời hạn 14 ngày (gia hạn tối đa 02 lần). | 0.7979 | Có (Relevant) | Sinh viên được mượn tối đa 05 cuốn sách in trong thời hạn 14 ngày, gia hạn tối đa 02 lần. [1] |
| 3 | Sinh viên thanh toán học phí VinUni bằng những phương thức nào và nộp mấy lần trong năm? | `financial-regulations-tariff-student#8`: Nộp trực tuyến qua cổng my.vinuni.edu.vn, nộp trực tiếp thẻ tại Phòng Kế toán hoặc chuyển khoản ngân hàng Techcombank. | 0.8136 | Có (Relevant) | Nộp 2 lần/năm vào đầu mỗi kỳ chính (Thu và Xuân); các phương thức gồm nộp trực tuyến qua cổng my.vinuni.edu.vn, nộp trực tiếp thẻ hoặc chuyển khoản ngân hàng. [1] |
| 4 | Mức học phí của chương trình đào tạo kỹ sư chuyên sâu Trí tuệ nhân tạo tạo sinh GenAI tại ĐHBKHN được tính như thế nào? | `hoc-phi-hust#3`: Mức học phí bằng mức học phí chương trình Khoa học dữ liệu và trí tuệ nhân tạo (IT-E10), tính theo số tín chỉ học phí đăng ký. | 0.8633 | Có (Relevant) | Chương trình kỹ sư chuyên sâu GenAI có mức học phí bằng mức chương trình IT-E10, tính theo số tín chỉ học phí của các học phần đăng ký. [1] |
| 5 | Khi đăng ký học phần sinh viên cần lưu ý điều kiện gì và xử lý thế nào khi gặp lỗi trùng lịch? *(Filter: audience=student)* | `course-registration#0`: Kiểm tra học phần tiên quyết trước khi xác nhận; trùng lịch cần điều chỉnh trước thời hạn công bố. | 0.8705 | Có (Relevant) | Cần kiểm tra điều kiện học phần tiên quyết trước khi đăng ký; khi trùng lịch phải điều chỉnh trước thời hạn hoặc gửi yêu cầu ngoại lệ qua kênh chính thức. [1] |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc áp dụng metadata pre-filtering (như `audience: student` hoặc `department: library`) đóng vai trò quyết định đối với dữ liệu dịch vụ đại học, giúp tách biệt hoàn toàn các quy định riêng giữa sinh viên và giảng viên vốn thường dùng chung nhiều từ khóa. Ngoài ra, việc bảo toàn tiêu đề mục trong quá trình chia nhỏ (heading-preserving chunking) giúp các chunk con không bị mất bối cảnh điều khoản khi tính toán độ tương đồng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
