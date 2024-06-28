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

----------------------------------------------


%-[Phần mở đầu chương
\chapter[CƠ SỞ LÝ THUYẾT]{CƠ SỞ LÝ THUYẾT} \label{chchukytapthedathanhphan}%
%\minitoc %
%\setcounter{baitap}{0}
%\thispagestyle{empty}
%\vspace*{1cm}
%]-

 
Chương này trình bày cơ sở lý thuyết của nghiên cứu: Bao gồm mã độc, các kỹ thuật phân tích mã độc, mô hình phát hiện mã độc, và mô hình học tăng cường.


\section{Mã độc}
\subsection{Cấu trúc tệp thực thi}
Trong nghiên cứu này chúng tôi chỉ chọn tệp thực thi của Windows làm mẫu đối tượng.

Định dạng tập tin PE, viết tắt của Portable Executable, là một định dạng tập tin cho các tập tin .EXE, .DLL, mã đối tượng (Object Code) trong hệ điều hành Windows (cho cả hai phiên bản x86 và x64). Định dạng này là một cấu trúc dữ liệu cung các thông tin cần thiết để bộ nạp của hệ điều hành Window có thể quản lý và thực thi được các lệnh được định nghĩa trong tập tin. Định dạng này được phát triển dựa trên định dạng UNIX COFF. Vào thời điểm hiện tại, phần mở rộng của tập tin PE có các dạng như sau: .EXE, .DLL, .SRC, .BPL, .DPL, .CPL, .OCX, .ACM, .AX.
Định dạng tập tin PE có các vai trò cơ bản sau:
\begin{itemize}
\item \textbf{Cung cấp dữ liệu để tải chương trình lên bộ nhớ:} Định dạng PE mô tả đoạn mã cần được tải lên bộ nhớ và nơi chúng cần được lưu trữ, cách thức khởi tạo và thư viện cần được tham chiếu tới.
\item \textbf{Cung cấp tài nguyên mà chương trình có thể sử dụng trong quá trình thực thi:} Các tài nguyên bao gồm hình ảnh, đoạn phim, chuỗi ký tự, ...
\item \textbf{Cung cấp cơ chế bảo mật:} Tập tin PE sử dụng các dữ liệu bảo mật như là một chữ ký số để đảm bảo rằng hệ điều hành có khả năng xác thực nguồn gốc của chương trình được nạp.
\end{itemize}
Cấu trúc chung của định dạng tập tin PE thường sẽ có 2 phân đoạn, phân đoạn thứ nhất là cho đoạn mã và phân đoạn thứ hai là cho dữ liệu.
\begin{figure}[htp]
    \centering
    \includegraphics[width=5cm]{Images/PE-file-structure.png}
    \caption{Cấu trúc định dạng tập tin PE}
    \label{fig:reinforcement learning}
\end{figure}
\subsubsection{Trường tiêu đề DOS (DOS Header)}
Trường này được thực thi bất cứ khi nào tập tin chạy trong môi trường MS-DOS, mục tiêu của nó là để thông báo tập tin này không thể hoạt động trong môi trường trên. Chi tiết hơn, trường tiêu đề DOS chiếm 64 bytes đầu tiên trong tập tin chứa 2 giá trị quan trọng là e\textunderscore magic (0x5a4b) và e\textunderscore lfanew là một DWORD (4bytes), giá trị nằm trong 4 bytes này chứa khoảng cách (offset) đến Trường tiêu đề tập tin PE.

\subsubsection{Trường tiêu đề PE (PE Header)}
Trường tiêu đề PE bao gồm các thông tin cần thiết để tải chương trình lên bộ nhớ. Cấu trúc của phần này bao gồm 3 phần chính:
\begin{itemize}
\item \textbf{Signature:} là 1 DWORD bắt đầu trường tiêu đề PE chứa chữ ký PE: 50h, 45h, 00h, 00h
\item \textbf{Trường tiêu đề tập tin:} bao gồm 20 bytes tiếp theo của Trường tiêu đề PE, phần này chứa thông tin về sơ đồ bố trí vật lý và các đặc tính của tập tin. Trong trường này chúng ta cần chú ý tới trường NumberOfSections , đây là trường chứa số section của file. Nếu muốn thêm/xoá đoạn trong tập tin PE, ta cần thay đổi tương ứng trường này.
\item \textbf{Trường tiêu đề tùy chọn:} bao gồm 224 bytes tiếp theo sau Trường tiêu đề Tập tin. Cấu trúc này được định nghĩa trong windows.inc, đây là phần chứa thông tin về sơ đồ luận lý trong tập tin PE.
\end{itemize}
\subsubsection{Phân đoạn bảng (Section Table)}
Section Table là thành phần kế tiếp ngay sau Trường tiêu đề PE, chứa một mảng các cấu trúc IMAGE\textunderscore SECTION\textunderscore HEADER, mỗi phần từ sẽ chứa thông tin về một phân đoạn trong tập tin PE
Một số phân từ quan trọng như:
\begin{itemize}
\item \textbf{Kích thước ảo (VirtualSize):} Kích thước thật của phân đoạn sau khi được nạp vào bộ nhớ, được tính theo byte và giá trị này có thể nhỏ hơn kích thước trên ổ đĩa.
\item \textbf{Địa chỉ ảo (VirtualAddress):} Giá trị để ánh xạ các phân đoạn khi được tải lên bộ nhớ
\item \textbf{Kích thước của dữ liệu nguyên bản (SizeOfRawSection):} Kích thước phân đoạn dữ liệu trên đĩa.
\item \textbf{Con trỏ của dữ liệu nguyên bản (PointerOfRawSection):} là khoảng cách từ vị trí đầu tập tin cho tới phân đoạn dữ liệu.
\item \textbf{Đặc tính (Characteristic):}  chứa các cờ như cờ thực thi (excutable code), dữ liệu khởi tạo (initialized data), ...
\end{itemize}

\subsubsection{Phân đoạn tập tin PE (Section PE File)}
Là những phân đoạn chứa nội dung chính của tập tin, bao gồm các đoạn mã, dữ liệu, tài nguyên và các thông tin khác của tập tin thực thi. Mỗi phân đoạn có một trường tiêu đề và một dữ liệu nguyên bản (dữ liệu chưa được xử lý). Những phân đoạn trường tiêu đề được chứa trong phân đoạn bảng.
Một chương trình cơ bản trên hệ điều hành Windows sẽ bao gồm:

\begin{itemize}
\item Phân đoạn mã thực thi là các đoạn mã tập trung vào một phân đoạn đơn lẻ .text hoặc mã.
\item Phân đoạn dữ liệu (.rdata) biểu diễn dữ liệu với quyền đọc là các chuỗi , giá trị hằng, thông tin, ... tất cả các biến khác ngoài biến tự động mà chỉ xuất hiện trong ngăn xếp (stack) cũng được lưu trữ trong phân đoạn này.
\item Phân đoạn tài nguyên (.rsrc) chứa thông tin tài nguyên cho một mô-đun, 16 byte đầu tiên gồm một trường tiêu đề giống như các phân đoạn khác, nhưng dữ liệu của phân đoạn này được cấu  trúc vào trong một cây tài nguyên và được quna sat bằng trình biên soạn tài nguyên
\item Phân đoạn xuất dữ liệu (.edata) chứa các thư mục xuất (Export Directory) cho mọt chươn trình ứng dụng hoặc một tập tin .DLL. Khi biểu diễn, phân đoạn này bao gồm các thông tin và địa chỉ của những hàm có chức năng xuất.
\item Phân đoạn nhập dữ liệu (.idata) chứa những thông tin khác nhau về thư mục nhập (Import Directory) và bảng địa chỉ nhập (Import Address Table).
\end{itemize}

\subsection{Hợp ngữ}
Hợp ngữ thuộc loại ngôn ngữ bậc thấp được thiết kế cho từng họ bộ xử lý, được sử dụng để tương tác gần nhất với máy tính. Mỗi dòng lệnh của hợp ngữ gần như tương đương với một lệnh chỉ dẫn của bộ xử lý. Với ngôn ngữ này, ta có thể sử dụng các công cụ để dịch ngược mã độc thành hợp ngữ để dễ dàng hơn trong việc phân tích và điều tra.
Thông thường, khi được biên dịch thành hợp ngữ, các chương trình độc hại sử dụng các lệnh để tương tác với hệ điều thông qua việc gọi các thư viện liên kết động (DLL), nhứng thứ được tải lên bộ nhớ tại thời điểm hoạt động. Mã độc thường sử dụng DLL để thực hiện các tác vụ như thay đổi thanh ghi của hệ thống, di chuyển hoặc sao chép tập tin, tạo liên kết hoặc kết nối với máy chủ, vùng mạng khác thông qua các giao thức mạng khác nhau, vân vân.
Các trình phát hiện mã độc thường dựa vào các đặc điểm về cấu trúc tập tin hoặc hành vi khi thực thi để xác định tập tin độc hại. Để vượt mặt các trình này, một vài kỹ thuật trên hợp ngữ được áp dụng nhằm làm biến đổi hình dạng, trạng thái của mã độc như:
\begin{itemize}
\item Chèn mã chết (Dead-code insertion)
\item Tái khai báo thanh ghi (Register Reassignment)
\item Tái sắp xếp chương trình con (Subroutine Reordering)
\item Thay thế lệnh (Instruction Subtitution)
\item Chuyển vị mã (Code Transposition)
\item Tích hợp mã (Code Integration)
\end{itemize}

Việc phân tích hợp ngữ giúp chúng tôi hiểu rõ hơn cơ chế phát hiện mã độc của các trình phát hiện hiện tại. Bởi ngoài thuộc tính liên quan đến tệp thực thi, các trình phát hiện còn tập trung phân tích theo mẫu hợp ngữ.

\section{Mô hình phát hiện mã độc}
Mục đích của phát hiện mã độc là đưa ra những cảnh báo sớm để có cơ chế ngăn chặn kịp thời trước khi các tập tin mã độc thực thi và gây ra các tổn hại tới hệ thống. Vì thế, vai trò của phát hiện mã độc là rất quan trọng trong việc giảm thiểu thiệt hại hoặc ngăn chặn các tập tin này kịp thời.

\subsection{Phương pháp phân tích tĩnh}
Kỹ thuật phát hiện mã độc dựa trên phương pháp phân tích tĩnh có đặc điểm là phát hiện mã độc mà không cần phải chạy hay thực thi bất kỳ đoạn mã nào của nó gồm có 3 phường pháp chính là kỹ thuật dò quét, chuẩn đoán dựa trên kinh nghiệm và kiểm tra tính tóàn vẹn.

\subsubsection{Kỹ thuật dò quét}
Thông thường mỗi một mã độc được biểu diễn bởi một hay nhiều mẫu, hoặc là các dấu hiệu, chuỗi tuần tự các byte là đặc trưng được coi là duy nhất của mã độc. Các dấu hiệu này có thể là chuỗi hoặc không cần bất kỳ ràng buộc về chuỗi nào. Một vài chương trình phát hiện mã độc hỗ trợ việc sử dụng các ký tự đại diện cho mõi một byte tùy ý, một phần của byte, hoặc không hay nhiều byte. Cụ thể hơn, quá trình phát hiện được thụ hiện thông qua một dòng các mã byte, chúng có thể là toàn bộ nội dung của một khối khởi tạo, toàn bộ nội dung của tập tin, hoặc là một phần của tập tin được đọc hoặc ghi, hay cũng có thể là các gói tin mạng.
Với hàng trăm ngàn dấu hiệu để phát hiện, việc tìm kiếm chúng tại một thời điểm trở nên bất khả thi. Một trong những thách thức lớn nhất của kỹ thuật này là tìm ra các thuật toán có khả năng quét nhiều mẫu một cách hiệu quả và đồng thời có khả năng phân tích, đánh giá chúng.

