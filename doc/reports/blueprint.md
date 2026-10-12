# Blueprint CI/CD cho RAG và guardrails

Nhóm: Nhóm 67

Người phụ trách: Nguyễn Minh Hiếu — 2A202602669

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: 2026-10-12T06:42:51.306458+00:00; guard models: `gpt-4o-mini`.
Models generation/evaluator/judge từ A/B: generation `gpt-4o-mini-2024-07-18` (answers_50q.json);
evaluator `gpt-4o-mini` và `text-embedding-3-small` (ragas_50q.json); judge `gpt-4o-mini` (judge_results.json).

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

| Tầng | Việc làm | Failure action |
|---|---|---|
| Presidio | Tìm CCCD/CMND, số điện thoại VN, email bằng pattern | Có PII thì chặn request, trả câu từ chối cố định, không gọi LLM |
| NeMo input | Self-check bằng `gpt-4o-mini` theo policy trong `guardrails/config.yml` | Rail dừng thì trả câu từ chối trong `rails.co`, không chạy RAG |
| RAG | BM25 + dense (bge-m3, Qdrant) → rerank top 3 → `gpt-4o-mini` | Không có context hoặc generation lỗi thì trả "Không tìm thấy", không bịa |
| NeMo output | Self-check answer trước khi trả | Rail dừng thì thay answer bằng câu từ chối |

- **Presidio chỉ tính ba loại PII dựa trên pattern.** Lượt chạy đầu dùng toàn bộ recognizer mặc
  định: NER tiếng Anh của spaCy gắn nhầm cụm tiếng Việt thành PERSON và chặn nhầm 7/8 câu sạch.
  Sau khi lọc còn `VN_CCCD`, `VN_PHONE`, `EMAIL_ADDRESS` thì hết chặn nhầm ở tầng này. Hệ quả:
  tên người không còn bị bắt ở Presidio; attack id 5 (hỏi CCCD của người khác, không chứa số)
  do NeMo input chặn.
- **Log và redact:** ghi id request, tầng chặn (`presidio` / `nemo_input` / `nemo_output`), loại
  entity và độ trễ từng tầng. Chỉ lưu bản đã anonymize (`<VN_CCCD>`, `<VN_PHONE>`…), không lưu
  nguyên văn input có PII.
- **Secrets:** `OPENAI_API_KEY` nằm trong `.env` ở máy chạy và trong secret store của CI; `.env`
  đã được gitignore và không có trong artifacts.
- **Fallback:** khi OpenAI lỗi hoặc timeout ở tầng NeMo thì fail-closed (từ chối), vì cho qua
  một request chưa kiểm tra rủi ro hơn từ chối nhầm. Qdrant không kết nối được thì coi là sự
  cố, không âm thầm chuyển sang in-memory trong production.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 14.04 | 16.71 | 16.74 | Đã đo, Task 12 |
| NeMo input | 728.97 | 846.26 | 854.75 | Đã đo, Task 12 |
| Input guard sequential | 743.13 | 859.73 | 869.30 | Đã đo, Task 12; vượt target |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 = 859.73 ms; `latency_budget_ok` = false.

Bottleneck là NeMo input: mỗi lần kiểm tra là một lời gọi `gpt-4o-mini` qua mạng, chiếm khoảng
98% thời gian (P50 729 ms so với 14 ms của Presidio). Ngay cả P50 cũng đã vượt 500 ms, nên
không thể đạt target chỉ bằng tinh chỉnh nhỏ. Hướng giảm: (1) chạy một bộ phân loại cục bộ
nhỏ trước và chỉ gọi LLM cho các câu bộ phân loại không chắc; (2) cache quyết định cho các câu
hỏi lặp lại; (3) chạy self-check song song với retrieval và hủy RAG nếu bị chặn. Hai lượt chạy
trước đó cho P95 khoảng 749 ms và 1493 ms, tức độ trễ dao động mạnh theo mạng; 20 mẫu là quá ít
để chốt P99.

Kế hoạch đo phần chưa đo: dùng cùng 8 câu sạch, 2 warm-up, ít nhất 20 mẫu cho từng scope; ghi
timestamp `perf_counter` ở ranh giới mỗi tầng trong một request thật (có short-circuit) để có
RAG, NeMo output và full guard riêng, không cộng dồn từ `input_guard_ms`.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.

Workflow này **chưa được triển khai**; dưới đây là thiết kế đề xuất.

| Job | Lệnh | Khi nào chạy | Gate |
|---|---|---|---|
| Unit tests offline | `python -m pytest tests/ -q` | Mọi pull request | Có test fail thì dừng |
| Kiểm tra bằng chứng | `python scripts/check_lab.py` | Mọi pull request | Exit code khác 0 thì dừng |
| Eval thật | `python scripts/run_experiments.py --phase a --live` (tương tự b, c) | Thủ công hoặc hằng đêm, vì tốn phí API | Script gate đọc JSON và so ngưỡng |

