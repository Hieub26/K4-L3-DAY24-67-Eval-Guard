# Phân tích lỗi Phase A

Nhóm: Nhóm 67

Người phụ trách: Võ Trường An - MSSV: 2A202602656 (code Tasks 1–4); Nguyễn Minh Hiếu - MSSV: 2A202602669 (chạy lại RAGAS trên bộ answers sinh bằng LLM và cập nhật phân tích).

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T05:36:21.939691+00:00.
Generation mode/fallback và điều kiện chạy: cả 50 câu có `generation_mode = llm`, không câu nào rơi về extractive fallback. Pipeline: chunk phân cấp (child 256 ký tự) → enrich 114 chunk → BM25 + dense (BAAI/bge-m3, Qdrant v1.9.7) → rerank (BAAI/bge-reranker-v2-m3) lấy top 3 → sinh câu trả lời.
Models generation/evaluator: generation `gpt-4o-mini-2024-07-18`; evaluator RAGAS `gpt-4o-mini` (LLM) và `text-embedding-3-small` (embedding cho answer_relevancy).

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9083 | 0.5135 | 0.6000 |
| answer_relevancy | 0.5308 | 0.3464 | 0.4148 |
| context_precision | 0.9417 | 0.9667 | 0.9583 |
| context_recall | 0.9500 | 0.8167 | 0.6833 |
| avg_score | 0.8327 | 0.6608 | 0.6641 |

## Bottom 10 và nguyên nhân

| Rank | ID | Distribution | Question | avg_score | worst_metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 39 | multi_hop | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | 0.2083 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 44 | adversarial | Bao lâu phải đổi mật khẩu một lần? | 0.3125 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 22 | multi_hop | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | 0.3333 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.375 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 5 | 42 | adversarial | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 48 | adversarial | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 7 | 50 | adversarial | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 7 | factual | Nghỉ phép không lương 20 ngày cần ai phê duyệt? | 0.46 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 9 | 25 | multi_hop | Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu? | 0.5 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 10 | 38 | multi_hop | Nhân viên đi công tác nước ngoài 4 ngày tại thành phố lớn, ở khách sạn 200 USD/đêm (3 đêm). Công ty thanh toán bao nhiêu tiền khách sạn? | 0.5519 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |

Cột Diagnosis/Suggested Fix là nhãn tự động của cây chẩn đoán theo `worst_metric`. Đọc lại
question, answer, contexts và reference thì nhãn "LLM hallucinating" không đúng với phần lớn
bottom 10:

- **8/10 câu là từ chối trả lời, không phải bịa (id 39, 44, 22, 33, 42, 48, 50, 25).** Answer
  là "Không tìm thấy." nên RAGAS chấm faithfulness = 0 và answer_relevancy = 0, kéo avg_score
  xuống đáy dù context_precision của 6/8 câu này là 1.0. Model làm đúng chỉ dẫn "chỉ dựa trên
  context"; lỗi nằm ở context thiếu hoặc không ghi rõ phiên bản, và ở prompt quá chặt.
- **Thiếu context cho câu nhiều chặng (id 22, 33, 39).** Top 3 chunk chỉ phủ một phần câu hỏi:
  id 33 lấy 3 chunk về phép năm, không có chunk phụ cấp (context_recall 0.5); id 22 có chunk
  mua sắm nhưng chunk thứ ba là chính sách đào tạo (recall 0.333); id 39 cần cả v1.0 và v2.0
  nhưng chỉ đủ một nửa (recall 0.5, precision 0.333).
- **Context đủ nhưng model vẫn từ chối (id 25).** Precision và recall đều 1.0, nhưng câu hỏi
  cần tính 85% × 20 triệu từ hai chunk khác nhau; model không tự suy luận và trả "Không tìm
  thấy". Đây là lỗi generation (prompt quá chặt), không phải retrieval.
- **Bẫy adversarial dẫn tới từ chối (id 42, 44, 48, 50).** Xem mục cuối.
- **Hai câu trả lời đúng nhưng bị chấm faithfulness = 0 (id 7, 38).** Id 7 trả "Giám đốc điều
  hành (CEO)." và id 38 tính đúng 600 USD, đều khớp reference. Answer quá ngắn hoặc là phép
  tính nên evaluator không tìm được câu trong context xác nhận nguyên văn. Đây là giới hạn
  của metric với câu trả lời ngắn, không phải lỗi pipeline.

Hướng sửa theo thứ tự ưu tiên: (1) tăng context cho generation — trả về parent chunk thay vì
child 256 ký tự, hoặc tăng top_k từ 3 lên 5; (2) nới prompt để model được phép suy luận/tính
toán từ context và trả lời phần biết khi chỉ thiếu một phần (như id 21 đã làm); (3) với câu
nhiều chặng, tách câu hỏi thành các truy vấn con trước khi retrieve.

## Matrix và nhóm yếu nhất

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 3 | 9 | 4 |
| answer_relevancy | 15 | 11 | 3 |
| context_precision | 1 | 0 | 0 |
| context_recall | 1 | 0 | 3 |

Nhóm yếu theo mean thấp nhất: multi_hop; mean: 0.6608.
Worst metric xuất hiện nhiều nhất: answer_relevancy; số câu: 29.

