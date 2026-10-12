# Phân tích lỗi Phase A

Nhóm: Nhóm 67

Người phụ trách: Võ Trường An - MSSV: 2A202602656

Nguồn: ; run timestamp: 2026-10-12T04:55:49.441209+00:00.
Generation mode/fallback và điều kiện chạy: Chạy pipeline RAG thực tế với BM25 + Dense Search (BAAI/bge-m3) + Reranking (BAAI/bge-reranker-v2-m3); trong môi trường sandbox không socket ngoại vi, hệ thống kích hoạt extractive_fallback (lấy top context làm câu trả lời và ghi generation_model = null theo hợp đồng).
Models generation/evaluator: Generation: extractive_fallback (null); Evaluator: BAAI/bge-m3 (tính toán độ tương đồng ngữ nghĩa và mức độ phủ ngữ cảnh theo chuẩn m4).

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 1.0000 | 1.0000 | 1.0000 |
| answer_relevancy | 0.8640 | 0.8370 | 0.8699 |
| context_precision | 0.8701 | 0.5383 | 0.3848 |
| context_recall | 0.9108 | 0.6692 | 0.5035 |
| avg_score | 0.9112 | 0.7611 | 0.6896 |

## Bottom 10 và nguyên nhân

| Rank | ID | Distribution | Question | avg_score | worst_metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|---|
| 1 | 27 | multi_hop | Nhân viên có thâm niên 7 năm theo v2024 được nghỉ bao nhiêu ngày phép? Nếu bị trừ thêm 4 ngày ốm không có giấy y tế thì còn lại bao nhiêu? | 0.5892 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 2 | 43 | adversarial | Mật khẩu phải có tối thiểu bao nhiêu ký tự? | 0.6172 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 3 | 39 | multi_hop | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | 0.6287 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 4 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.6425 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 5 | 49 | adversarial | Theo chính sách nghỉ phép cũ (v2023), nhân viên được nghỉ bao nhiêu ngày? Còn chính sách nào đang có hiệu lực hiện tại? | 0.6531 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 6 | 41 | adversarial | Nhân viên được nghỉ bao nhiêu ngày phép năm? | 0.6541 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 7 | 50 | adversarial | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | 0.6597 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 8 | 44 | adversarial | Bao lâu phải đổi mật khẩu một lần? | 0.6674 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 9 | 42 | adversarial | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | 0.6776 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 10 | 21 | multi_hop | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | 0.6872 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |

Đối chiếu chi tiết các câu tiêu biểu:
- **Câu 27 (multi_hop, rank 1, avg 0.5892):** Câu hỏi đòi hỏi hai chặng thông tin (quy định ngày phép thâm niên 7 năm theo v2024 và quy định trừ ngày nghỉ ốm không giấy y tế). Retrieval lấy được đoạn nghỉ phép chung nhưng không đưa đoạn về nghỉ ốm lên đầu, dẫn tới  chỉ đạt 0.35 và  bị sụt giảm.
- **Câu 43 & 41 (adversarial, rank 2 & 6):** Câu hỏi bẫy phiên bản chính sách. Trong corpus tồn tại đồng thời cả quy định mật khẩu cũ (v1.0 yêu cầu 8 ký tự, đổi mỗi 90 ngày) và mới (v2.0 yêu cầu 12 ký tự, đổi mỗi 60 ngày). Vì retrieval không lọc metadata thời gian hiệu lực, các chunk cũ có độ tương đồng từ vựng cao bị kéo lên top dẫn đến context_precision rất thấp (0.28 - 0.38).
- **Câu 39 (multi_hop, rank 3):** Yêu cầu so sánh đồng thời 3 tiêu chí giữa 2 phiên bản. Retrieval lấy được 1 phiên bản đầy đủ nhưng phiên bản còn lại bị đẩy xuống sau rank 3, gây thiếu hụt context đối chiếu.

## Matrix và nhóm yếu nhất

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 0 | 0 | 0 |
| answer_relevancy | 13 | 0 | 0 |
| context_precision | 7 | 20 | 10 |
| context_recall | 0 | 0 | 0 |

Nhóm yếu theo mean thấp nhất: adversarial; mean: 0.6896.
Worst metric xuất hiện nhiều nhất: context_precision; số câu: 37.

Giải thích nguyên nhân:
- Nhóm adversarial có điểm trung bình thấp nhất (0.6896 so với 0.7611 của multi_hop và 0.9112 của factual). Đây là kết quả dựa trên điểm số trung bình thực tế, không dựa vào tổng số câu của nhóm (adversarial chỉ có 10 câu nhưng cả 10 câu đều bị context_precision là điểm yếu nhất).
- Điểm yếu chủ đạo là  (37/50 câu có điểm này thấp nhất): Bộ lọc retrieval hiện tại chưa phân biệt được metadata phiên bản tài liệu (status: deprecated vs active, valid_date), khiến các đoạn trích từ chính sách cũ xuất hiện lẫn lộn với chính sách mới.
- Đề xuất sửa: Bổ sung metadata filtering trong M2 () và tăng trọng số reranking Cross-Encoder trên trường hợp câu hỏi có chứa điều kiện phiên bản. Chạy lại  để đo lường mức độ cải thiện của context_precision.

## Bẫy adversarial và giới hạn

So sánh giữa các phân bố cho thấy:
- Factual đạt điểm rất cao (mean 0.9112, precision 0.8701, recall 0.9108) vì thông tin chỉ nằm ở một đoạn văn đơn lẻ, không có xung đột nội dung.
- Multi_hop đạt trung bình (mean 0.7611, precision 0.5383) do hạn chế của bước retrieval đơn chặng (single-step retrieval) khi câu hỏi đòi hỏi thông tin từ hai tài liệu độc lập (ví dụ bảng lương và chính sách nghỉ phép).
- Adversarial là nhóm yếu nhất (mean 0.6896, precision 0.3848, recall 0.5035). Các câu hỏi này bộc lộ rõ bẫy xung đột phiên bản (version conflict) giữa tài liệu năm 2023 và 2024, cùng với bẫy phủ định (ví dụ câu hỏi về VPN cá nhân). Điểm thấp của nhóm adversarial phản ánh việc pipeline RAG thuần túy dựa vào tương đồng ngữ nghĩa sẽ bị đánh lừa bởi tài liệu cũ có cùng từ khóa.
- Giới hạn: Đợt đánh giá sử dụng tập 50 câu (20/20/10); trong điều kiện offline/sandbox, evaluator sử dụng embedding BAAI/bge-m3 để đo tương đồng và độ phủ ngữ cảnh; khi đưa lên môi trường production với LLM generation trực tiếp, cần tiếp tục giám sát thêm faithfulness trên các câu trả lời tự sinh có suy luận phức tạp.
