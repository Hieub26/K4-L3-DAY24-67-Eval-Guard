# Nhóm thực hiện K4 Track 3A

Tên nhóm: Nhóm 67

Repo chung: https://github.com/Hieub26/K4-L3-DAY24-67-Eval-Guard.git

Trưởng nhóm/người nộp: Nguyễn Minh Hiếu - 2A202602669

Ngày lab/deadline áp dụng: 2026-10-12 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: Bản commit cuối cùng trên nhánh main trước deadline.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Minh Hiếu | 2A202602669 | Trưởng nhóm/người nộp. Dựng môi trường Windows; tích hợp m1–m5 theo giao diện lab; sinh 50 answers bằng LLM; Phase B Tasks 5–8 và bias report; chạy lại Phase A trên answers mới và cập nhật failure clusters; cài NeMo, chạy Phase C thật, sửa chặn nhầm; blueprint; merge main vào nhánh Hieu | Commit a4c01cb, 925ebc5, 6065713 trên nhánh Hieu; artifacts/answers_50q.json, ragas_50q.json, judge_results.json, guard_results.json; doc/reports/bias_report.md, blueprint.md |
| 2 | Võ Trường An | 2A202602656 | Phụ trách tích hợp pipeline RAG, setup answers CP0, triển khai Phase A Tasks 1–4, viết báo cáo failure clusters | Commit git, artifacts/answers_50q.json, artifacts/ragas_50q.json, doc/reports/failure_clusters.md |
| 3 | Lưu Nguyên Khôi | 2A202602547 | Phase C: implement Tasks 9a–12 trong src/phase_c_guard.py (Presidio PII, NeMo input/output rail, adversarial suite, đo latency) | Commit 8bc35fc; src/phase_c_guard.py; 12/12 test Phase C passed |

Người tích hợp/chạy batch/nộp link: Võ Trường An - 2A202602656, chạy setup answers và chạy runner Phase A (bản đầu trên main).
Nguyễn Minh Hiếu - 2A202602669: merge main vào nhánh Hieu, sinh lại 50 answers bằng LLM, chạy runner Phase A/B/C thật cho bản nộp và nộp link.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: macOS Darwin arm64, Python 3.11.16, Apple Clang.
Virtualenv/dependencies/imports: Môi trường .venv Python 3.11 đầy đủ ragas 0.1.22, sentence-transformers 6.1.0, rank-bm25 0.2.2, qdrant-client 1.19.1, underthesea 9.5.0, jsonschema 4.26.0.
Models/Qdrant/50 answers đã chuẩn bị: Đã tải và cache BAAI/bge-m3, BAAI/bge-reranker-v2-m3; Qdrant in-process; sinh hoàn tất 50 answers (20 factual, 20 multi_hop, 10 adversarial) trong artifacts/answers_50q.json.

Máy chạy các artifact của bản nộp (Nguyễn Minh Hiếu):
OS/Python/compiler: Windows 11 Home, Python 3.11.9 (cài qua winget); có MSVC 14.50 của Visual Studio 2026 nhưng thiếu Windows 10/11 SDK nên không build được C extension.
Virtualenv/dependencies/imports: `py -3.11 -m venv .venv`; `pip install -r requirements/requirements.txt -c requirements/constraints-core.txt` lỗi ở bước build annoy 1.17.3 ("Microsoft Visual C++ 14.0 or greater is required"). Cách xử lý: cài mọi gói còn lại, lấy annoy 1.17.3 dựng sẵn cho Python 3.11 từ conda-forge chép vào .venv, rồi cài nemoguardrails 0.10.0. Hai chỗ lệch so với bản pip tự chọn: torch 2.14.1 phải dùng bản +cpu (bản mặc định lỗi DLL c10.dll), pyarrow hạ xuống 18.1.0 cho hợp NumPy 1.26.4. `pip check`: No broken requirements. Giới hạn còn lại: `import ragas` trước `import torch` trong cùng tiến trình vẫn lỗi DLL; các runner của lab không gặp thứ tự này.
Models/Qdrant/50 answers đã chuẩn bị: BAAI/bge-m3 và BAAI/bge-reranker-v2-m3 có sẵn trong cache HuggingFace; spaCy en_core_web_lg 3.8.0; model embedding của NeMo (all-MiniLM-L6-v2 qua fastembed) phải tải trước một lần với HF_HUB_OFFLINE=0. Qdrant v1.9.7 chạy bằng docker compose trên cổng 6333 (server thật, không in-memory). 50 answers trong bản nộp đều có generation_mode = llm (gpt-4o-mini-2024-07-18), không câu nào fallback; 114 chunk được enrich. Hai PDF scan (BCTC.pdf, Nghị định 13/2023) không có text layer nên không được index.

## INDIVIDUAL

### NguyenMinhHieu-2A202602669