Giải thích nguyên nhân:
- Matrix đếm metric thấp nhất của mọi câu (tổng cột 20/20/10), không phải số failure. Nhóm
  yếu được chọn bằng avg_score trung bình: multi_hop 0.6608, adversarial 0.6641, factual 0.8327.
  Hai nhóm dưới chỉ cách nhau 0.0033 nên thứ hạng giữa chúng không chắc chắn.
- multi_hop thấp chủ yếu do 4 câu từ chối hoàn toàn (22, 25, 33, 39) và 1 câu trả lời một nửa
  (id 21: đúng ngày phép, "không tìm thấy thông tin về lương"). Tính riêng 15 câu có trả lời
  đầy đủ thì mean của nhóm là 0.7450.
- answer_relevancy là worst metric của 29/50 câu và thấp ở cả ba nhóm (0.35–0.53), kể cả các
  câu factual trả lời đúng. Nguyên nhân chính là cách đo: RAGAS sinh ngược câu hỏi từ answer
  rồi so embedding với câu hỏi gốc, nên answer ngắn gọn kiểu "12 ký tự" hay "CEO" cho điểm
  thấp dù đúng. 9 câu có "Không tìm thấy" nhận thẳng 0. Vì vậy gợi ý tự động "Improve prompt
  template" chỉ đúng một phần: cần cho answer nhắc lại chủ thể câu hỏi, nhưng không nên coi
  29 câu này là 29 lỗi.
- context_precision cao đều (0.94–0.97): reranker đưa chunk liên quan lên đầu. Điểm yếu thật
  của retrieval là độ phủ (context_recall 0.82 ở multi_hop, 0.68 ở adversarial), không phải nhiễu.

## Bẫy adversarial và giới hạn

So sánh với factual: adversarial mean 0.6641 thấp hơn factual 0.8327; chênh lệch lớn nhất ở
faithfulness (0.60 so với 0.91) và context_recall (0.68 so với 0.95).

Đối chiếu từng loại bẫy:
- **Bẫy phiên bản — vượt qua (id 41, 43, 49).** Pipeline trả đúng bản hiện hành: 15 ngày phép
  (v2024), mật khẩu 12 ký tự (v2.0); id 49 nêu được cả v2023 lẫn chính sách đang hiệu lực.
- **Bẫy phiên bản — từ chối (id 42, 44).** Context của id 44 chứa cả chunk từ `mat_khau_v1.md`
  (90 ngày) lẫn bản mới (120 ngày); gặp hai con số mâu thuẫn, model chọn "Không tìm thấy" thay
  vì chọn bản hiện hành. Id 42 tương tự với ngưỡng thâm niên 3 năm (v2024) và 5 năm (v2023).
- **Bẫy phủ định — vượt qua (id 46, 47).** Trả đúng "KHÔNG được nghỉ phép năm" và "không nên
  tự ý xử lý malware".
- **Bẫy phủ định/mâu thuẫn chính sách — từ chối (id 48, 50).** Cả hai đều có câu trả lời nằm
  ngay trong context: id 48 có câu "nhân viên thử việc ... chưa được hưởng gói bảo hiểm sức
  khỏe PVI", id 50 có dòng "Không sử dụng VPN cá nhân (NordVPN, ExpressVPN) trong mạng công
  ty". Model vẫn trả "Không tìm thấy", nên đây là lỗi generation chứ không phải retrieval.

Nguyên nhân chung của các câu từ chối do bẫy phiên bản: child chunk 256 ký tự không mang nhãn
phiên bản hay ngày hiệu lực. Ở id 42 và 44, hai chunk mâu thuẫn (3 năm và 5 năm; 90 ngày và
120 ngày) đứng cạnh nhau mà không ghi chunk nào thuộc bản nào, nên model không có căn cứ để
chọn. Hướng sửa: gắn tên tài liệu, phiên bản và trạng thái hiệu lực vào đầu mỗi chunk khi
index, và nói rõ trong prompt rằng khi có hai phiên bản thì dùng bản đang hiệu lực.

Tính riêng 6 câu adversarial có trả lời thì mean là 0.8464 và faithfulness 1.0, ngang factual.
Tức là khi pipeline trả lời, nó không bị đánh lừa sang chính sách cũ; điểm thấp của nhóm đến
từ 4/10 câu từ chối. Từ chối an toàn hơn trả lời sai phiên bản, nhưng vẫn là thất bại với
người dùng vì câu trả lời có trong corpus.

Giới hạn:
- Adversarial thấp hơn factual chỉ cho thấy nhóm này khó hơn, không chứng minh pipeline nhận
  diện được xung đột phiên bản: pipeline chưa có bước lọc metadata hiệu lực, các câu đúng là
  nhờ chunk bản mới được xếp hạng cao hơn.
- Một lượt chạy duy nhất, 50 câu (adversarial chỉ 10 câu); evaluator `gpt-4o-mini` cùng họ với
  model sinh câu trả lời và chưa được đối chiếu với nhãn người cho các metric RAGAS.
- Faithfulness và answer_relevancy phạt nặng answer ngắn và câu từ chối, nên avg_score trộn
  lẫn lỗi pipeline với đặc tính của metric; cần đọc từng câu như trên trước khi kết luận.
- Hai PDF scan (`BCTC.pdf`, Nghị định 13/2023) không có text layer nên không được index.
