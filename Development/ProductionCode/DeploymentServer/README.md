outline folder:

ddqn_loss_fn.py: hàm loss function cho mô hình DDQN
htpg_inf.csv: csv của sơ đồ HTPG dùng cho inference
ntpg_inf.csv: csv của sơ đồ NTPG dùng cho inference

inference.py: file chứa hàm inference cho mô hình (file lỗi, ko chạy được)
inference_v2.py: file chứa hàm inference cho mô hình dạng server flask (query input qua url, xuất output ra file + json response)
inference_v3.py: file chứa hàm inference cho mô hình dạng thao tác file (lấy input + xuất output ra file)

misc.py: file chứa các hàm hỗ trợ cho việc inference
NetworkHoneypotEnv_base_fnrfprtest_v3.py: môi trường mô phỏng mạng honeypot

input.tmp: file chứa input cho mô hình (inf_v3)
output.tmp: file chứa output cho mô hình (inf_v3 + inf_v2)

README.md: file mô tả cấu trúc thư mục
test.py: file chứa hàm test cho mô hình (file lung tung, ko chạy được)

UPDATE 02/06/2024: Đã chỉnh cho cả inf_v2 và inf_v3 xuất output ra file
WARNING 02/06/2024: Tui chưa update ntpg_inf.csv và htpg_inf.csv, hai file này của model 10 node random, cần update lại theo mô hình thật của mình để build đúng môi trường

UPDATE 03/06/2024: Đã update model keras 10 node cho inference code
Nhớ thay hai cái file ntpg htpg thành của mình

- Ko cần update model keras, chỉ cần update file ntpg_inf.csv và htpg_inf.csv nếu thay môi trường mạng mới nhưng cùng số node