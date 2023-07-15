# Abstract
Đoạn văn nói về một bài báo nghiên cứu đề xuất một chính sách triển khai thông minh cho các tài nguyên đánh lừa trong mạng. 

Tài nguyên lừa đảo là tài sản giả mạo hoặc gây hiểu lầm => có thể gây nhầm lẫn hoặc mắc bẫy những kẻ tấn công. 

Bài báo lập luận rằng việc triển khai tĩnh các tài nguyên đánh lừa là không hiệu quả và các phương pháp triển khai động hiện có là quá lý tưởng/xa vời để có thể hiện thực. 

Bài báo phát triển một phương pháp sử dụng phương pháp học tăng cường, một loại máy học học hỏi từ quá trình thử và sai, để triển khai linh hoạt các tài nguyên đánh lừa dựa trên trạng thái an ninh mạng và chiến lược của kẻ tấn công. 

Bài báo sử dụng biểu đồ thâm nhập mối đe dọa để sàng lọc các vị trí triển khai có thể và thuật toán Q-Learning để tìm ra chính sách tối ưu. 

Bài báo đánh giá phương pháp này trên môi trường mạng trong thế giới thực và cho thấy rằng nó có xác suất phòng thủ thành công cao gần 80%, tốt hơn so với các phương án hiện có.

# Introduction
Bài báo bắt đầu bằng cách nêu vấn đề về mối đe dọa liên tục nâng cao (Advanced Persistent Threat - APT), đây là một kiểu tấn công lén lút và tinh vi có thể vượt qua các biện pháp phòng thủ truyền thống và gây rủi ro đáng kể cho an ninh mạng. 

Sau đó, bài viết giới thiệu khái niệm phòng thủ mạng dựa trên lừa dối (deception-based cyber defenses - DCD), là các phương pháp tạo và triển khai lừa đảo trong mạng mục tiêu để đánh lạc hướng những kẻ tấn công và cung cấp cho chúng thông tin sai lệch. 

Bài báo so sánh DCD với hệ thống phòng thủ mục tiêu di động (moving target defense - MTD), đây là một khái niệm phòng thủ nâng cao khác tập trung vào việc thay đổi bề mặt tấn công của hệ thống một cách liên tục. Bài báo cho rằng DCD có mục tiêu xa hơn MTD và được coi là thời kỳ hậu MTD. 

Bài báo cũng đề cập đến cuốn sách đầu tiên dành riêng cho nghiên cứu về DCD, có tên là “Cyber Deception”. Sau đó, bài báo xem xét một số tài nguyên đánh lừa hiện có có thể được sử dụng để triển khai DCD, chẳng hạn như honeypots, honey-words, honey-patches và những tài nguyên khác. 

Honeypots là hệ thống hoặc thiết bị giả mạo bắt chước hệ thống hoặc thiết bị thật và thu hút sự chú ý của kẻ tấn công. Bài viết phân loại honeypots thành ba loại dựa trên mức độ tương tác và chức năng của chúng: honeypots tương tác thấp, honeypots tương tác trung bình và honeypots tương tác cao. Bài báo cũng đưa ra một số ví dụ về honeypots cho các giao thức và thiết bị khác nhau, chẳng hạn như Telnet, HTTP, điện thoại thông minh, thiết bị USB và thiết bị thu thập dữ liệu. Honey-words là mật khẩu giả được lưu trữ cùng với mật khẩu thật để phát hiện những kẻ tấn công cố gắng bẻ khóa chúng. Honey-patches là các bản vá lỗ hổng giả mạo được phát hành để lừa những kẻ tấn công khai thác chúng. Bài báo cũng đề cập đến một số dạng tài nguyên lừa đảo khác liên quan đến thiết bị IoT, địa chỉ URL và các biện pháp mã hóa. 

Bài báo nói rằng bất kỳ thứ gì mà kẻ tấn công quan tâm đều có thể bị giả mạo làm tài nguyên đánh lừa. 

Bài viết nhằm trình bày những nghiên cứu mới nhất về DCD và các ứng dụng của nó trong các lĩnh vực khác nhau.

Bài báo tiếp tục bằng cách nêu vấn đề nghiên cứu về cách triển khai các tài nguyên đánh lừa một cách hiệu quả, đây cũng là một kỹ thuật hỗ trợ quan trọng cho DCD. 

Bài báo lập luận rằng hầu hết các phương pháp triển khai hiện có là tĩnh - static, nghĩa là chúng không coi trạng thái của kẻ tấn công (ý định, khả năng và chiến lược) là một biến số có thể thay đổi theo thời gian. Bài viết xem xét một số phương pháp triển khai tĩnh sử dụng lý thuyết đồ thị, lý thuyết trò chơi hoặc công nghệ mạng được xác định bằng phần mềm (SDN) để mô hình hóa hành vi của kẻ tấn công, thiết kế chuỗi hoặc cụm mồi nhử hoặc thay đổi địa chỉ IP của tài nguyên lừa đảo. Tuy nhiên, bài báo chỉ trích những phương pháp này là quá lý tưởng hoặc không hiệu quả, bởi vì chúng cố gắng ngăn chặn những kẻ tấn công khám phá ra các tài nguyên lừa đảo hơn là chủ động dụ dỗ kẻ tấn công, hoặc chúng đưa ra nhiều giả định và ràng buộc nghiêm ngặt về chiến lược của kẻ tấn công mà không thể thỏa mãn trong thực tế. 

Sau đó, bài báo giới thiệu học tăng cường (RL) như một kỹ thuật trí tuệ nhân tạo (AI) đầy hứa hẹn có thể tự động điều chỉnh vị trí của các tài nguyên đánh lừa theo trạng thái an ninh mạng và bẫy kẻ tấn công với xác suất cao. RL là một kỹ thuật cho phép một tác nhân học hỏi từ các hành động và phần thưởng của chính nó trong một môi trường không chắc chắn và đã được áp dụng thành công cho nhiều lĩnh vực, chẳng hạn như rô-bốt, lái xe tự động và trò chơi trên bàn cờ. 

Bài báo tuyên bố rằng phương pháp của họ là phương pháp đầu tiên không dựa trên các giả định và ràng buộc nghiêm ngặt về chiến lược của kẻ tấn công và đạt được các thuộc tính thỏa đáng. Bài viết cũng so sánh phương pháp của họ với các phương pháp dựa trên RL khác để bảo mật mạng và nêu bật những ưu điểm và đóng góp của họ.