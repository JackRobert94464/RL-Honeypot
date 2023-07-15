# Structure
Bài viết được chia thành sáu phần. 

Phần đầu tiên là phần giới thiệu, trong đó đưa ra nền tảng, động lực và ý tưởng chính của bài báo. 

Phần thứ hai là phần đặt vấn đề, trong đó các định nghĩa, giả định và mục tiêu của vấn đề triển khai tài nguyên đánh lừa được giải thích. 

Phần thứ ba là sàng lọc sơ bộ, trong đó một phương pháp dựa trên TPG được đề xuất để lọc ra các vị trí triển khai tài nguyên lừa đảo không hiệu quả. 

Phần thứ tư là chính sách triển khai thông minh, trong đó một phương pháp dựa trên RL được đề xuất để tự động điều chỉnh vị trí của các tài nguyên đánh lừa theo trạng thái an ninh mạng. 

Phần thứ năm là các thử nghiệm, trong đó hiệu suất và hiệu quả của các phương pháp được đề xuất được đánh giá và so sánh với các phương pháp khác. 

Phần thứ sáu là phần kết luận, trong đó tóm tắt những phát hiện chính, đóng góp và công việc trong tương lai của bài báo.

# Abstract
Đoạn văn nói về một bài báo nghiên cứu đề xuất một chính sách triển khai thông minh cho các tài nguyên đánh lừa trong mạng. 

Tài nguyên lừa đảo là tài sản giả mạo hoặc gây hiểu lầm => có thể gây nhầm lẫn hoặc mắc bẫy những kẻ tấn công. 

Bài báo lập luận rằng việc triển khai tĩnh các tài nguyên đánh lừa là không hiệu quả và các phương pháp triển khai động hiện có là quá lý tưởng/xa vời để có thể hiện thực. 

Bài báo phát triển một phương pháp sử dụng phương pháp học tăng cường, một loại máy học học hỏi từ quá trình thử và sai, để triển khai linh hoạt các tài nguyên đánh lừa dựa trên trạng thái an ninh mạng và chiến lược của kẻ tấn công. 

Bài báo sử dụng biểu đồ thâm nhập mối đe dọa để sàng lọc các vị trí triển khai có thể và thuật toán Q-Learning để tìm ra chính sách tối ưu. 

Bài báo đánh giá phương pháp này trên môi trường mạng trong thế giới thực và cho thấy rằng nó có xác suất phòng thủ thành công cao gần 80%, tốt hơn so với các phương án hiện có.

# I - Introduction
Bài báo bắt đầu bằng cách nêu vấn đề về mối đe dọa liên tục nâng cao (Advanced Persistent Threat - APT), đây là một kiểu tấn công lén lút và tinh vi có thể vượt qua các biện pháp phòng thủ truyền thống và gây rủi ro đáng kể cho an ninh mạng. 

Sau đó, bài viết giới thiệu khái niệm phòng thủ mạng dựa trên lừa dối (deception-based cyber defenses - DCD), là các phương pháp tạo và triển khai lừa đảo trong mạng mục tiêu để đánh lạc hướng những kẻ tấn công và cung cấp cho chúng thông tin sai lệch. 

Bài báo so sánh DCD với hệ thống phòng thủ mục tiêu di động (moving target defense - MTD), đây là một khái niệm phòng thủ nâng cao khác tập trung vào việc thay đổi bề mặt tấn công của hệ thống một cách liên tục => tăng độ khó cho việc xác định môi trường cần tấn công là gì. Bài báo cho rằng DCD có mục tiêu xa hơn MTD và được coi là thời kỳ hậu MTD. 

Bài báo cũng đề cập đến cuốn sách đầu tiên dành riêng cho nghiên cứu về DCD, có tên là “Cyber Deception”. Sau đó, bài báo xem xét một số tài nguyên đánh lừa hiện có có thể được sử dụng để triển khai DCD, chẳng hạn như honeypots, honey-words, honey-patches và những tài nguyên khác. 

Honeypots là hệ thống hoặc thiết bị giả mạo bắt chước hệ thống hoặc thiết bị thật và thu hút sự chú ý của kẻ tấn công. Bài viết phân loại honeypots thành ba loại dựa trên mức độ tương tác và chức năng của chúng: honeypots tương tác thấp, honeypots tương tác trung bình và honeypots tương tác cao. Bài báo cũng đưa ra một số ví dụ về honeypots cho các giao thức và thiết bị khác nhau, chẳng hạn như Telnet, HTTP, điện thoại thông minh, thiết bị USB và thiết bị thu thập dữ liệu. Honey-words là mật khẩu giả được lưu trữ cùng với mật khẩu thật để phát hiện những kẻ tấn công cố gắng bẻ khóa chúng. Honey-patches là các bản vá lỗ hổng giả mạo được phát hành để lừa những kẻ tấn công khai thác chúng. Bài báo cũng đề cập đến một số dạng tài nguyên lừa đảo khác liên quan đến thiết bị IoT, địa chỉ URL và các biện pháp mã hóa. 

