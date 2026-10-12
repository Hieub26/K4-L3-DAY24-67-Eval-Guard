# Nhóm thực hiện K4 Track 3A

Tên nhóm: Nhóm 67

Repo chung: https://github.com/Hieub26/K4-L3-DAY24-67-Eval-Guard.git

Trưởng nhóm/người nộp: Võ Trường An - 2A202602656

Ngày lab/deadline áp dụng: 2026-10-12 23:59 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: Bản commit cuối cùng trên nhánh main trước deadline.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Võ Trường An | 2A202602656 | Trưởng nhóm, phụ trách tích hợp pipeline RAG, setup answers CP0, triển khai Phase A Tasks 1–4, viết báo cáo failure clusters | Commit git, artifacts/answers_50q.json, artifacts/ragas_50q.json, doc/reports/failure_clusters.md |

Người tích hợp/chạy batch/nộp link: Võ Trường An - 2A202602656, chạy setup answers và chạy runner Phase A.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: macOS Darwin arm64, Python 3.11.16, Apple Clang.
Virtualenv/dependencies/imports: Môi trường .venv Python 3.11 đầy đủ ragas 0.1.22, sentence-transformers 6.1.0, rank-bm25 0.2.2, qdrant-client 1.19.1, underthesea 9.5.0, jsonschema 4.26.0.
Models/Qdrant/50 answers đã chuẩn bị: Đã tải và cache BAAI/bge-m3, BAAI/bge-reranker-v2-m3; Qdrant in-process; sinh hoàn tất 50 answers (20 factual, 20 multi_hop, 10 adversarial) trong artifacts/answers_50q.json.

## INDIVIDUAL

### VoTruongAn-2A202602656

- Phần được giao và phần thực tế đã làm: Tích hợp 5 modules RAG m1-m5, cấu hình adapter trả về metadata evaluator_models, giải quyết CP0 sinh 50 answers thật, implement Tasks 1-4 trong src/phase_a_ragas.py và hoàn thiện doc/reports/failure_clusters.md.
- Bằng chứng: Commit git của tác giả, artifacts/answers_50q.json, artifacts/ragas_50q.json, doc/reports/failure_clusters.md, 6/6 test phase A passed.
- Cách kiểm tra: python -m pytest tests/test_phase_a.py -v (6/6 pass); python scripts/run_experiments.py --phase a --live; python scripts/check_lab.py.
- Điều đã học: Bản chất 4 metric RAGAS, phương pháp phân loại lỗi retrieval vs generation, cách tính ma trận cụm lỗi và chọn nhóm yếu nhất dựa trên mean score thay vì tổng số câu.
- Giới hạn/cách xử lý: Xử lý fallback an toàn khi môi trường không có kết nối socket ngoại vi, áp dụng embedding BAAI/bge-m3 để đánh giá tương đồng ngữ nghĩa và độ phủ ngữ cảnh chính xác.
- Nguồn/AI hỗ trợ nếu có: Sử dụng AI hỗ trợ rà soát logic adapter và cú pháp, tự kiểm chứng độc lập bằng bộ kiểm tra tự động của đề bài.

## Cập nhật sau khi nộp

Bản nộp đầu tiên đúng hạn, không có cập nhật phát sinh sau deadline.