\subsubsection{Kỹ thuật Tìm kiếm tĩnh (Static Heuristic)}
Với mục đích tận dụng khả năng và kinh nghiệm chuẩn đoán của các chuyên gia mã độc, kỹ thuật này được áp dụng nhằm tăng khả năng tìm thấy các loại mã độc đã biết hoặc các biến thể dựa trên những mẩu đặc điểm chung. Kỹ thuật này thực hiện 2 bước chính, thu thập dữ liệu và phân tích dữ liệu.
Kỹ thuật Static Heuristic được ứng dụng để giảm tài nguyên cần có cho quá trình quét. Dữ liệu về mã độc được lưu trong cơ sở dữ liệu được chọn lựa và giảm thành tập dữ liệu nhỏ hơn và gần với mục tiêu hơn.

\subsubsection{Kỹ thuật kiểm tra tính toàn vẹn}
Kỹ thuật kiểm tra tính toàn vẹn được ứng dụng với mục đích khai thác các hành vi thay đổi nội dung tập tin thực thi. Việc kiểm tra toàn vẹn được khởi tạo với việc tính và lưu chỉ số tổng kiểm tra (checksum) cho mỗi tập tin. Sau khi tập tin được vận chuyển hoặc trao đổi giữa các máy hoặc người dùng, nó tập tính lại chỉ số trên và so sánh với giá trị được lưu trữ. Trong trường hợp hai chỉ này khác nhau, trình kiểm tra có thể kết luận tập tin đã bị thay đổi và cảnh báo cho người dùng.
Kỹ thuật này được sử dụng phổ biến cùng với các hàm băm như MD5, SHA, CRC, … để tính toán giá trị tổng kiểm tra thông qua việc băm toàn bộ nội dung của tập tin.

\subsection{Phương pháp phân tích động}
Kỹ thuật phân tích động là một kỹ thuật phát hiện mã độc dựa trên các hành vi của tập tin được thực thi trong thời gian thực. Trình chống mã độc thực hiện việc giám sát các hành động, khối lệnh của tập tin này. Để thực hiện kỹ thuật này, hệ thống nên được thiết lập môi trường thử nghiệm để thực thi mã độc và theo dõi hành vi của chúng trên môi trường này. Các hành động đáng chú ý như: hoạt động của các tiến trình, thông tin về thanh ghi, sự thay đổi của các tập tin, thư mục, lưu lượng mạng và các kết nối. Tất cả các hành vi của mã độc sẽ được lưu dưới dạng các nhật ký phục vụ cộng việc phân tích và điều tra về sau.

\subsubsection{Kỹ thuật Giám sát hành vi (Behavior Monitors)}
Giám sát hành vi là kỹ thuật giám sát các hành vi thực thi của một chương trình trong thời gian thực, theo dõi các hành động, khối lệnh khả nghi của nó. Nếu những hành động này được tìm thấy, trình phát hiện mã độc có thể ngăn chặn những hành động khả nghi thành công và chấm dứt các tiến trình của chúng hoặc cảnh báo cho người dùng. Về bản chất, một trình giám sát hành vi xem xét hành động của các chương trình khả nghi có phải là bất thường hay không, ví dụ như các hành vi liên quan tới mở, sửa đổi hay xóa tập tin, những thao tác định dạng ổ đĩa phân vùng, thay đổi thanh nhớ, kết nối mạng, mở cổng đặc biệt, vân vân. 

\subsubsection{Kỹ thuật giả lập (Emulation)}
Kỹ thuật giả lập cho phép các chương trình thực thi và phân tích trong môi trường mô phỏng được thiết lập sẵn. Với mục tiêu rằng khi được thực thi như thông thường thì mã độc sẽ để lộ các đặc tính và hành vi nguy hại, từ đó cho phép trình chống mã độc dễ dàng phát hiện.
Có 2 phương pháp chính để áp dụng kỹ thuật này là:
\begin{itemize}
\item Tìm kiếm động (Dynamic Heuristic): Đây là kỹ thuật có độ chính xác tương tự kỹ thuật Tìm kiếm tĩnh. Các dữ liệu mà kỹ thuật này thu thập chính là các thông tin từ môi trường giả lập về các hành vi của chương trình khả nghi.
\item Giải mã chung (Generic Decryption): Với những mã độc đa hình, vòng giải mã có thể là một yếu tố gây ra khó khăn cho các phần mềm diệt mã độc để phát hiện được chúng. Mã độc được thiết kế để thực thi các hành vi tấn công trong trường hợp bình thường và được mã hóa, chính vì thế, trình chống mã độc có khả năng phát hiện được chúng. Khi mã độc giải mã, phần thân của chương trình có thể được phát hiện bằng các phương pháp dò quét thông thường, điều này xác định chính xác khả năng nhận biết các mã độc đa hình, kỹ thuật này sử dụng các kinh nghiệm để xác minh mỗi khi mã độc mã hóa chính nó.
\end{itemize}

\subsection{Mô hình phát hiện mã độc dựa trên học máy}
Trong hai kỹ thuật vừa nêu trên, kỹ thuật phân tích tĩnh và kỹ thuật phân tích động, có thể nhận xét rằng hai kỹ thuật này  đều dựa trên các mẫu mã độc đã xuất hiện hoặc các biến thể để đúc kết và đưa phát các phân tích, khuôn mẫu chung. Chính vì thế, rất khó để một trình chống mã độc có thể nhận diện được các loại mã độc mới chưa từng được ghi nhận, điều này dẫn tới hệ thống có khả năng bị xâm nhập rất cao. Không những thế, việc phân tích mã độc khi chúng xuất hiện và đưa ra giải pháp để khắc tốn một khoảng thời gian không ngắn, dẫn tới nguy cơ lây lan và xâm nhập của mã độc.

Các nghiên cứu về triển khai honeypot sử dụng mô hình học sâu tăng cường đều đã chỉ ra được nhiều khía cạnh trong việc triển khai các mô hình RL khác nhau để phân bổ hợp lí tài nguyên đánh lừa, tuy nhiên, các agent được chọn chưa có được cái nhìn toàn diện về toàn bộ hệ thống mạng mà hầu hết chỉ đưa ra quyết định dựa trên trạng thái hiện tại của hệ thống mạng.

Hiện nay, với sự phát triển của các thuật toán và dữ liệu, học máy đã được ứng dụng trong lĩnh vực phát hiện mã độc với mục đích dự báo được các loại mã độc mới. Mô hình phát hiện mã độc dựa học máy cung cấp khả năng khám phá các khuôn mẫu mã độc một cách tự động dựa trên các dữ liệu được trích xuất. Các thuật toán học máy phổ biến được ứng dụng trong việc phát hiện mã độc có thể kể tới như: Cây quyết định, Máy véc-tơ hỗ trợ (SVM), Naive Bayes, Rừng ngẫu nhiên (Random Forest), Mạng nơ-ron (Neural Networks), K hàng xóm gần nhất (K-Nearest Neighbors), ... Trong phạm vi khóa luận này, chúng tôi sẽ mô tả về hai mô hình học máy được áp dụng chính trong bài là Cây quyết định tăng cường tốc độ (Gradient booosting decision tree - GBDT) và Mạng nơ-ron (Neural Networks).

\subsubsection{Cây quyết định tăng cường tốc độ}
Cây quyết định tăng cường tốc độ là một thuật toán học máy được ứng dụng rộng rãi do hiệu suất, tính chính xác và khả năng diễn giải của nó. Thuật toán này đang tạo ra hiệu suất vượt trội trong một số bài toán học máy như là phân loại nhiêu lớp, hay xếp hạng.

Về bản chất, GBDT là một mô hình tập hợp các cây quyết định, được đào tạo theo trình tự. Trong mỗi lần lặp lại, GBDT học các cây quyết định bằng cách điều chỉnh các trường vô hướng âm (còn được gọi là lỗi dư).
Chi phí chính trong GBDT nằm ở việc học các cây quyết định và phần tốn thời gian nhất trong học cây quyết định là tìm ra các điểm phân tách tốt nhất. Một trong những thuật toán phỏ biến nhất để tìm sự phân chia điểm là thuật được được sắp xếp trước [8, 9], liệt kê tất cả các điểm phân tách có thể có trên các giá trị tính năng. Thuật toán này đơn giản và có thể tìm ra các điểm phân tách tối ưu, tuy nhiên, nó không hiệu quả cả về tốc độ đào tạo và mức tiêu thụ bộ nhớ. Một thuật toán phổ biến khác là biểu đồ thuật toán [10, 11, 12], thay vì tìm các điểm phân tách trên đối tượng địa lý đã sắp xếp giá trị, thuật toán dựa trên biểu đồ tập hợp các giá trị đối tượng địa lý liên tục vào các phần riêng biệt và sử dụng các phần này để xây dựng biểu đồ tính năng trong quá trình đào tạo. Vì thuật toán dựa trên biểu đồ nhiều hơn nên hiệu quả về cả mức tiêu thụ bộ nhớ và tốc độ đào tạo.

\subsubsection{Mạng nơ-ron}
Mạng nơ-ron là một chuỗi những thuật toán được đưa ra để hỗ trợ tìm kiếm những mối quan hệ cơ bản cuảm ột tập hợp dữ liệu dựa vào việc bắt chước cách thức hoạt động từ não bộ con người. Phương pháp này có khả năng thích ứng được với mọi thay đổi từ đầu vào, do vậy, nó có thể đưa ra được mọi kết quả một cách tốt nhất mà không cần thiết kế lại những tiêu chí đầu ra. Với ưu điểm, mạng nơ-ron phù hợp để ứng dụng trong việc phát hiện các loại mã độc mới cũng như sự gia tăng đáng kể của các biến thể mã độc.
Cụ thể hơn, mạng nơ-ron là một kiến trúc nhiều tầng, và thông thường có 3 kiểu tầng chính là:
\begin{itemize}
\item Tầng đầu vào: Là tầng thể hiện cho những đầu vào của mạng.
\item Tầng đầu ra: Là tầng thể hiện cho những đầu ra của mạng.
\item Tầng ẩn: Nằm giữa tầng đầu vào và tầng đầu ra, phụ trách nhiệm vụ suy luận luận lý của mạng.
\end{itemize}
Trong mạng nơ-ron, mỗi nút mạng là một sigmoid nơ-ron nhưng hàm kích hoạt của chúng có thể khác nhau. Tuy nhiên, trong thực tế, các mô hình được thường tùy chỉnh cho chúng cùng dạng với nhau để thuận tiện trong việc tính toán. Ngoài ra, để gia tăng khả năng giải quyết các bài toán phức tạp, mạng nơ-ron sẽ gia tăng số lượng lớp ẩn, tuy nhiên, càng nhiều số lượng lớp ẩn, thời gian thực hiện tính toán sẽ càng lâu hơn. Nếu có nhiều lớp ẩn, số nút trong các lớp đó thường được chọn bằng nhau.


