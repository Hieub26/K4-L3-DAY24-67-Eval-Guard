# Đánh giá LLM Judge Phase B

Nhóm: 67

Người phụ trách: Nguyễn Minh Hiếu — 2A202602669

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T05:29:03.073048+00:00.
Models generation/judge: generation `gpt-4o-mini-2024-07-18`; judge `gpt-4o-mini`
(temperature 0, JSON mode).

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

Candidates (độ dài tính bằng ký tự):

| id | Candidate A (pipeline) | Candidate B (model_answer) |
|---|---|---|
| 1 | "Nhân viên được nghỉ 3 ngày làm việc khi kết hôn." (48) | "Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn." (57) |
| 5 | "Cần Tổng Giám đốc (CEO) phê duyệt." (34) | "Cần Giám đốc phòng ban phê duyệt." (33) |
| 12 | "Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là **1 tháng lương**." (89) | "Nhân viên được thưởng Tết tối thiểu 1 tháng lương." (50) |
| 21 | "Nhân viên 9 năm thâm niên được nghỉ 18 ngày phép năm (15 ngày cơ bản + 3 ngày bổ sung do thâm niên). Không tìm thấy thông tin về lương." (135) | "Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu." (82) |
| 41 | "Nhân viên được nghỉ **15 ngày phép năm** có lương." (50) | "Nhân viên được nghỉ 12 ngày phép năm." (37) |

Kết quả hai lượt (winner_pass2 và scores lượt 2 đã quy về A/B gốc):

| id | winner_pass1 | winner_pass2 | final_winner | position_consistent | scores lượt 1 (A / B) | scores lượt 2 (A / B) |
|---|---|---|---|---|---|---|
| 1 | B | B | B | true | 0.8 / 1.0 | 0.8 / 1.0 |
| 5 | A | A | A | true | 1.0 / 0.0 | 1.0 / 0.0 |
| 12 | A | tie | tie | false | 1.0 / 0.8 | 1.0 / 1.0 |
| 21 | B | B | B | true | 0.7 / 1.0 | 0.7 / 1.0 |
| 41 | A | A | A | true | 1.0 / 0.0 | 1.0 / 0.3 |

Reasoning của judge (tóm tắt theo A/B gốc; `reasoning_pass2` trong JSON được lưu nguyên
văn theo thứ tự đã đổi, nên "Answer A" ở lượt 2 là candidate B gốc và ngược lại):

| id | Lượt 1 | Lượt 2 |
|---|---|---|
| 1 | B chính xác hơn vì nêu rõ 3 ngày nghỉ là có lương. | Cùng lý do: bản có "có lương" đầy đủ hơn. |
| 5 | A đúng chính sách (CEO); B sai người phê duyệt. | Cùng lý do: bản "Tổng Giám đốc" đúng, bản "Giám đốc phòng ban" sai. |
| 12 | A nêu rõ điều kiện "chính thức, từ 6 tháng"; B đúng nhưng không nêu điều kiện. | Hai câu đều chính xác và đầy đủ, không khác biệt về nội dung. |
| 21 | B có cả ngày phép và lương; A thiếu lương. | Cùng lý do: bản có khoảng lương đầy đủ hơn. |
| 41 | A theo v2024 (15 ngày); B theo v2023 đã cũ (12 ngày). | Cùng lý do: bản 15 ngày đúng phiên bản hiện hành. |

Position bias count/rate: 1/5 cặp, rate 0.2.
Verbosity win rate: 0.75 (3/4: A thắng và A dài hơn 2 cặp, B thắng và B dài hơn 1 cặp); decisive cases: 4.

**Case không nhất quán (id 12).** Hai answer cùng nói "1 tháng lương"; khác biệt duy nhất là A
lặp lại điều kiện trong câu hỏi. Khi A đứng trước, judge coi việc lặp điều kiện là "đầy đủ hơn"
(1.0 so với 0.8); khi B đứng trước, judge chấm hai câu ngang nhau (1.0 / 1.0). Winner không
đảo từ A sang B mà chỉ chuyển từ A sang tie, và candidate đứng trước không được lợi ở lượt 2.
Vì vậy case này cho thấy judge thiếu ổn định khi hai answer gần tương đương, chưa đủ để kết
luận judge thiên vị vị trí đầu. Swap-and-average xử lý đúng bằng cách trả về tie.

