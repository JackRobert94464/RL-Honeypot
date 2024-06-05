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