\section{Mô hình học tăng cường}

\subsection{Quy trình quyết định Markov (Markov Decision Process - MDP)}

Hầu hết các bài toán trong học tăng cường được xây dựng trên MDP. MDP gồm bốn thành phần:

\begin{itemize}
\item $S$: Không gian các trạng thái mà tác tử quan sát được khi tương tác với môi trường.
\item $A$: Một tập các hành động mà tác tử có thể thực hiện với môi trường.
\item $P$: Hàm chuyển. Hàm này đưa ra xác suất dự đoán một trạng thái có thể xảy ra, đầu vào của nó là trạng thái hiện tại của môi trường và một hành động.
\item $R$: Một hàm đưa ra phần thưởng. Hàm này sẽ xác định phần thưởng khi môi trường chuyển từ một trạng thái sang trạng thái kế tiếp, dưới tác động của một hành động.
\end{itemize}


Vì vậy, MDP thường được định nghĩa như sau: $M=<S, A, P, R>$

\subsection{Tổng quan mô hình học tăng cường}

Học tăng cường là một nhánh nghiên cứu của học máy, trong đó sẽ có một tác tử đưa ra các hành động để tương tác với một môi trường. Mục tiêu cuối là tối ưu hóa phần thưởng tích lũy đạt được.

Dựa trên MDP, một hệ thống học tăng cường cơ bản sẽ có hai thành phần chính là Tác tử (Agent) và Môi trường (Environment). Kênh giao tiếp của hai thành phần này bao gồm: Hành động (Action), Phần thưởng (Reward), và Trạng thái (State). 

\begin{figure}[htp]
    \centering
    \includegraphics[width=5cm]{Images/Reinforcement-learning-illustration.png}
    \caption{Mô hình học tăng cường}
    \label{fig:reinforcement learning}
\end{figure}

  Tác tử sẽ tương tác với môi trường qua mội chuỗi các lượt đi. Với mỗi lượt $t$, tác tử sẽ chọn một hành động $a_t \in A$, dựa vào một chính sách $\pi(a | s_t)$ và thu về một vectơ trạng thái có thể quan sát được $s_t$ từ môi trường. Môi trường cũng sẽ xuất ra một phần thưởng $r_t \in R$ tương ứng với các hành động nhận vào, đồng thời môi trường cũng thay đổi trạng thái của chính nó, tạo ra một trạng thái mới $s_{t+1}$. Phần thưởng $r_t$ và trạng thái $s_{t+1}$ sẽ là đầu vào kế tiếp của tác tử. Từ đó, tác tử sẽ xây dựng tiếp  chính sách $\pi(a|s_{t+1})$. Tác tử sẽ học dần và tuần tự qua việc khám phá (exploration) và khai thác (exploitation), dần dần chọn ra được hành động nhằm tạo ra trạng thái môi trường mong muốn.

Phần thưởng là yếu tố quan trọng trong việc học và mục tiêu cuối cùng của mô hình học tăng cường là xây dựng được một chính sách để tối đa hóa kì vọng:
\[V^{\pi}(s_t) = E_{a_t}[Q^{\pi}(s_t, a_t)|s_t]\]
với
\[Q^{\pi}(s_t, a_t) = E_{s_{t+1}:\infty, a_{t+1}:\infty}[R_t|s_t,a_t]\]
và
\[R_t = \sum_{i\geq1}\gamma^ir_t+i , \gamma \in [0,1]\]
$\gamma$ là giá tri chiết khấu cho phần thưởng. Giá trị $\gamma$ kiểm soát hành động mới sao cho chúng không được phép tác động nhiều đến phần thưởng nhưng lại quan trọng đối với kết quả $V^\pi$. Hàm đánh giá mức độ hữu ích của một hành động cho một trạng thái được gọi là hàm Q.

\subsection{Q-Learning}

Như đã nêu trên, hệ thống học tăng cường sẽ tối đa hóa $V^\pi$. Điều này đồng nghĩa với việc hệ thống phải tối ưu giá trị Q \cite{watkins1992q} ở mỗi lượt thực hiện hành động. Để lưu lại các thông tin mà tác tử tương tác với môi trường trong mỗi bước, hệ thống học tăng cường sẽ có một bảng chứa: các giá trị của hàm Q, trạng thái và hành động tương ứng. Trong một bài toán nhỏ với môi trường không quá phức tạp, ta có thể xây dựng một bảng ở dạng mảng hai chiều để lưu các giá trị này. Phương pháp này gần giống với quy hoạch động.

\subsection{Deep Q-Learning}

Đối với những không gian 

Một điểm đáng chú ý đối với thuật toán Deep Q-Learning là nó sử dụng hai mạng nơ-ron giống nhau về cấu trúc nhưng khác trọng số cho việc học tập. Cứ sau N bước, thông tin từ mạng nơ-ron chính sẽ được cập nhật sang mạng nơ-ron mục tiêu. Nhờ đó, việc nhiễu loạn thông tin từ kiến thức liên tục cập nhật từ môi trường sẽ được mạng nơ-ron chính khắc phục bằng cách sử dụng mạng mục tiêu như một ví dụ ổn định hơn của chính mình và học theo đó để tự cải thiện trọng số của mình.Việc sử dụng hai mạng nơ-ron như vậy cho phép việc học tập được diễn ra ổn định hơn cũng như tăng hiệu suất học của tác tử. 

\subsection{Mô hình học sâu tăng cường}

Việc lưu trữ giá trị Q ở dạng bảng là một giải pháp đơn giản, nhưng đồng thời nó cũng gây hao tốn tài nguyên rất nhanh chóng, đặc biệt là đối với môi trường sử dụng dữ liệu lớn như hình ảnh. Vì vậy, mô hình học sâu được ứng dụng vào mô hình học tăng cường để giảm thiểu hao tổn tài nguyên. Mô hình kết hợp này được gọi là mô hình học sâu tăng cường \cite{li2017deep}.

Thay vì trực tiếp tính tóan giá trị Q và lưu trữ ở dạng bảng thì một mạng nơ ron với trọng số $\theta$ được dùng để tính toán xấp xỉ các giá trị. Mạng này được huấn luyện để tối thiểu hóa hàm mất mát $L(\theta)$ qua các lượt với phương pháp như SGD (stochastic gradient descent). Kích cỡ của đầu ra của mạng này phải bằng số lượng hành động của tác tử. Hệ thống này tương tự như hệ thống học giám sát, và phần thưởng sẽ tương tự như các nhãn. Mạng nơ ron sẽ học các giá trị như hành động, trạng thái của môi trường và phần thưởng, từ đó nó sẽ dự đoán các phần thưởng cho các giá trị khác để giảm tối thiểu hàm mất mát.

\subsection{Mô hình gym-malware} \label{gym-malware}
Nghiên cứu của chúng tôi phần lớn dựa trên trình tạo đột biến trước đó. Có thể nói, nhóm tác giả Anderson là đại diện tiên phong trong việc tích hợp học tăng cường vào việc tạo mẫu đối kháng. Nhóm này thiết kế một mô hình với tập mười hành động nhằm thay đổi thuộc tính của tệp thực thi. Theo thiết kế, các hành động này sẽ không làm ảnh hưởng tới chức năng của tệp. Tác tử trong mô hình của nhóm được phép chèn tối đa mười hành động. Điều kiện dừng sẽ xảy ra khi chèn hết mười hành động, hoặc khi tệp đã né tránh được trình phát hiện mã độc. Môi trường trong công trình này được thực hiện dựa trên framework OpenAI gym \cite{brockman2016openai}. 

\begin{figure}[htp]
    \centering
    \includegraphics[width=4cm]{Images/Gym-malware-model.png}
    \caption{Mô hình của gym-malware}
    \label{fig:gym-malware}
\end{figure}

Cụ thể các thành phần của hệ thống gym-malware bao gồm:

\subsubsection{Tác tử}

Gym-malware được tạo ra để người dùng có thể linh hoạt chọn lựa các loại thuật toán khác nhau, nhưng nhóm của Anderson lựa chọn thuật toán ACER \cite{wang2016sample}. ACER sử dụng một mạng nơ ron để học chính sách $\pi$ và hàm Q để đưa ra đánh giá về trạng thái-hành động. Sẽ có một vec tơ để lưu các kinh nghiệm học được (experience replay), giúp cho mô hình ACER tối ưu hóa khả năng đánh giá trạng thái-hành động.

\subsubsection{Môi trường và trạng thái}

Môi trường trong mô hình học tăng cường là mẫu mã độc ở dạng mã nhị phân. Tuy nhiên, để xác định chính sách trạng thái của môi trường (và cũng là trạng thái của mẫu mã độc), mã độc dạng nhị phân được trích xuất thuộc tính và lưu ở dạng các vec tơ. Trong thực nghiệm, nhóm Anderson đã xây dựng môi trường với vec tơ thuộc tính 2350 chiều gồm các thành phần của tệp thực thi PE như sau:
 
\begin{itemize}
\item Tiêu đề tệp PE
\item Tiêu đề của các đoạn: đoạn về tên, kích cỡ và tính chất của tệp
\item Bảng nhập, xuất của các hàm
\item Số lượng các chuỗi được lưu trong tệp
\item Thống kê tần suất xuất hiện của các byte
\item Bảng phân phối của các byte
\end{itemize}

Ngoài lưu tệp thực thi ở dạng vec tơ thuộc tính thì môi trường còn chứa một trình phát hiện mã độc để kiểm tra mẫu đối kháng. Cụ thể, gym-malware sẽ sử dụng mô hình LGBM \cite{ke2017lightgbm}  được huấn luyện với tập dữ liệu EMBER.

\subsubsection{Không gian hành động}

Như đã nêu trên, tác tử trong mô hình sẽ thực hiện hành động chèn hoặc thay đổi tính chất của tệp thực thi. Số lượng hành động này được giới hạn để tránh ảnh hưởng tới định dạng của tệp PE và khả năng thực thi của tệp. Không gian hành động bao gồm:

\begin{itemize}
\item \textit{imports\textunderscore append}: Thêm cách hàm vào bảng nhập
\item {section\textunderscore rename}: Thay đổi tên của cách đoạn
\item {section\textunderscore add}: Tạo ra các đoạn mới
\item {section\textunderscore append}: Thêm các byte rác vào sau các đoạn
\item {create\textunderscore new\textunderscore entry}: Tạo điểm đầu (entry point) để thay đổi luồng thực thi
\item {remove\textunderscore signature}: Bỏ thông tin chữ ký trong tệp
\item {remove\textunderscore debug}: Thay đổi thông tin mục sửa lỗi.
\item {upx\textunderscore pack/upx\textunderscore unpack}: Nén hoặc giải nén tệp (sử dụng công cụ upx)
\item {break\textunderscore optional\textunderscore header\textunderscore checksum}: Thay đổi thông tin mã băm
\item {overlay\textunderscore append}: Thêm các byte rác vào đoạn cuối của tệp
\end{itemize}

Các hành động này được cho là có tính chất ngẫu nhiên (stochastic). Ví dụ, với hành động thay đổi tên các đoạn, tác tử sẽ lấy ngẫu nhiên tên từ danh sách các tên thường xuất hiện trong tệp lành tính. Tương tự, khi chèn cách byte rác, tác tử sẽ chọn ngẫu nhiên các byte. 