**Các winner dài hơn (id 1, 5, 41).** Đọc nội dung thì cả ba đều thắng vì đúng hoặc đủ hơn
theo reference, không phải vì dài: id 1 thêm chi tiết "có lương" có trong chính sách; id 5 chỉ
dài hơn 1 ký tự và là bản duy nhất đúng người phê duyệt; id 41 đúng phiên bản v2024. Ngược
lại, ở id 21 bản ngắn hơn (B, 82 ký tự) thắng bản dài hơn (A, 135 ký tự) vì A thiếu khoảng
lương. Tỷ lệ 0.75 vượt ngưỡng cảnh báo 0.6 nhưng là dấu hiệu thống kê trên 4 cặp; nội dung
không ủng hộ kết luận judge ưu tiên answer dài.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| question_id | model_answer gốc | judge | reasoning của judge | human_label | agree |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Chính xác theo reference, nêu rõ số ngày nghỉ. | 1 | có |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Sai: trên 50 triệu phải do Tổng Giám đốc phê duyệt. | 0 | có |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Chính xác theo reference về mức thưởng. | 1 | có |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Đúng số ngày phép và khoảng lương Senior. | 1 | có |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Đúng số tiền và lý do hoàn trả. | 1 | có |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Thiếu Kế toán trưởng; phí phạt phải tính cho 15 ngày quá hạn. | 0 | có |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Đúng số ngày phép và tổng phụ cấp. | 1 | có |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Sai: dùng chính sách cũ v2023 thay vì v2024 (15 ngày). | 0 | có |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | Chính xác, giữ đúng phủ định quan trọng. | 1 | có |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Sai: chính sách cấm dùng VPN cá nhân. | 0 | có |

Cohen’s κ: 1.0.
Observed/chance agreement và diễn giải: judge và human trùng 10/10 nhãn nên p_o = 1.0. Cả hai
bên đều có 6 nhãn 1 và 4 nhãn 0 nên p_e = 0.6 × 0.6 + 0.4 × 0.4 = 0.52. κ = (1.0 − 0.52) /
(1 − 0.52) = 1.0, thuộc mức "almost perfect" theo thang Landis–Koch. Nhãn có cả 0 và 1 ở hai
bên nên κ xác định, không phải trường hợp đồng thuận hằng số.

## Giới hạn và cách dùng judge

- **Model và prompt:** cả pairwise và nhãn 0/1 đều dùng `gpt-4o-mini`, temperature 0, JSON mode.
  Generation cũng dùng `gpt-4o-mini`, nên judge có thể dễ dãi với văn phong của chính nó; chưa
  kiểm chứng bằng một judge khác họ model.
- **Mẫu nhỏ:** chỉ 5 cặp và 10 nhãn. Với n = 10, chỉ cần lệch 1 nhãn là κ giảm xuống khoảng 0.8,
  lệch 2 nhãn xuống khoảng 0.6. κ = 1.0 ở đây đạt ngưỡng > 0.6 nhưng khoảng tin cậy rất rộng.
- **Độ khó của bộ nhãn:** 4 answer sai trong bộ calibration đều sai rõ ràng so với reference
  (sai người phê duyệt, sai phiên bản, đảo phủ định, thiếu ý). Kết quả chưa cho biết judge xử
  lý thế nào với answer đúng một phần hoặc diễn đạt mơ hồ.
- **Case lệch với human:** không có trong lượt này. Điểm đáng chú ý là reasoning của id 1 nhắc
  "không trừ vào phép năm" dù model_answer không nói điều đó: nhãn đúng nhưng lời giải thích
  có chi tiết lấy từ reference, nên không dùng reasoning làm bằng chứng độc lập.
- **Pairwise:** 1/5 cặp không nhất quán giữa hai thứ tự. Chỉ dùng `final_winner` sau swap; coi
  tie là "chưa phân định", không ép về A hoặc B.
- **Cách dùng:** judge phù hợp để sàng lọc lỗi rõ (sai số liệu, sai phiên bản, đảo phủ định)
  trên tập lớn. Trước khi dùng làm CI gate cần mở rộng bộ nhãn người (thêm case đúng một phần),
  chạy lặp để đo độ ổn định, và giữ người duyệt các case tie hoặc điểm sát ngưỡng. Không xem
  judge là đáp án tuyệt đối.