- `run_experiments.py` hiện chỉ ghi artifact, chưa so ngưỡng. Cần thêm một script gate đọc ba
  file JSON, so với các biến `MIN_FAITHFULNESS`, `MIN_AVG_SCORE`, `MIN_ATTACKS_BLOCKED`,
  `MAX_CLEAN_FALSE_POSITIVES` và trả exit code khác 0 khi không đạt. Chừng nào chưa có script
  đó thì các biến `MIN_*` chỉ là tên đề xuất, chưa phải quality gate.
- Với số liệu hiện tại, gate faithfulness ≥0.75 **không đạt**: trung bình 50 câu là 0.689
  (factual 0.908, multi_hop 0.514, adversarial 0.600). Gate avg_score ≥0.65 đạt (0.730). Gate
  guard đạt: 20/20 attacks, 8/8 clean, 4/4 output cases.
- Gate guard nên chạy mỗi input nhiều lần: self-check là LLM và không hoàn toàn ổn định (xem
  mục dưới), một lượt đạt 8/8 chưa bảo đảm lượt sau cũng đạt.

## Monitoring và cải tiến

| Metric | Cách lấy | Ngưỡng cảnh báo đề xuất |
|---|---|---|
| Tỷ lệ chặn theo tầng | Đếm `blocked_by` trên log request | Tăng hoặc giảm đột ngột so với trung bình 7 ngày |
| False positive | Người dùng báo bị từ chối sai; mẫu ngẫu nhiên các câu bị chặn được người duyệt hằng tuần | Trên 2% số câu được duyệt |
| Tỷ lệ "Không tìm thấy" | Đếm answer từ chối của RAG | Trên 10% (hiện 8/50 = 16% trên bộ test) |
| Latency từng tầng | Timestamp ở ranh giới tầng | P95 input guard trên 1000 ms trong 15 phút |
| Chất lượng RAG | Chạy lại bộ 50 câu hằng đêm | Faithfulness hoặc avg_score giảm quá 0.05 so với lần trước |

- **Xử lý false positive:** thêm câu bị chặn nhầm vào bộ clean controls rồi mới sửa policy, để
  mỗi lần sửa đều được kiểm lại trên toàn bộ attacks.
- **Drift:** chạy lại 20 attacks + 8 clean mỗi khi đổi model, đổi prompt policy hoặc nâng NeMo.
- **Privacy:** log chỉ chứa text đã anonymize; mẫu đưa cho người duyệt cũng lấy từ bản đã redact.
- **Người xử lý:** người trực của nhóm vận hành xem cảnh báo; thay đổi policy cần một người
  khác review.

RAGAS mean/worst distribution: avg_score trung bình 50 câu 0.730; nhóm yếu nhất multi_hop (0.6608).
Cohen’s κ: 1.0 (10/10 nhãn trùng với người).
Attacks passed: 20/20; clean false_positive_rate: 0.0.

Giới hạn cần đọc cùng các số trên:
- **Policy input được chỉnh sau khi thấy kết quả trên chính bộ kiểm thử.** Prompt gốc cho 18/20
  attacks và 7/8 clean (chặn nhầm câu hỏi về độ dài mật khẩu, bỏ lọt hai câu off-topic). Bản
  chỉnh đầu tiên lên 20/20 nhưng chặn nhầm 2/8 câu sạch; bản hiện tại đạt 20/20 và 8/8. Vì
  vậy 20/20 và 8/8 là kết quả trên dữ liệu đã dùng để chỉnh, không phải ước lượng cho attack
  mới; cần một bộ attack và clean giữ kín để đánh giá lại.
- **Self-check không hoàn toàn ổn định.** Với prompt gốc, hỏi lặp lại cùng một câu sạch cho cả
  "Yes" lẫn "No" (id 104 và 107). Prompt hiện tại ổn định qua 6 lần hỏi mỗi câu, nhưng đó vẫn
  là mẫu nhỏ.
- Bộ dữ liệu nhỏ: 50 câu RAG, 20 attacks, 8 clean, 4 output; một lượt chạy cho mỗi phase.

Cải tiến có thể kiểm tra:
1. Gắn tên tài liệu, phiên bản và trạng thái hiệu lực vào đầu mỗi chunk; kỳ vọng id 42 và 44
   (hai phiên bản mâu thuẫn, model từ chối) trả lời được theo bản hiện hành.
2. Trả parent chunk hoặc tăng top_k từ 3 lên 5; kỳ vọng context_recall của multi_hop (0.82) tăng
   và số câu "Không tìm thấy" giảm từ 8.
3. Nới prompt generation để được suy luận và tính toán từ context; kỳ vọng id 25, 48, 50 (context
   đã chứa đáp án) không còn bị từ chối, faithfulness trung bình vượt 0.75.
4. Thêm bộ phân loại cục bộ trước NeMo input; kỳ vọng P95 input guard xuống dưới 500 ms, kiểm
   bằng cùng phép đo Task 12 và giữ nguyên 20/20, 8/8.
5. Mở rộng bộ nhãn người cho judge với các answer đúng một phần, rồi đo lại κ.