\subsubsection{Phần thưởng}

Sau khi tác tử chèn xong tệp, tạo được mẫu đối kháng, thì mẫu này sẽ được trình phát hiện LGBM của môi trường tiếp nhận. Dựa vào kết quả của trình phát hiện mà phần thưởng sẽ được tính toán với giá trị như sau: 
\[r \in \{0, R\}\]
\begin{itemize}
\item $r = 0$, khi trình phát hiện nhận thấy mẫu đối kháng là mã độc.
\item $r = R$, khi trình phá hiện nhận thấy mẫu lành tính (vượt mặt thành công). Trong thực nghiệm, nhóm Anderson cho $R= 10$.
\end{itemize}


Chúng tôi có tham khảo các mô hình cải tiến khác như DQEAF của nhóm Fang \cite{fang2019evading} và AIMED-RL của nhóm Labaca-Castro \cite{labaca2021aimed}. Qua các nghiên cứu liên quan này, nhóm nhận thấy cải tiến của các công trình chỉ nhắm vào không gian vector qua việc tăng hoặc hạn chế số lượng hành động của mô hình học tăng cường. Để đánh giá đầy đủ khả năng tạo đột biến của mô hình học tăng cường, chúng tôi chọn gym-malware để làm mô hình chính, với đầy đủ số lượng hành động và thuộc tính của mẫu. 

Cải tiến chính của nhóm nằm ở việc đánh giá khả năng thực thi của mẫu sau khi tác tử thực hiện hành động, được trình bày ở Hình \ref{fig:RL model}. Điểm đánh giá khả năng thực thi sẽ ảnh hưởng đến phần thưởng, vì vậy tác tử sẽ học được hành động nào nên sử dụng và hạn chế sử dụng để không ảnh hưởng khả năng thực thi. 

Đầu tiên tệp mã độc sẽ được trích xuất thuộc tính ở dạng các vec tơ. Bộ vec tơ này đóng vai trò như môi trường (environment) của hệ thống học tăng cường. Tác từ nhận được bộ thuộc vec tơ này và đưa ra các hành động nhằm thay đổi tính chất của thuộc tính. Môi trường tiếp nhận hành động và thay đổi trạng thái. Sau đó, môi trường kiểm tra khả năng thực thi của tệp (functionality test) và kiểm tra xem tệp là độc hại hay lành tính (malware detector). Các kết quả liên quan đến khả năng thực thi và lành tính sẽ làm phần thưởng cho tác tử. Cứ như vậy, qua nhiều lần thực hiện hành động trên các mẫu mã độc khác nhau, mạng nơ ron của tác tử sẽ học dần và dự đoán các hành động hợp lí để tối ưu hóa phần thưởng.


Khả năng của kẻ tấn công đối với trình phát hiện mã độc được phân loại theo năm khía cạnh như sau:
\begin{enumerate}
\item \textbf{Mục đích của kẻ tấn công}: Kẻ tấn công có thể theo đuổi ba hướng (theo mô hình Tính bảo mật - Tính toàn vẹn - Tính sẵn sàng) như sau: 
\begin{itemize}
\item Tính bảo mật (confidentiality): Kẻ tấn công muốn lấy thông tin của mô hình phát hiện mã độc.
\item Tính toàn vẹn (integrity): Kẻ tấn công có thể kiến cho mô hình đưa ra các kết quả sai lệch.
\item Tính sẵn sàng (availability): Kẻ tấn công có thể làm cho mô hình không hoạt động được hoặc làm gián đoạn các chức năng của mô hình.
\end{itemize}
\item \textbf{Kiến thức của kẻ tấn công}: Các phương pháp tấn công sẽ thay đổi tùy vào lượng kiến thức của kẻ tấn công đối với mô hình. Ở đây có ba phương pháp:
\begin{itemize}
\item Tấn công hộp đen (black-box attack)  không yêu cầu kiến thức về trình phát hiện  và chỉ cần khả năng truyền dữ liệu đầu vào (mẫu mã độc) và truy xuất dữ liệu đầu ra (nhãn phân loại).
\item Tấn công hộp xám (gray-box attack) yêu cầu ít kiến thức về trình phát hiện. Kiến thức ở đây có thể bao gồm tập thuộc tính mà mục tiêu sử dụng hoặc  thông số đầu ra cụ thể của mô hình (khác với nhãn đơn thuần).
\item Tấn công hộp trắng (white-box attack) yêu cầu kiến thức về kiến trúc của trình phát hiện (các lớp của mô hình học máy) và các thông số (hyperparameter) mà mô hình được huấn luyện.
\end{itemize}

\item \textbf{Khả năng truy cập dữ liệu huấn luyện}: Kẻ tấn công có thể truy cập dữ liệu huấn luyện của trình phát hiện theo bốn chế độ: 
\begin{itemize}
\item Đọc được dữ liệu được dùng để huấn luyện.
\item Thêm dữ liệu mới vào tập huấn luyện.
\item Thay đổi các mẫu dữ liệu.
\item Hoàn toàn không truy cập được.
\end{itemize}

\item \textbf{Giai đoạn tấn công}: Bao gồm giai đoạn huấn luyện và giai đoạn suy luận của mô hình.
\item \textbf{Mục tiêu tấn công}: Đối với mô hình phát hiện mã độc thì kẻ tấn công có thể có ba mục tiêu:
\begin{itemize}
\item Tấn công vào khả năng dự đoán: tạo mẫu đối kháng khiến cho mô hình của hệ thống dán nhãn sai.
\item Tấn công vào nhãn phân loại: khiến cho mô hình chỉ dự đoán được một số nhãn nhất định.
\item Tấn công vào thuộc tính: tập trung vào thay đổi một số thuộc tính đầu vào của mẫu. 
\end{itemize}

\item \textbf{Tấn công thuộc tính}: Trong bối cảnh trình phát hiện mã độc thì mô hình học máy sẽ sử dụng nhiều loại thuộc tính khác nhau. Vì vậy, kẻ tấn công cần đưa ra phương án phù hợp, lựa chọn và thử nghiệm các loại thuộc tính để thay đổi mẫu dữ liệu.
\item \textbf{Kỳ vọng về kết quả của cuộc tấn công}: Như đã nêu trên, hầu hết các cuộc tấn công hệ thống sẽ tập trung thay đổi thuộc tính. Ở đây kỳ vọng về kết quả sẽ theo hai hướng:
\begin{itemize}
\item Tấn công qua vec tơ thuộc tính: Kiểu tấn công này thay đổi thuộc tính của mẫu nhưng không đảm bảo về khả năng hoạt động của mẫu. Mẫu đối kháng dù né tránh được hệ thống phát hiện nhưng lại không khởi chạy được.
\item Tấn công qui trình đầu cuối (end-to-end): Kiểu tấn công này sẽ hướng tới việc tạo mẫu đối kháng nhưng vẫn giữ được toàn bộ tính năng của mẫu.
\end{itemize}
 
\end{enumerate}


\begin{figure}[htp]
    \centering
    \includegraphics[width=17cm]{Images/RL_model.png}
    \caption{Tổng quan mô hình đề xuất}
    \label{fig:RL model}
\end{figure}

\subsection{Giả định về ngữ cảnh tấn công}

Nghiên cứu này được xây dựng trên mô hình tạo đột biến với học tăng cường để thực hiện tạo mẫu đối kháng, mục tiêu là làm cho trình phát hiện mã độc đưa ra phát hiện sai. Các tấn công trong nghiên cứu này sử dụng hoàn toàn phương pháp hộp đen, như đã nêu trong mô hình mối đe dọa. Và cũng xét theo khung của mô hình mối đe dọa, kẻ tấn công trong nghiên cứu này sẽ lựa chọn các phương thức sau:
\begin{enumerate}
\item Mục đích của kẻ tấn công là làm ảnh hưởng tới tính toàn vẹn của mô hình phát hiện mã độc.
\item Kẻ tấn công sẽ sử dụng phương thức hộp đen. Giả định này sát với thực tế khi mà các hệ thống phát hiện mã độc sẽ ở dạng một phần mềm dịch vụ (Security-as-a-Service - Security SaaS), như Norton hay McAfee. Phương thức truy cập duy nhất là giao diện để người dùng nạp vào các tệp mã độc và đầu ra là thông tin tĩnh về tệp.
\item Kẻ tấn công không thể truy cập dữ liệu huấn luyện. 
\item Giai đọan tấn công là giai đoạn suy luận của mô hình (sau khi mô hình đã được huấn luyện).
\item Mục tiêu tấn công là nhắm vào khả năng dự đoán của mô hình.
\item Kỳ vọng tấn công hướng tới một quy trình đầu cuối. Đối với các công trình nghiên cứu liên quan, việc tạo mẫu chỉ đơn thuần theo dạng xây dựng vec tơ thuộc tính mang tính lý thuyết. Nghiên cứu của chúng tôi khắc phục được nhược điểm đấy: mỗi mẫu tạo được sẽ qua bước kiểm tra tính năng. Mẫu tạo chỉ thành công khi mẫu vừa qua mặt được trình phát hiện, vừa có thể thực thi.
\end{enumerate}

Ngoài ra, đối tượng tấn công là mô hình phát hiện mã độc ở dạng phân tích tĩnh và kẻ tấn công có khả năng tương tác, phản hồi nhanh từ mô hình hộp đen.

\section{Mô hình phát sinh đột biến mã độc}

\textbf{Tạo môi trường học tăng cường}:

\subsubsection{Tạo môi trường học tăng cường}

Như đã giới thiệu ở Chương 2, trạng thái của môi trường chính là tệp mã độc được trích xuất thành dạng các vec tơ thuộc tính. Để trích xuất các thuộc tính của tệp PE, chúng tôi sử dụng thư viện LIEF của Quarkslab \cite{thomas2017lief}. Các vec tơ thuộc tính bao gồm:

\textbf{Thuộc tính liên quan đến tệp PE}:

\begin{enumerate}
\item Trường siêu dữ liệu (metadata) của tệp PE (62 chiều): Được trích xuất từ đầu mục tệp PE, như thông tin về hệ điều hành, thông tin về linker.
\item Trường siêu dữ liệu của các đoạn (section metadata) (255 chiều): Lưu trữ thông tin về tên các đoạn, kích cỡ, và thống kê phân phối của các byte (entropy). 
\item Trường siêu dữ liệu của bảng nhập (import table) (1280 chiều): Chứa thông tin về các hàm mà tệp thực thi sử dụng từ thư viện bên ngoài (DLL).
\item Trường siêu dữ liệu về bảng xuất (export table) (128 chiều): Chứa thông tin về các hàm mà tệp thực thi xuất ra.
\item Số lượng chuỗi có thể đọc được (104 chiều): Số lượng các chuỗi như URL (https://), các registry key trong Windows (HKEY\_) và các đường dẫn thư mục (c:{\textbackslash\textbackslash}).
\item Thông tin chung về tệp (general file information) (10 chiều): Thông tin chung về tệp, như là tệp có chứa mục sửa lỗi (debug), chữ ký (signature), hoặc độ dài của bảng nhập và xuất.
 
\end{enumerate}
\textbf{Thuộc tính liên quan đến phân phối của byte}:
\begin{enumerate}
\item Bảng tầng suất (byte histogram) (256 chiều): Tạo một bảng để thống kê số lần xuất hiện của các byte. 
\item Ma trận thống kê phân phối của các byte (2D byte-entropy histogram) (256 chiều): Để tính toán được ma trận này, chương trình thực hiện quét tuần tự các byte trong tệp theo kích cỡ 1024 trên mỗi lần quét. 
\end{enumerate}
Hai loại thuộc tính này sẽ tạo thành không gian vec tơ vởi tổng cộng 2351 chiều.

\subsubsection{Tạo phần thưởng}
Phần thưởng là một trong những yếu tố quan trọng nhất của hệ thống học tăng cường, bởi nó ảnh hưởng trực tiếp việc xây dựng chính sách cho tác tử. Trong nghiên cứu này, chúng tôi tính toán phần thưởng qua một hàm tuyến tính với ba tham số:

\begin{equation} \label{eq:eq-reward}
   R = R_{det}  * \omega_{det}  + R_{dis} * \omega_{dis} + R_{func} * \omega_{func}
\end{equation}

Với $R_{max} = 10$, phần thưởng sẽ có các tham số và trọng số như sau:
\begin{itemize}
\item $R_{det}$: Giá trị trả về của trình phát hiện mã độc. Vì đây là mô hình hộp đen nên giá trị đầu ra của trình phát hiện sẽ chỉ có \textit{độc hại} hoặc \textit{lành tính}. $R_{det} = 10$ khi mẫu lành tính (vượt mặt thành công) và $R_{det} = 0$ khi mẫu vẫn độc hại. 
\item $R_{dis}$: Đây là tham số thể hiện số lần thực hiện hành động (distance). Tham số này được tính như sau: \begin{equation} \label{eq: Rdis}
R_{dis} = \frac{R_{max}}{t_{max}} * t
\end{equation}$t$ là số lượt tác tử đã thực hiện và $t_{max}$ là số lượt tối đa mà ta muốn tác tử thực hiện. Như vậy ta có thể tùy chỉnh giá trị $t_{max}$ để khuyến khích tác tử giới hạn số hành động tới một ngưỡng nhất định.
\item $R_{func}$: Đây là giá thể hiện khả năng thực thi của mẫu sau khi chèn. Giá trị này sẽ được tính toán khi mẫu được thử nghiệm trên môi trường máy ảo. $R_{func} = 10$ khi mẫu khởi chạy thành công và $R_{func} = 0$ khi mẫu hỏng.
\end{itemize}
Để tinh chỉnh giá trị phần thưởng dựa trên độ quan trọng của ba tham số, chúng tôi thêm vào các trọng số $\omega$.

Trong thực nghiệm, các trọng số sẽ có giá trị $\omega_{det} = \omega_{dis} = \omega_{func} = 0.33$.

Bên cạnh đó, qua quan sát  chúng tôi nhận thấy tác tử có xu hướng chọn lại liên tục các hành động, vì vậy, chúng tôi thêm vào cơ chế \textit{phạt} cho tác tử. Cụ thể, nếu tác tử sử dụng lặp lại các một hành động $p$ lần thì phần thưởng sẽ là:

\begin{equation}
    R = 
\begin{cases} \label{eq:penalty}
    R,&   \text{khi } p = 0\\
    0 * 0.8,&    \text{khi } p = 1\\
    R * 0.6, &  \text{khi } p \geq 1
\end{cases}
\end{equation}
\subsubsection{Tạo không gian hành động}

Trong nghiên cứu này chúng tôi giữ nguyên không gian hành động của toán tử được nhắc đến ở Mục \ref{gym-malware}. 

\subsubsection{Tạo tác tử}

Trong nhóm Anderson sử dụng thuật toán ACER, một thuật toán dựa trên chính sách (policy-based), cho mô hình gym-malware, thì nhóm Fang DQEAF và  Castro AIMED-RL chỉ ra thuật toán dựa trên giá trị (value-based) cũng cho kết quả thực nghiệm khả quan. Vì vậy tác tử trong mô hình của chúng tôi sử dụng một biến thể của DQN mà nhóm Castro sử dụng: Distributional DQN (DiDQN) \cite{bellemare2017distributional}. Mô hình sẽ tập trung vào học các phân phối của phần thưởng thay vì dự đoán giá trị phần thưởng.

Bảng \ref{tab:approach} so sánh các tác tử được sử dụng trong nghiên cứu này với các nghiên cứu liên quan. Ở đây chúng tôi sử dụng phương pháp khám phá Noisy Nets \cite{fortunato2017noisy}, được chính minh là cho hiệu năng cao về mặt khám phá không gian hành động và đa dạng hóa việc thay đổi vec tơ thuộc tính.

\begin{table}
\centering
\begin{tabular}{|l|l|l|l|}
\hline
Approach     & Agent & Optimizer & Explorer\\ \hline
Fang, 2019     & DDQN   & Adam                     & \epsilon-greedy                          \\ \hline
Anderson, 2018 & ACER   & Adam                     & Boltzmann                       \\ \hline
AIMED-RL       & DiDQN  & Adam                     & Noisy Nets                      \\ \hline
Ours & DiDQN  & Adam                     & Noisy Nets                      \\ \hline
\end{tabular}
\caption{Bảng so sánh tác tử của các nghiên cứu liên quan.}
\label{tab:approach}
\end{table}

\subsection{Trình phát hiện mã độc}
Trong hệ thống được xây dựng, chúng tôi sử dụng 3 mô hình phát hiện mã độc dựa trên học máy là LightGBM, MalConv và Random Forest. Các mô hình này được xem như là mục tiêu tấn công của mã độc và được dùng để đo lường khả năng xâm nhập và tỉ lệ biến đổi thành công của chúng. Nội dung tiếp theo của phần này sẽ mô tả cách thức hoạt động của 3 mô hình trên.

\subsubsection{LightGBM}
Mô hình này được phát triển dựa trên thuật toán Cây quyểt định tăng cường gradient (Gradient boosting decision tree - GBDT), là một thuật toán được sử dụng rộng rãi do sự hiệu quả và độ chính xác cao. Tuy nhiên, thuật toán gặp phải một vấn đề lớn về việc đánh đổi tài nguyên và thời gian xử lý với hiệu năng cao khi phải xử lý một lượng dữ liệu lớn. Cụ thể, thuật toán GBDT cần phải quét tất cả các phiên bản dữ liệu để ước tính mức tăng thông tin của tất cả các điểm phân tách có thể có. Do đó, độ phức tạp tính toán của chúng sẽ tỷ lệ thuận với số lượng thuộc tính và số lượng thực thể dữ liệu. Điều này làm cho việc triển khai này rất tốn thời gian khi xử lý một lượng lớn dữ liệu.

Mô hình LGBM được áp dụng để giải quyết vấn đề trên của thuật toán GBDT bằng hai kỹ thuật chính, Kỹ thuật Lấy mẫu một phần dựa trên gradient (Gradient based One Side Sampling - GOSS) và Kỹ thuật Nhóm thuộc tính độc quyền (Exclusive Feature Bundling - EFB). Với phương pháp này, mô hình được chứng minh đã làm giảm quá trình huấn luyện khoảng 20 lần nhưng vẫn giữ nguyên độ chính xác khi thực hiện trên các tập dữ liệu như Allstate, FlighDelay, LETOR, KDD10, KDD12.

Kỹ thuật Lấy mẫu một phần dựa trên độ dốc: Là một phương pháp lấy mẫu dựa trên cơ sở gradient. Một phương pháp thông thường để giảm mẫu là loại bỏ các trường hợp có gradient nhỏ bằng cách chỉ tập tủng vào các trường hợp có gradient lớn, nhưng điều này sẽ làm thay ododir phân phối liệu. Tóm lại, GOSS giữ lại các trường hợp có gradient lớn trong khi thực hiện lấy mẫu ngẫu nhiên các trường hợp có gradientn nhỏ.

Kỹ thuật Nhóm thuộc tính độc quyền: Là một phương pháp giảm số lượng thuộc tính một cách hiệu quả mà gần như không làm mất mát dữ liệu. Trong một không gian đối tượng thưa thớt, nhiều đối tượng gần như là độc quyền, ngụ ý rằng chúng hiếm khi nhận các giá trị khác không đồng thời. Các tính năng được mã hóa một lần là một ví dụ hoàn hảo về các tính năng độc quyền. EFB kết hợp các tính năng này, giảm kích thước để cải thiện hiệu quả trong khi vẫn duy trì mức độ chính xác cao.

\begin{figure}[htp]
    \centering
    \includegraphics[width=17cm]{Images/LightGBM.png}
    \caption{Luồng hoạt động của mô hình LGBM}
    \label{fig:model-flow}
\end{figure}
\subsubsection{MalConv}
Mô hình phát hiện mã độc MalCon được phát triển dựa trên thuật toán Mạng Nơ-ron với 3 tiêu chí:
\begin{itemize}
\item Khả năng mở rộng tốt cùng với độ dài chuỗi
\item Khả năng xem xét toàn bộ nội dung cục bộ hoặc toàn cục của tập tin
\item Khả năng hỗ trợ phân tích với các mã độc bị gắn cờ.
\end{itemize}
\begin{figure}[htp]
    \centering
    \includegraphics[width=17cm]{Images/MalConv.png}
    \caption{Kiến trúc của mô hình MalConv}
    \label{fig:model-flow}
\end{figure}

Tập tin ban đầu được truyền vào cho lớp nhúng, sau đó, kết quả được xử lý bởi lớp này được đưa qua 2 lớp chập đồng thời. Kết quả đầu ra của hai lớp được nhân từng phần tử và tùy chọn chuyển sang một đơn vị tuyến tính được chỉnh lưu (ReLU). Sau đó, một lớp tổng hợp tối đa tạm thời sẽ lấy giá trị tối đa chung của mỗi kênh trong số 128 kênh. Phần cuối cùng là mạng nơ-ron được kết nối đầy đủ (với kích hoạt ReLU tùy chọn) có 128 nút đầu vào và chín nút đầu ra softmax tương ứng với các lớp độc hại khác nhau của phần mềm độc hại.

\subsubsection{Random Forest}
Random forest là một thuật toán học máy giám sát, thường được ứng dụng để giải quyết các bài toán dạng hồi quy hoặc phân loại. Ý tưởng cơ bản của thuật toán là xây dựng các cây quyết định dựa trên các tập con độc lập nhau thuộc tập dữ liệu cho trước. Tại mỗi nút, một số gái trị được lựa chọn ngẫu nhiên cho tới khi tìm được cách phân chia tốt nhất.

Trong trình phát hiện dựa trên thuật toán Random Forest này, các tập tin dạng nhị phân sẽ được phân tích thành 2381 trường dựa trên các thuộc tính như các đoạn mã, dữ liệu, liên kết động, kích thước, hình ảnh, số lượng ký tự, và vân vân.Các siêu tham số được dùng để tinh chỉnh mô hình bao gồm số lượng cây quyết định, độ sâu, số lượng thuộc tính được lựa chọn ngẫu nhiên, số lượng thực thể tối thiểu ở mỗi lá, tỉ lệ biến số lớp tối thiểu

\subsection{Trình xác thực khả năng thực thi}
Thông thường, nếu muốn phân tích khả năng thực thi và đầy đủ các tính năng, ta sẽ sử dụng một trình phân tích động dạng \textit{Hộp cát} (Sandbox). Hệ thống này sẽ khởi chạy mã độc trong một môi trường ảo và phân tích các đặc tính động của tệp, đưa ra một bảng phân tích khả đầy đủ. Nổi tiếng nhất là VirusTotal (https://www.virustotal.com/)  - một trình phân tích mã độc qua giao diện web. Ngoài ra còn có dự án mã nguồn mở như Cuckoo (https://cuckoosandbox.org/). Tuy nhiên, qua thực nghiệm nhóm chúng tôi nhận thấy các trình phát hiện này tốn nhiều thời gian để phân tích một mẫu, không thích hợp để thử nghiệm khả năng thực thi trong hệ thống đề xuất. Vì vậy chúng tôi lựa chọn phương án sử dụng máy ảo.

Trình xác thực khả năng thực thi ở đây sẽ là một máy ảo chạy Windows. Sau khi trình phát hiện mã độc phân tích xong mẫu thì mẫu này sẽ được nạp vào máy ảo. Ở đây, chúng tôi chỉ kiểm tra khả năng khởi chạy của mã độc.

\section{Luồng hoạt động mô hình đề xuất}

Hình \ref{fig:model-flow} là sơ đồ của luồng hoạt động của mô hình. Tuần tự các bước như sau:

\begin{enumerate}
\item Môi trường sẽ lựa chọn một mẫu mã độc và đặt giới hạn số lần chèn các hành động là $N$ lần.
\item Môi trường sẽ  trích xuất thuộc tính của mã độc thành một bộ vec tơ thuộc tính. Sau đó tác tử của hệ thống sẽ nhận bộ vec tơ này và đưa ra hành động để thay đổi tập thuộc tính này.
\item Môi trường chuyển bộ vec tơ thuộc tính lại thành dạng tệp thực thi.
\item Tệp thực thi sau đó được đưa vào trình phát hiện mã độc.
\item Nếu trình phát hiện đưa ra đánh giá lành tính cho tệp (né tránh thành công) thì mẫu sẽ được chuyển sang trình xác thực khả năng thực thi.
\item Trình xác định khả năng thực thi (máy ảo) sẽ nhận mẫu và kiểm tra. Nếu mẫu có khả năng thực thi ổn định thì xem như mẫu đối kháng được tạo thành công. Ngược lại, mẫu đối kháng không thực thi được thì xem như thất bại.
\end{enumerate}

\begin{figure}[htp]
    \centering
    \includegraphics[width=17cm]{Images/model-flow.png}
    \caption{Luồng hoạt động của mô hình}
    \label{fig:model-flow}
\end{figure}

Chi tiết quá trình huấn luyện mô hình được trình bày trong Thuật toán \ref{alg:training-algorithm}. Như đã nêu trên, chúng tôi sử dụng mô hình Distributional DQN cho tác tử \cite{bellemare2017distributional}, cụ thể là hàm CategoricalDQN \ref{alg:categoricaldqn}. Hàm này sẽ tính toán phân phối của các giá trị $Q$ thay vì chỉ tối đa hóa giá trị kỳ vọng như trong phương trình Bellman. 

\begin{algorithm}
\begin{algorithmic}[1]
\caption{Huấn luyện mô hình tạo đột biến}\label{alg:training-algorithm}
\STATE Initialize Memory $M$ with size $M_{max}$\\
\STATE Initialize Network $Q$ with weight $\theta$\\
\FOR{$episode \gets 1$ to $EPISODES$}
    \STATE Select a binary $bin_{original}$ randomly from folder of malwares
    \STATE Extract binary features $s_{orignial} = ExtractBinaryFeatures(bin_{original})$
    \FOR{$t \gets 1$ to $MAXTURNS$}
        \STATE With noise parameter $\epsilon$ select an action $a_t$ 
        \STATE Modify $bin_t$ by action $a_t$ to make $bin_{t+1}$ and $s_{t+1} = ExtractBinaryFeatures(bin_{t+1})$, observe reward $r_{t+1}$
        \STATE Store transition $(s_t, a_t, r_{t+1}, s_{t+1})$
        \IF{ $sizeof(M) > batchSize$}
            \FOR{$i \gets 1$ to $K$}
                \STATE Sample transition $X_i ~ P(X_i) = p_{x_i} / {\sum jp_j}$    
                \STATE Calculate $CategoricalDQN(X_i)$ ( \ref{alg:categoricaldqn})
            \ENDFOR
            \STATE Exert Adam optimizer to optimize parameter $\theta$
        \ENDIF
    \ENDFOR
\ENDFOR
\end{algorithmic}
\end{algorithm}

\begin{algorithm} \caption{CategoricalDQN trong DiDQN}\label{alg:categoricaldqn}
\begin{algorithmic}[1]
\STATE $X_t = (x_t, a_t, r_t, x_{t+1}), \gamma \in [0, 1]$
\STATE $Q(x_{t+1}, a) := \sum z_ip_i(x_{t+1}, a)$
\STATE $a^{\ast} \gets arg \max_a Q(x_{t+1}, a)$
\STATE $m_i = 0, i \in 0,...,N-1$
\FOR{$j \in 0,...,N-1 $}
	\STATE $\hat{T}z_j \gets [r_t + \gamma_tz_j]_{V_{min}}^{V_{max}}$
        \STATE $b_j \gets (\hat{T}z_j - V_{min}) / \delta z$ \Comment{ #$b_j \in [0,N-1]$}
        \STATE $l \gets \lfloor b_j \rfloor , u \gets \lceil b_j \rceil$
        \STATE $m_l \gets m_l + p_j(x_{t+1}, a^{\ast})(u - b_j)$
        \STATE $m_u \gets m_u + p_j(x_{t+1}, a^{\ast})(b_j - l)$
\ENDFOR
\RETURN $-\sum_i m_i \log p_i(x_t, a_t)$
\end{algorithmic}
\end{algorithm}


Theo kết quả của nhóm Anderson thì hệ thống có khả năng né tránh trình phát hiện mã độc lên tới 24 \%. Nghĩa là với 100 mã độc thì hệ thống sẽ tạo ra được 24 mẫu đối kháng né tránh thành công. Ở bước đánh giá với 200 mẫu, khả năng né tránh là 16.25\%. Mặc dù các hành động được cho là sẽ không làm ảnh hưởng tới chức năng của mã độc, công trình của nhóm chưa có bước kiểm tra lại tính năng của mã được sinh ra.

Cũng dựa vào phương thức tương tự mà nhóm tác giả Fang đã xây dựng hệ thống tạo mẫu đối kháng sử dụng học máy DQEAF \cite{fang2019evading}. Nhóm này cho rằng với dữ liệu đầu vào cỡ nhỏ thì hiệu quả tạo mẫu sẽ tốt hơn. Không gian hành động của công trình này được giảm xuống chỉ còn bốn hành động. Tuy nhiên, như nhóm tác giả Anderson, việc kiểm tra lại tính năng của mã vẫn chưa được thực hiện. Mặc khác, với mỗi mã độc, hệ thống của Fang chỉ có bốn hành động khác nhau, nhưng số lần thực hiện lại lên tới 80 lần. Việc này vô tình tạo nên đặc tính cho mã độc tạo bởi DQEAF, giúp trình phát hiện học lại đặc tính và cuối cùng phát hiện được mẫu đối kháng.

Tiếp nối DQEAF là hệ thống AIMED-RL \cite{labaca2021aimed} do nhóm tác giả Raphael Labaca-Castro xây dựng. Hệ thống này sử dụng lại mô hình của gym-malware; nhóm đã cải tiến nhiều hơn về mặc đảm bảo tính năng cho mã độc. Cụ thể, AIMED-RL sẽ đánh giá thêm mức độ tương đồng giữa mẫu đối kháng và mẫu gốc. Bởi họ xác định rằng nếu muốn giữ cho mẫu hoạt động được sau khi chèn thì phải đảm bảo mẫu không bị thay đổi nhiều. Vì vậy, phần thưởng của hệ thống AIMED-RL sẽ tính toán cả mức độ tương đồng. Hành động giữ được độ tương đồng với mẫu gốc càng cao thì phần thưởng sẽ càng cao. Cải tiến này khích lệ tác tử lựa chọn những hành động để bảo toàn khả năng thực thi của mẫu.

Tuy nhiên, các công trình kể trên chỉ đánh giá lại số lượng mẫu đột biến có khả năng thực thi sau khi huấn luyện mô hình học tăng cường. Vì vậy, mô hình học tăng cường không chú trọng vào việc tạo mẫu có khả năng thực thi mà chỉ đơn thuần giúp mẫu vượt mặt trình phát hiện. Nhận thấy được điều đấy, nhóm chúng tôi quyết định nghiên cứu và xây dựng một mô hình tạo đột biến có khả năng thực thi. 

-----------------------------------------------------------------------------------------------------




\subsection{Tập dữ liệu}

\subsubsection{EMBER}

Tập dữ liệu EMBER là một tập hợp các thuộc tính được trích xuất từ tập tin PE với sự hỗ trợ của thư viện LIEF của Quarkslab \cite{thomas2017lief}. EMBER chứa 1.1 triệu tập tin nhị phân,
trong đó bao gồm 400,000 mã độc, 400,000 tập tin lành tính và còn lại chưa dán nhãn.
Các thuộc tính được trích xuất từ các tập tin bao gôm các loại như:
\begin{itemize}
\item Dữ liệu chung của tập tin
\item Dữ liệu của các trường tiêu đề
\item Dữ liệu về các hàm nhập
\item Dữ liệu về các hàm xuất
\item Dữ liệu về các phân đoạn
\item Byte histogram
\item Byte-entropy histogram
\item Dữ liệu về các chuỗi
\end{itemize}

\subsubsection{Virus Total}
Chúng tôi thực hiện việc huấn luyện mô hình học tăng cường qua tập dữ liệu mã độc bao gồm 16068 tệp thực thi trên hệ điều hành Windows 32 bit (Windows PE32)  được lọc ra từ bộ dữ liệu gốc bao gồm hơn 200 000 mẫu chứa cả PE32 và PE32+. Trong đó, các tệp lành tính được thu thập từ hệ thống của hệ điều hành Windows 7, 8, 10 và một số tệp cài đặt phần mềm. Bên cạnh đó, các tệp độc hại được thu thập từ nguồn VirusTotal, những tập tin này đều được phát hiện bởi ít nhất một nửa trên tổng số trình phát hiện mã độc trên VirusTotal. Các mẫu độc hại bao gồm các loại Adware (DownloadHelper, StartPage,...), Backdoor (Androm, Nanobot,...), Ransomware (Gandcrab, Locker,...), Trojan (Emotet, Coinminer,...), Virus (Virut, Lamer,...), Worm (Allape, Sobig,...). 

\subsection{Trình phát hiện mã độc}
Như đã trình bày trong Chương 3, chúng tôi sử dụng hai trình phát hiện mã độc với phương pháp phân tích tĩnh là LGBM, MalConv và RandomForest. Ba trình phát hiện này đều được huấn luyện với tập dữ liệu EMBER và cho ra kết quả khá khả quan.

Chúng tôi đã tiến hành xác thực lại 3 mô hình trên với mục đích kiểm tra khả năng phát hiện mã độc. Mỗi mô hình được huấn luyện với tập dữ liệu EMBER và kiểm tra khả năng phát hiện mới với tập dữ liệu VirusToal. Kết quả được mô tả ở Bảng \label{tab:verify-detector} cho thấy rằng 3 mô hình mục tiêu đều có khả năng phát hiện các loại mã độc tương đối tốt, với ngưỡng tỉ lệ phát hiện chính xác giao động từ $93.74\%$ tới $96.51\%$, trong đó, kết quả cao nhất thuộc về mô hình ứng dụng thuật toán LGBM.

Trong quá trình thực nghiệm, nhóm đã kiểm tra và đưa ra ngưỡng phát hiện mã độc (threshold) cho hai hệ thống này: nếu trình phát hiện trả về thông số (confidence score) lớn hơn ngưỡng phát hiện thì được cho là độc hại, ngược lại mẫu sẽ là lành tính. Việc đưa ra ngưỡng phát hiện chỉ đơn thuần tuân theo giả định tấn công hộp đen. Vì vậy, kết quả huấn luyện hệ thống học tăng cường phụ thuộc nhiều vào ngưỡng phát hiện.

Cụ thể, chúng tôi đặt ngưỡng phát hiện như trong Bảng \ref{tab:thresholds}
\begin{center}
\begin{table}
\centering
\begin{tabular}{|c|c|c|}
\hline
Detector & Accuracy & AUC \\ \hline
LGBM              &   96.51\%       &   98.50\%                \\ \hline
MalConv                &    93.74\%          &    97.92\%               \\ \hline
RandomForest                &    95.81\%          &    92.86\%               \\ \hline
\end{tabular}
\caption{Bảng kết quả tỉ lệ né tránh của trình tạo đột biến so với 3 mô hình khi không sử dụng trình phát hiện.}
\label{tab:verify-detector}
\end{table}
\end{center}

\begin{center}
\begin{table}
\centering
\begin{tabular}{|c|c|}
\hline
Detector & Threshold \\ \hline
 LGBM       & 0.9  \\ \hline
 MalConv    &  0.7  \\ \hline
 RandomForest & 0.9 \\ \hline
\end{tabular}
\caption{Bảng tham số ngưỡng phát hiện của 3 mô hình.}
\label{tab:thresholds}
\end{table}
\end{center}
\subsection{Trình xác thực khả năng thực thi}

Ở đây chúng tôi thiết lập một máy ảo của VirtualBox chạy hệ điều hành Windows 7 như ở hình \ref{fig:vm-windows7}. Qua thử nghiệm, hầu hết các mã độc trong tập dữ liệu chạy ổn định trên hệ điều hành này. 

Trong thực nghiệm, máy ảo này sẽ chạy ở chế độ ngầm (headless), vì vậy hao tốn tài nguyên là không đáng kể. Hệ thống học tăng cường sẽ điều khiển máy ảo qua công cụ VBoxManage của VirtualBox với các đoạn lệnh như:

\begin{itemize}
\item \textit{VBoxManage showvminfo} - Lệnh xác định trạng thái của máy ảo (bật/tắt).
\item \textit{VBoxManage startvm <VM> --type headless} - Lệnh khởi chạy máy ảo. Mỗi mẫu mã độc nạp vào thì chúng tôi sẽ khởi động lại máy ảo.
\item \textit{VBoxManage guestcontrol <VM> --username <username> --password <password> run --exe <path>}: Lệnh thực thi tệp. Đây là lệnh quan trọng nhất trong hệ thống, lệnh này sẽ điều khiển máy ảo thực thi mẫu sau khi được chèn và trả về mã trạng thái (tệp có khởi chạy được hay không).
\end{itemize}

\begin{figure}[htp]
    \centering
    \includegraphics[width=10cm]{Images/VirtualBox-injected.png}
    \caption{Máy ảo VirtualBox với hệ điều hành Windows 7 đang được trình tạo đột biến nạp mẫu và thực thi}
    \label{fig:vm-windows7}
\end{figure}

\subsection{Hệ thống tạo đột biến}

Chúng tôi thực hiện hệ thống tạo đột biến được trình bày ở Chương 3.

\subsubsection{Trích xuất và thay đổi thuộc tính của tập mã độc}

Như đã nêu, chúng tôi sử dụng thư viện LIEF của Quarkslab \cite{thomas2017lief} để tùy chỉnh tệp mã độc.  Luồng hoạt động của thư viện LIEF được trình bày qua Hình \ref{fig:lief-library}. Thư viện này nhận vào một tập thực thi và cung cấp các API để người dùng có thể tùy biến tập theo ý muốn. Dựa vào những API này mà chúng tôi có thể tác động các hành động chỉ định bởi tác tử học tăng cường lên tập mã độc.

\begin{figure}[htp]
    \centering
    \includegraphics[width=10cm]{Images/lief-library.png}
    \caption{Luồng hoạt động của thư viện LIEF.}
    \label{fig:lief-library}
\end{figure}

\subsubsection{Xây dựng hệ thống học tăng cường}

Để xây dựng hệ thống học tăng cường, chúng tôi sử dụng thư viện chainerrl \cite{fujita2019chainerrl}. Thư viện này cung cấp đa dạng các thuật toán học tăng cường và các cơ chế học sâu liên quan. Trong nghiên cứu này, chúng tôi chỉ sử dụng DiDQN để thực hiện hóa hệ thống. DiDQN được chứng mình là cho hiệu quả cao nhất so với các biến thể khác của DQN. Các tham số của hệ thống học tăng cường được trình bày trong Bảng \ref{tab:RL-parameter}.

\begin{table}
	\centering
	\caption{Bảng các tham số được sử dụng trong mô hình học tăng cường.}
	\label{tab:RL-parameter}
	\begin{tabular}{l l p{8cm}}
		\toprule[0.125em]
		{\textsc{Parameter}} & {\textsc{Value}} & \textsc{{Description}}\\\toprule[0.125em]%\hline% \midrule
		EPISODES    &  1000      &   Số mẫu mã độc tối đa được nạp vào\\  \midrule
		MAXTURNS    &  10      &  Số lượt thực hiện hành động tối đa đối với một mẫu mã độc\\\midrule
		adam\textunderscore epsilon   &   1e-2      &  Tham số của thuật toán  tối ưu Adam được sử dụng\\\midrule
      $\gamma$    &  0.95     &   Chiết khấu cho giá trị phần thưởng\\\midrule
        $M_{max}$    &   1000      &   Số mục kinh nghiệm trong mô hình DQN\\\midrule
        training files count & 3700 & Số lượng tệp trong tập dữ liệu huấn luyện\\\midrule
        testing files count & 300 & Số lượng tệp trong tập dữ liệu kiểm tra        \\\bottomrule[0.125em]
	\end{tabular}
\end{table}

\section{Kết quả thí nghiệm}

Ở mục này, nhóm sẽ trình bày các kết quả thực nghiệm và đưa ra đánh giá.

Nhóm tập trung trả lời hai câu hỏi sau:

Câu hỏi 1: Với việc tích hợp trình xác định khả năng thực thi thì tỉ lệ né tránh thành công trình phát hiện mã độ là bao nhiêu và so sánh với kết quả của các nghiên cứu liên quan?

Câu hỏi 2: Liệu hệ thống học tăng cường có khả năng sử dụng đa dạng các hành động thay vì chỉ tập trung vào một số hành động như trong các nghiên cứu liên quan?

\subsection{Tỉ lệ né tránh thành công không sử dụng trình xác thực}

Bảng \ref{tab:result-lgbm-malconv-no-vm} là kết quả về tỉ lệ né tránh thành công các trình phát hiện khi không sử dụng trình xác thực. Kết quả thu được khá cao. Với tác tử DiDQN, ba mô hình LGBM, MalConv, và RandomForest cho kết quả lần lượt là 42.7\%, 43.8\%, 33.4\%. Kết quả này cao tương ứng với các nghiên cứu trước đó, được trình bày ở Bảng \ref{tab:result-comparison}. Hầu hết các hệ thống thu được kết quả trên 40\% tỉ lệ né tránh khi không có trình xác thực thực thi.

\begin{center}
\begin{table}
\centering
\begin{tabular}{|c|c|c|}
\hline
Detector & DiDQN Agent & Random Agent \\ \hline
LGBM              &   42.7\%       &   6.8\%                \\ \hline
MalConv                &    43.8\%          &    7.8\%               \\ \hline
RandomForest                &    33.4\%          &    5.4\%               \\ \hline
\end{tabular}
\caption{Bảng kết quả tỉ lệ né tránh của trình tạo đột biến so với hai mô hình LGBM và MalConv  khikhông sử dụng trình phát hiện.}
\label{tab:result-lgbm-malconv-no-vm}
\end{table}
\end{center}

\subsection{Tỉ lệ né tránh thành công có trình xác thực}

Bảng \ref{tab:result-lgbm-malconv} là kết quả về tỉ lệ né tránh thành công các trình phát hiện. Tỉ lệ này được so sánh với hệ thống sử dụng tác tử ngẫu nhiên. Cụ thể, với mô hình LGBM, tác tử DiDQN đạt tỉ lệ tạo mẫu đột biến là 14.6\%; với mô hình MalConv tỉ lệ này đạt 18.6\%. Có thể thấy, tác tử sử dụng thuật toán DiDQN cho kết quả tốt hơn so với tác tử ngẫu nhiên. Khác biệt về tỉ lệ mẫu tạo cho LGBM so với MalConv nằm ở việc lựa chọn ngưỡng phát hiện.

Bảng \ref{tab:result-comparison} là kết quả so sánh tỉ lệ né tránh với các nghiên cứu liên quan. Kết quả bảng này cho thấy tỉ lệ né tránh khi áp dụng trình phát hiện LGBM, với ngưỡng phát hiện như nhau (0.9).  Nhóm chúng tôi nhận thấy tỉ lệ né tránh trong nghiên cứu này (14.6\%)  thấp hơn so với các nghiên cứu khác, nhưng tỉ lệ này đại diện cho tỉ lệ mẫu đột biến thành công và có thể thực thi được. Điều này chứng minh rằng các nghiên cứu trước đó mang lại hiệu quả cao về mặt né tránh trình phát hiện, nhưng chưa thực tế khi không có khả năng xác thực lại khả năng thực thi của mẫu. 

Bên cạnh đó, các kết quả ở Bảng \label{tab:change-maxturns} cho thấy rằng tỉ lệ vượt mặt trình phát hiện dựa trên học máy có xu hướng tăng dần khi điều chỉnh thông số về lượt chèn hành động tối đa từ 10, 20, 40 tới 80 hành động, với khả năng vượt mặt giao động từ $42.7\%$ tới $47.47\%$. Tuy nhiên, khả năng thực thi và vượt mặt không tỉ lệ thuận với kết quả vừa được nếu ra. Với cấu hình $MaxTurn = 10$, khả năng thực thi và vượt mặt đồng thời là $14.65\%$, và với cầu hình $MaxTurn=80$ thì tỉ lệ đó là $13.18\%$. Nguyên nhân cho sự giảm này là việc nhiều hành động được thực thi trên một tập tin dẫn tới tập tin bị hư hại và mất khả năng thực thi.

\begin{center}
\begin{table}
\centering
\begin{tabular}{|c|c|c|}
\hline
Detector & DiDQN Agent & Random Agent \\ \hline
LGBM              &   14.6\%       &   5.6\%                \\ \hline
MalConv                &    18.6\%          &    7.8\%               \\ \hline
RandomForest                &    12.3\%          &    6.7\%               \\ \hline
\end{tabular}
\caption{Bảng kết quả tỉ lệ né tránh của trình tạo đột biến so với hai mô hình LGBM và MalConv.}
\label{tab:result-lgbm-malconv}
\end{table}
\end{center}

\begin{table}
    \begin{tabular}{|c|c|c|c|c|} \hline
        Approach            & Action Space   & Max Turn & Evasion Rate & \multicolumn{1}{m{3cm}|}{Evasion and Execution Rate} \\ \hline
        Aderson	et al, 2018 & 11             & 10       & 16.25\%      & - \\ \hline
        Fang et al, 2019	& 4              & 80       & 46.56\%      & - \\ \hline
        Castro et al, 2021	& 10             & 5        & 42.13\%      & - \\ \hline
        Ours            	& 10             & 10       & 42.70\%      & 14.65\% \\ \hline
    \end{tabular}
    \caption{Bảng so sánh tỉ lệ né tránh với các nghiên cứu liên quan khi sử dụng mô hình phát hiện LGBM.}
\label{tab:result-comparison}
\end{table}

\begin{table}
    \begin{tabular}{|c|c|c|c|c|} \hline
        Action Space   & Max Turn & Evasion Rate & \multicolumn{1}{m{3cm}|}{Evasion and Execution Rate} & \multicolumn{1}{m{3cm}|}{Training Time (minutes)} \\ \hline
        10             & 10       & 42.70\%      & 14.65\%                    & 330         \\ \hline
        10             & 20       & 42.84\%      & 14.72\%                    & 612         \\ \hline
        10             & 40       & 44.23\%      & 14.59\%                    & 1187         \\ \hline
        10             & 80       & 47.57\%      & 13.18\%                    & 2136         \\ \hline
    \end{tabular}
    \caption{Bảng so sánh tỉ lệ né tránh khi thay đổi thông số Max Turn0 trên đối tượng LGBM}
    \label{tab:change-maxturns}
\end{table}

\subsection{Mức độ đa dạng của các hành động}
Như đã trình bày trong mục \ref{sec:related-works} Khi hệ thống học tăng cường chỉ tập trung vào thực hiện một số hành động mà nó cho là hiệu quả thì cũng tạo ra các đặc tính riêng. Hệ quả là trình phát hiên mã độc có thể học lại các đặc tính này và cải thiện khả năng của nó. Mô hình DQEAF của nhóm Fang là một ví dụ. Nghiên cứu của Fang sử dụng tới 80 thực hiện hành động với không gian chỉ 4 hành động riêng biệt. Vì vậy, nhóm chúng tôi thêm vào cơ chế phạt, được đề cập ở hàm \ref{eq:penalty}. Tỉ lệ sử dụng các hành động của tác tử  được trình bày trong hình \ref{fig:actions-percentage}. 

Tương tự như các nghiên cứu trước đó, upx\textunderscore pack là hành động phổ biến nhất để tạo mẫu đột biến. Bởi cơ chế nén sẽ thay đổi cấu trúc của tệp mã độc, làm thay đổi toàn bộ vec tơ thuộc tính của tệp. Trong thực tế, các nhà phát hành ứng dụng thường nén các tệp thực thi để giảm kích cỡ chương trình. Các trình phát hiện thường sẽ không xét cơ chế nén là một thuộc tính của mã độc, vì làm như vậy sẽ tạo ra nhiều dương tính giả (false positive) \cite{demetrio2021functionality}. Vì vậy, việc tạo mẫu đột biến qua upx\textunderscore pack vẫn được xem là an toàn.

Theo như kết quả ở bảng \label{tab:evasion-and-execution-malware-result}, hành động upx_pack xuất hiện ở hầu hết các tập tin mã độc được tạo đột biến có khả năng vượt mặt và thực thi thành công. Các lượt huấn luyện tạo ra mã độc thỏa mãn hai tiêu chí về thực thi và vượt mặt có số điểm tương đối cao, từ 6.93 tới 9.9. Với 6.93 tương ứng với mã độc đột biến được tạo từ 1 hành động upx_pack và 9.9 tương ứng với 10 hành động tác động trên tập tin mã độc, trong đó, các hành động thay đổi giá trị kiểm tra header_checksum hoặc thay đổi các phân đoạn được sử dụng phổ biến. Với những mã độc được tạo đột biến này, khả năng phát hiện của các trình phát hiện mã độc dựa trên học máy giảm đáng kể, từ ngưỡng xấp xỉ $96\%$ xuống còn khoảng $77.71\%$ tới $89.48\%$ với mô hình phát hiện sử dụng thuật toán LGBM.

Ở bảng \label{tab:evasion-malware-result}, chúng ta có thể thấy rằng điểm phần thưởng cho những tập tin mã độc đột biến chỉ có khả năng vượt mặt thấp hơn rõ rệt khi so sánh với các tập tin vừa có khả năng vượt mặt vừa có khả năng thực thi. Cụ thể, điểm giao động từ 3.63 tới 6.27, với 3.63 tương ứng với mã độc được thêm các phân đoạn và 6.27 tương ứng với tập hợp các hành động như upx_pack, remove_debug, imports_append, .... Tuy nhiên, các tập tin này vẫn đảm bảo khả năng vượt mặt khi giảm được đáng kể khả năng kiểm tra của trình phát hiện mã độc xuống còn ngưỡng 80\% tới gần 90\%, đặc biệt, có trường hợp xuống còn 69.13\%.

\begin{table}
    \begin{tabular}{|c|c|c|c|} \hline
           & Detection Value & Reward & Actions taken \\ \hline
        1 & 80.94\% & 6.93 & \multicolumn{1}{m{7cm}|}{upx\_pack} \\ \hline
        2 & 88.74\% & 7.26 & \multicolumn{1}{m{7cm}|}{upx\_unpack; upx\_pack} \\ \hline
        3 & 88.06\% & 7.26 & \multicolumn{1}{m{7cm}|}{overlay\_append; upx\_pack} \\ \hline
        4 & 89.48\% & 7.26 & \multicolumn{1}{m{7cm}|}{imports\_append; upx\_pack} \\ \hline
        5 & 77.71\% & 7.26 & \multicolumn{1}{m{7cm}|}{section\_rename; upx\_pack} \\ \hline
        6 & 88.75\% & 7.26 & \multicolumn{1}{m{7cm}|}{break\_optional\_header\_checksum; upx\_pack} \\ \hline
        7 & 85.05\% & 7.59 & \multicolumn{1}{m{7cm}|}{imports\_append; break\_optional\_header\_checksum; upx\_pack} \\ \hline
        8 & 88.01\% & 7.92 & \multicolumn{1}{m{7cm}|}{imports\_append; break\_optional\_header\_checksum; imports\_append; upx\_pack} \\ \hline
        9 & 88.34\% & 8.25 & \multicolumn{1}{m{7cm}|}{section\_rename; imports\_append; break\_optional\_header\_checksum; section\_rename; upx\_pack} \\ \hline
        10 & 88.94\% & 8.25 & \multicolumn{1}{m{7cm}|}{imports\_append; section\_rename; break\_optional\_header\_checksum; break\_optional\_header\_checksum; upx\_pack} \\ \hline
        11 & 79.54\% & 9.9 & \multicolumn{1}{m{7cm}|}{section\_rename; upx\_pack; upx\_pack; overlay\_append; upx\_unpack; section\_rename; section\_append; upx\_unpack; break\_optional\_header\_checksum; upx\_pack} \\ \hline
    \end{tabular}
    \caption{Bảng mô tả thông số của các mã độc được tạo đột biến có khả năng vượt mặt và thực thi}
    \label{tab:evasion-and-execution-malware-result}
\end{table} 


\begin{table}
    \begin{tabular}{|c|c|c|c|} \hline
             & Detection Value & Reward & Actions taken \\ \hline
        1	& 86.82\% & 3.63 & \multicolumn{1}{m{7cm}|}{section\_add} \\ \hline
        2	& 89.29\% & 3.63 & \multicolumn{1}{m{7cm}|}{remove\_signature} \\ \hline
        3	& 89.31\% & 4.29 & \multicolumn{1}{m{7cm}|}{imports\_append; remove\_debug; section\_add} \\ \hline
        4	& 89.45\% & 3.96 & \multicolumn{1}{m{7cm}|}{break\_optional\_header\_checksum; section\_add} \\ \hline
        5	& 89.05\% & 4.62 & \multicolumn{1}{m{7cm}|}{section\_rename; upx\_pack; upx\_pack; section\_add} \\ \hline
        6	& 69.13\% & 4.62 & \multicolumn{1}{m{7cm}|}{upx\_unpack; section\_rename; section\_append; section\_add} \\ \hline
        7	& 88.59\% & 4.95 & \multicolumn{1}{m{7cm}|}{section\_rename; imports\_append; section\_append; upx\_pack; section\_add} \\ \hline
        8	& 89.44\% & 5.28 & \multicolumn{1}{m{7cm}|}{imports\_append; imports\_append; upx\_pack; imports\_append; imports\_append; section\_add} \\ \hline
        9	& 89.29\% & 5.61 & \multicolumn{1}{m{7cm}|}{section\_rename; upx\_pack; upx\_pack; upx\_unpack; upx\_pack; imports\_append; section\_add} \\ \hline
        10	& 88.65\% & 5.61 & \multicolumn{1}{m{7cm}|}{imports\_append; upx\_pack; imports\_append; upx\_unpack; upx\_pack; imports\_append; section\_add} \\ \hline
        11	& 89.98\% & 6.27 & \multicolumn{1}{m{7cm}|}{upx\_pack; remove\_debug; overlay\_append; imports\_append; imports\_append; section\_append; upx\_unpack; upx\_pack; section\_add} \\ \hline
        12	& 86.88\% & 5.61 & \multicolumn{1}{m{7cm}|}{break\_optional\_header\_checksum; section\_append; overlay\_append; overlay\_append; remove\_signature; break\_optional\_header\_checksum; section\_add} \\ \hline
    \end{tabular}
    \caption{Bảng mô tả thông số của các mã độc được tạo đột biến có khả năng vượt mặt}
    \label{tab:evasion-malware-result}
\end{table}

\subsection{Hành động làm ảnh hưởng khả năng thực thi}
Bên cạnh việc đánh giá độ thông dụng của các hành động, chúng tôi còn tập trung vào tìm hiểu những hành động làm ảnh thưởng đến khả năng thực thi của mẫu. Với kết quả huấn luyện qua 1000 episode đối với cả hai mô hình phát hiện là LGBM và MalConv, chúng tôi nhận thấy có đến 98\%. mẫu không thực thi sau khi tác tử thực hiện hàn động thêm mục vào tệp (section\textunderscore add). Tác tử sau khi huấn luyện cũng hạn chế thực hiện hành động này và chủ yếu tập trung vào upx\textunderscore pack.

\begin{figure}[htp]
    \centering
    \includegraphics[width=17cm]{Images/actions-percentage.png}
    \caption{Tỉ lệ của các hành động thực hiện bởi tác tử }
    \label{fig:actions-percentage}
\end{figure}