Bài báo nói rằng bất kỳ thứ gì mà kẻ tấn công quan tâm đều có thể bị giả mạo làm tài nguyên đánh lừa. 

Bài viết nhằm trình bày những nghiên cứu mới nhất về DCD và các ứng dụng của nó trong các lĩnh vực khác nhau.

Bài báo tiếp tục bằng cách nêu vấn đề nghiên cứu về cách triển khai các tài nguyên đánh lừa một cách hiệu quả, đây cũng là một kỹ thuật hỗ trợ quan trọng cho DCD. 

Bài báo lập luận rằng hầu hết các phương pháp triển khai hiện có là tĩnh - static, nghĩa là chúng không coi trạng thái của kẻ tấn công (ý định, khả năng và chiến lược) là một biến số có thể thay đổi theo thời gian. Bài viết xem xét một số phương pháp triển khai tĩnh sử dụng lý thuyết đồ thị, lý thuyết trò chơi hoặc công nghệ mạng được xác định bằng phần mềm (SDN) để mô hình hóa hành vi của kẻ tấn công, thiết kế chuỗi hoặc cụm mồi nhử hoặc thay đổi địa chỉ IP của tài nguyên lừa đảo. Tuy nhiên, bài báo chỉ trích những phương pháp này là quá lý tưởng hoặc không hiệu quả, bởi vì chúng cố gắng ngăn chặn những kẻ tấn công khám phá ra các tài nguyên lừa đảo hơn là chủ động dụ dỗ kẻ tấn công, hoặc chúng đưa ra nhiều giả định và ràng buộc nghiêm ngặt về chiến lược của kẻ tấn công mà không thể thỏa mãn trong thực tế. 

Sau đó, bài báo giới thiệu học tăng cường (RL) như một kỹ thuật trí tuệ nhân tạo (AI) đầy hứa hẹn có thể tự động điều chỉnh vị trí của các tài nguyên đánh lừa theo trạng thái an ninh mạng và bẫy kẻ tấn công với xác suất cao. RL là một kỹ thuật cho phép một tác nhân học hỏi từ các hành động và phần thưởng của chính nó trong một môi trường không chắc chắn và đã được áp dụng thành công cho nhiều lĩnh vực, chẳng hạn như rô-bốt, lái xe tự động và trò chơi trên bàn cờ. 

Bài báo tuyên bố rằng phương pháp của họ là phương pháp đầu tiên không dựa trên các giả định và ràng buộc nghiêm ngặt về chiến lược của kẻ tấn công và đạt được các thuộc tính thỏa đáng. Bài viết cũng so sánh phương pháp của họ với các phương pháp dựa trên RL khác để bảo mật mạng và nêu bật những ưu điểm và đóng góp của họ.

# II - PROBLEM SETTING OF DECEPTION RESOURCES DEPLOYMENT
Xác định vấn đề: cài đặt vấn đề triển khai tài nguyên lừa dối.

Một trong hai yếu tố chính quyết định sự thành công của DCD là độ trung thực của các tài nguyên đánh lừa, điều này đề cập đến mức độ thực tế và thuyết phục của chúng đối với kẻ tấn công. Yếu tố khác là chính sách triển khai tài nguyên lừa dối - làm sao cho kẻ tấn công có thể bị dụ vào tài nguyên lừa dối với xác suất cao.

Phần này đưa ra một giả định đơn giản hóa rằng các tài nguyên đánh lừa có độ trung thực cao, có nghĩa là chúng có thể bắt chước hoàn hảo các tài nguyên thực và đánh lừa kẻ tấn công tin vào chúng. 

Sau đó, phần này mô tả kịch bản kẻ tấn công-người bảo vệ, bao gồm một mạng mục tiêu chứa cả tài nguyên thực và tài nguyên đánh lừa, kẻ tấn công cố gắng xâm nhập mạng và tìm tài nguyên thực, và một người bảo vệ cố gắng bảo vệ mạng và dụ kẻ tấn công vào tài nguyên lừa dối. 

Phần này cũng giải thích chiến lược của kẻ tấn công, chiến lược này dựa trên kiến thức của anh ta/cô ta về cấu trúc liên kết mạng, vị trí của các tài nguyên đánh lừa, phần thưởng và chi phí của mỗi hành động. Phần này nói rằng vấn đề triển khai tài nguyên đánh lừa là tìm ra một chính sách có thể tự động điều chỉnh vị trí của tài nguyên đánh lừa theo trạng thái an ninh mạng và bẫy kẻ tấn công với xác suất cao. 

Phần này cũng xác định một số ký hiệu và công thức để hình thức hóa vấn đề về mặt toán học.

