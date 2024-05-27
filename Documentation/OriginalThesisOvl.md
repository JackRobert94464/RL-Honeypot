\chapter[TỔNG QUAN]{TỔNG QUAN} \label{chtongquan}%
%\minitoc %
%\setcounter{baitap}{0}
%\thispagestyle{empty}
%\vspace*{1cm}

Chương này giới thiệu về vấn đề và các nghiên cứu liên quan. Đồng thời, trong chương này chúng tôi cũng trình bày phạm vi và cấu trúc của Khóa luận.

\section{Giới thiệu vấn đề}

Trong bối cảnh mã độc đang trở nên tinh vi hơn về tính năng và khả năng tránh né các công cụ phát hiện, các nhà nghiên cứu đang ứng dụng các kỹ thuật học máy để phát hiện và phân loại các đặc tính của mã độc \cite{gibert2020rise}. Nhờ áp dụng linh hoạt các kỹ thuật chiết tách thuộc tính, các thuật toán, và đặc biệt nhờ vào bộ dữ liệu đa dạng (ember) tỷ lệ phát hiện mã độc của các công cụ này đã đạt hiệu quả lên tới 97\% \cite{eskandari2011metamorphic} từ phương pháp phân tích tĩnh. 

Tuy vậy, nghiên cứu gần đây cũng chỉ ra các công cụ phân tích mã độc theo thuộc tính tĩnh dễ bị qua mặt bởi mẫu đối kháng. Những mẫu này được tạo ra qua việc thay đổi các thông số, đặc tính của mẫu mà không làm ảnh hưởng tới chức năng. Cụ thể về kỹ thuật thì có nghiên cứu của Hu và Tan \cite{hu2017generating}, công trình này sử dụng hệ thống GAN để tạo mẫu (MalwareGAN). Theo hướng áp dụng kỹ thuật học tăng cường thì có nghiên cứu tiên phong của Anderson với thư viện gym-malware (Gym-malware), và sau đó là hệ thống DQEAF \cite{fang2019evading}, AIMED-RL \cite{labaca2021aimed}. Kết quả từ những nghiên cứu này cho thấy khả năng né tránh trình phát hiện có thể lên tới 44\%. 

Sau khi thực nghiệm lại các nghiên cứu có học tăng cường nêu trên, nhóm nhận thấy hầu hết các hệ thống có thể tạo thành công mẫu, nhưng chưa có khả năng kiểm tra khả năng thực thi và tính năng của mẫu. Các nghiên cứu chỉ đơn thuần tạo các mẫu né tránh được trình phát hiện nhưng chưa tập trung vào việc kiểm tra xem mẫu có thể hoạt động hay không. Nhóm chúng tôi quyết định xây dựng thêm tính năng kiểm tra mẫu và thử nghiệm hệ thống mới với nhiều trình phát hiện mã độc khác nhau. Từ đó đánh giá lại khả năng thực của phương pháp tạo mẫu đối kháng sử dụng kỹ thuật học tăng cường.

\section{Giới thiệu những nghiên cứu liên quan}	

Những trình phát hiện mã độc mà nhóm sử dụng và trình bày đều áp dụng phương pháp phân tích tĩnh và có mô hình được huấn luyện với tập dữ liệu EMBER \cite{anderson2018ember}. Tập dữ liệu EMBER cung cấp các mẫu mã độc và 189 thuộc tính và là tập đầy đủ nhất về mã độc.

\subsection{{Mô hình học tăng cường}}

Học tăng cường là một phương pháp học máy. Đặc trưng của phương pháp này là việc học được hiện hoàn toàn qua tương tác trực tiếp với môi trường. Tùy vào thuật toán học tăng cường mà hệ thống có có cách tương tác và cập nhật mô hình khác nhau.

\section{Tính ứng dụng}

Đề tài này đưa hệ thống tạo mẫu đối kháng áp dụng học tăng cường vào ngữ cảnh thực tế hơn. Các mẫu được tạo ra sẽ qua một bước kiểm tra tính năng. Vì vậy kết quả sau khi thực nghiệm sẽ nêu lên tính ứng dụng của hệ thống, khác với các mô hình trước, chỉ dừng lại ở việc tạo mẫu đối kháng đơn thuần dựa vào kết quả của trình phát hiện.

\section{Những thách thức}

Dù có khả năng sửa đổi tệp thực thi ở nhiều vị trí, hệ thống cũng chỉ dừng lại ở việc né tránh trình phát hiện với khả năng phân tích tĩnh. Ngoài ra, bước kiểm tra tính năng của đề tài chỉ kiểm tra khả năng khởi chạy của mẫu, chưa phân tích sâu vào tính năng cụ thể. Liệu những tính năng khác, như khả năng kết nối, khả năng đặc trưng của mẫu có còn được nguyên vẹn hay không, điều này nhóm chúng tôi chưa thể thực hiện được.

\subsection{Phạm vi nghiên cứu}
Trích xuất thuộc tính của tệp thực thi mã độc, tạo ra các mẫu bằng cách thay đổi các thuộc tính của tệp, và đánh giá lại qua các trình phát hiện mã độc và khởi chạy tệp qua môi trường máy ảo.