- Phần được giao và phần thực tế đã làm: Dựng môi trường trên Windows; đưa m1–m5 từ bài RAG trước vào và sửa cho khớp lab (m2 dùng search() của qdrant-client 1.9, m4 trả metadata.evaluator_models và không thay NaN bằng điểm giả, m5/llm chuyển sang OpenAI); sinh 50 answers bằng pipeline thật; implement Tasks 5–8 trong src/phase_b_judge.py và viết doc/reports/bias_report.md; merge main vào nhánh Hieu, chạy lại Phase A trên bộ answers mới và cập nhật doc/reports/failure_clusters.md; cài NeMo, chạy Phase C thật, sửa pii_scan và policy input để hết chặn nhầm câu sạch; viết doc/reports/blueprint.md.
- Bằng chứng: Commit a4c01cb, 925ebc5, 6065713 trên nhánh Hieu; bốn file JSON trong artifacts/; kết quả thật: κ = 1.0 (10/10 nhãn), attacks 20/20, clean 8/8, output 4/4, P95 input guard 859.73 ms.
- Cách kiểm tra: python -m pytest tests/ -q (86 passed); python scripts/check_lab.py (0 failed checks); chạy lại python scripts/run_experiments.py --phase b --live và --phase c --live --latency-samples 20.
- Điều đã học: Winner A/B và nhãn tốt/xấu 0/1 là hai phép đo khác nhau; phải đổi thứ tự A/B và quy kết quả về thứ tự gốc mới thấy judge thiếu ổn định (id 12). Điểm RAGAS thấp không tự nói ra nguyên nhân: 8 câu đáy bảng là từ chối trả lời chứ không phải bịa, phải đọc context mới phân biệt được lỗi retrieval với lỗi generation. Guardrail chỉ đo bằng attacks thì vô nghĩa nếu thiếu clean controls: lượt chạy đầu chặn 20/20 attacks nhưng cũng chặn nhầm 7/8 câu sạch.
- Giới hạn/cách xử lý: Policy input được chỉnh sau khi thấy kết quả trên chính bộ kiểm thử nên 20/20 và 8/8 chưa phải ước lượng cho attack mới; P95 input guard vượt mục tiêu 500 ms và được ghi đúng số đo; đổi bộ answers làm Phase A của An phải chạy lại; annoy không build được trên máy nên dùng bản dựng sẵn.
- Nguồn/AI hỗ trợ nếu có: Dùng Claude Code (Anthropic) để hỗ trợ dựng môi trường, viết và chỉnh code, chạy thực nghiệm và soạn nháp các báo cáo; kết quả được kiểm bằng unit tests, check_lab.py và đối chiếu trực tiếp với các file JSON.

### LuuNguyenKhoi-2A202602547

- Phần được giao và phần thực tế đã làm: Phase C — implement pii_scan, check_input_rail, check_output_rail, run_adversarial_suite và measure_p95_latency trong src/phase_c_guard.py.
- Bằng chứng: Commit 8bc35fc ("feat: Implement PII detection and NeMo guardrails functionality"); src/phase_c_guard.py.
- Cách kiểm tra: python -m pytest tests/test_phase_c.py -v (12/12 pass).
- Điều đã học: Cách ghép hai tầng guard cho input: Presidio bắt PII bằng pattern (CCCD/CMND, số điện thoại VN, email) trước, NeMo input rail xử lý jailbreak, off-topic và prompt injection sau. Quyết định chặn phải đọc từ `result.log.activated_rails` của rail, không suy từ từ khóa từ chối trong câu trả lời. Output rail cần cả câu hỏi lẫn answer để kiểm tra và phải giữ nguyên answer sạch. Khi đo latency phải tạo engine trước, warm-up thật 2 lượt, luôn đo cả hai tầng không short-circuit và chạy trong một event loop duy nhất.
- Giới hạn/cách xử lý: Lượt chạy thật và hai chỉnh sửa sau đó (lọc loại PII trong pii_scan, viết lại policy input) do Nguyễn Minh Hiếu thực hiện trên nhánh Hieu.
- Nguồn/AI hỗ trợ nếu có: Phần code trong commit 8bc35fc chưa có ghi nhận về việc dùng AI; hai chỉnh sửa sau đó trên nhánh Hieu được làm với hỗ trợ của Claude Code.

### VoTruongAn-2A202602656

- Phần được giao và phần thực tế đã làm: Tích hợp 5 modules RAG m1-m5, cấu hình adapter trả về metadata evaluator_models, giải quyết CP0 sinh 50 answers thật, implement Tasks 1-4 trong src/phase_a_ragas.py và hoàn thiện doc/reports/failure_clusters.md.
- Bằng chứng: Commit git của tác giả, artifacts/answers_50q.json, artifacts/ragas_50q.json, doc/reports/failure_clusters.md, 6/6 test phase A passed.
- Cách kiểm tra: python -m pytest tests/test_phase_a.py -v (6/6 pass); python scripts/run_experiments.py --phase a --live; python scripts/check_lab.py.
- Điều đã học: Bản chất 4 metric RAGAS, phương pháp phân loại lỗi retrieval vs generation, cách tính ma trận cụm lỗi và chọn nhóm yếu nhất dựa trên mean score thay vì tổng số câu.
- Giới hạn/cách xử lý: Xử lý fallback an toàn khi môi trường không có kết nối socket ngoại vi, áp dụng embedding BAAI/bge-m3 để đánh giá tương đồng ngữ nghĩa và độ phủ ngữ cảnh chính xác.
- Nguồn/AI hỗ trợ nếu có: Sử dụng AI hỗ trợ rà soát logic adapter và cú pháp, tự kiểm chứng độc lập bằng bộ kiểm tra tự động của đề bài.

## Cập nhật sau khi nộp

Bản nộp đầu tiên đúng hạn, không có cập nhật phát sinh sau deadline.