## A - ATTACKER-DEFENDER SCENARIO
Phần này giới thiệu kịch bản kẻ tấn công-người bảo vệ (ADS), dựa trên ý tưởng về DCD và bao gồm ba thành phần: mạng đích (target network), kẻ tấn công (attacker) và người bảo vệ (defender). 

Hình minh họa các thành phần của ADS. 

![Alt text](image.png)

Phần này xác định mạng mục tiêu là một bộ tuple bốn thành phần (N, E, ncr, Nfr) bao gồm: 
- các node thông thường N = {n1, n2, ..., nk}, 
- các cạnh E c N * N (E tập con của N*N), 
- node chứa tài nguyên bí mật duy nhất ncr (ncr thuộc N),
- các node tài nguyên lừa dối Nfr (Nifr | i = 1, 2, ..., m).

Phần này giải thích rằng: 
- các node thông thường là các hệ thống hoặc thiết bị thực trong mạng, 
- các cạnh là kết nối giữa các node, 
- node tài nguyên bí mật là node duy nhất chứa dữ liệu hoặc tệp thực mà kẻ tấn công muốn lấy 
- các node tài nguyên lừa đảo là hệ thống hoặc thiết bị giả mạo chứa dữ liệu hoặc tệp giả mạo mà kẻ bảo vệ muốn dụ kẻ tấn công vào. 

Phần này cũng giải thích rằng nếu có một cạnh từ node này sang node khác (tồn tại một cạnh eij thuộc E nối node ni với node nj bất kì), điều đó có nghĩa là người dùng có thể truy cập node thứ hai từ node đầu tiên (dạng nó có thể SSH qua ấy). 

Phần giả định rằng mục tiêu của kẻ tấn công là tìm và truy cập node tài nguyên bí mật ncr trong mạng đích.

Phần này giải thích rằng có một số node trong mạng mục tiêu được gọi là “đối diện bên ngoài” (external facing), có nghĩa là kẻ tấn công ngoài internet có thể truy cập chúng. Trong sơ đồ minh họa, node n1 là node “hướng ra bên ngoài”. 

Kẻ tấn công bắt đầu cuộc tấn công bằng cách xâm nhập và kiểm soát các node “đối diện bên ngoài” bằng cách khai thác lỗ hổng trong code chạy trên mấy node này, sau đó anh ta/cô ta cố gắng xâm phạm thêm một số node khác trong mạng mục tiêu. 

Một cuộc tấn công thành công vào một node ni yêu cầu hai điều kiện: 
i) kẻ tấn công có quyền truy cập vào node đó
ii) có một số lỗ hổng có thể khai thác trên node. 

Lưu ý rằng kẻ tấn công không biết nơi cài đặt tài nguyên bí mật, vì vậy anh ta/cô ta phải tiếp tục xâm nhập cho đến khi tìm thấy node tài nguyên bí mật hoặc rơi vào node tài nguyên lừa đảo. 

Phần này định nghĩa Aa(ni) là một hành động tấn công, có nghĩa là kẻ tấn công xâm chiếm node ni.

Hành động triển khai tài nguyên đánh lừa Ad, đây là kỹ thuật chính của người phòng thủ trong ADS. 

Các tài nguyên đánh lừa là các hệ thống hoặc thiết bị giả mạo mà kẻ tấn công tạo ra và triển khai trong mạng mục tiêu để thu hút và đánh lừa kẻ tấn công. Các tài nguyên đánh lừa giống như nút tài nguyên bí mật, ngoại trừ việc chúng chứa dữ liệu hoặc tệp giả thay vì tệp thực. 

Việc tạo và duy trì các tài nguyên đánh lừa rất tốn kém, vì vậy số lượng tài nguyên đánh lừa thường nhỏ. 

Kẻ tấn công không thể biết sự khác biệt giữa tài nguyên bí mật và tài nguyên giả mạo. 

Hành động triển khai tài nguyên đánh lừa Ad dưới dạng ánh xạ từ tập hợp các nút tài nguyên đánh lừa Nfr sang tập hợp các nút bình thường N. Đối với mỗi nút tài nguyên đánh lừa nifr trong Nfr, có một nút bình thường tương ứng nj trong N thỏa mãn Ad(nifr) = nj, nghĩa là người phòng thủ tạo kết nối từ nj đến nifr. 

Khi Ad(nifr) = nj, điều đó có nghĩa là người phòng thủ triển khai nifr phía sau nj hoặc vị trí triển khai của nifr là nj. Trong trường hợp này, kẻ tấn công có thể truy cập nifr từ nj, và do đó, nếu kẻ tấn công xâm nhập và kiểm soát nj, anh ta/cô ta có thể tấn công nifr trong bước tiếp theo. 

Hình minh họa ba loại mối quan hệ ánh xạ có thể có từ Nfr đến N: một-một, một-nhiều và nhiều-một.

![Alt text](image-1.png)

