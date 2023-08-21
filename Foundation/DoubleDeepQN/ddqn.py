# import các thư viện cần thiết
import numpy as np
import random
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import RMSprop
from collections import deque 
from tensorflow import gather_nd
from tensorflow.keras.losses import mean_squared_error 

class DeepQLearning:
     
    ###########################################################################
    #   BẮT ĐẦU - hàm __init__
    ###########################################################################
    # INPUTS: 
    # env - Môi trường huấn luyện, ở đây là CartPolev1
    # gamma - hệ số giảm giá trị
    # epsilon - tham số cho chiến lược epsilon-greedy 
    # numberEpisodes - tổng số episodes được huấn luyện
     
    def __init__(self, env, gamma, epsilon, numberEpisodes):
         
        self.env = env
        self.gamma = gamma
        self.epsilon = epsilon
        self.numberEpisodes = numberEpisodes
         
        # kích thước của trạng thái (state) là 4 (x, x_dot, theta, theta_dot)
        self.stateDimension = 4
        # số lượng hành động có thể thực hiện (trái, phải)
        self.actionDimension = 2
        # kích thước của bộ nhớ lưu trữ trạng thái (để lấy mẫu huấn luyện)
        self.replayBufferSize = 300
        # kích thước mẫu huấn luyện được lấy ngẫu nhiên từ buffer trên
        self.batchReplayBufferSize = 100
         
        # số lượng episode cần để cập nhật tham số mạng mục tiêu
        # nghĩa là, mỗi lần cập nhật theo chu kỳ updateTargetNetworkPeriod, ta cập nhật tham số mạng mục tiêu
        self.updateTargetNetworkPeriod = 100
         
        # đây là bộ đếm để cập nhật mạng mục tiêu 
        # nếu bộ đếm này vượt quá (updateTargetNetworkPeriod-1), ta cập nhật mạng 
        # và đặt bộ đếm về 0, quá trình này được lặp lại cho đến cuối quá trình huấn luyện
        self.counterUpdateTargetNetwork = 0
         
        # biến này được sử dụng để lưu tổng thưởng thu được trong mỗi episode
        self.sumRewardsEpisode = []
         
        # bộ đệm lưu trữ các trạng thái
        self.replayBuffer = deque(maxlen=self.replayBufferSize)
         
        # đây là mạng chính (main network)
        # tạo mạng
        self.mainNetwork = self.createNetwork()
         
        # đây là mạng mục tiêu (target network)
        # tạo mạng
        self.targetNetwork = self.createNetwork()
         
        # sao chép trọng số ban đầu sang mạng mục tiêu
        self.targetNetwork.set_weights(self.mainNetwork.get_weights())
         
        # danh sách này được sử dụng trong hàm loss để chọn các mục từ ma trận dự đoán và mẫu thực tế
        # để tạo thành hàm loss
        self.actionsAppend = []
     
    ###########################################################################
    #   KẾT THÚC - hàm __init__
    ###########################################################################
     
    ###########################################################################
    # BẮT ĐẦU - hàm định nghĩa hàm loss
    # INPUTS: 
    #
    # y_true - ma trận kích thước (self.batchReplayBufferSize,2) - đây là mục tiêu 
    # y_pred - ma trận kích thước (self.batchReplayBufferSize,2) - đây là dự đoán bởi mạng
    # 
    # - hàm này sẽ chọn một số hàng từ y_true và y_pred để tạo thành đầu ra 
    # việc lựa chọn được thực hiện dựa trên các index hành động trong danh sách self.actionsAppend
    # - hàm này được sử dụng trong hàm createNetwork(self) để tạo mạng
    #
    # OUTPUT: 
    #    
    # - loss - cẩn thận ở đây, đây là một vector kích thước (self.batchReplayBufferSize,1), 
    # với mỗi mục là bình phương của sai số giữa các mục của y_true và y_pred
    # sau này, TensorFlow sẽ tính toán ra một giá trị số từ vector này (sai số bình phương trung bình)
    ###########################################################################    
     
    def my_loss_fn(self, y_true, y_pred):
         
        s1, s2 = y_true.shape
        #print(s1,s2)
         
        # ma trận này xác định các index của tập hợp mục chúng ta muốn trích xuất từ y_true và y_pred
        # s2=2
        # s1=self.batchReplayBufferSize
        indices = np.zeros(shape=(s1, s2))
        indices[:, 0] = np.arange(s1)
        indices[:, 1] = self.actionsAppend
         
        # gather_nd và mean_squared_error là các hàm của TensorFlow
        loss = mean_squared_error(gather_nd(y_true, indices=indices.astype(int)), gather_nd(y_pred, indices=indices.astype(int)))
        #print(loss)
        return loss    
    ###########################################################################
    #   KẾT THÚC - hàm my_loss_fn
    ###########################################################################
     
    # ... (Các hàm tiếp theo sẽ được dịch trong các phần tiếp theo)
    # ... (Các phần trước đã được dịch ở các phần trước)
     
    ###########################################################################
    #   BẮT ĐẦU - hàm tạo mạng createNetwork()
    # hàm này tạo mạng
    ###########################################################################
     
    # tạo một mạng nơ-ron
    def createNetwork(self):
        model = Sequential()
        model.add(Dense(128, input_dim=self.stateDimension, activation='relu'))
        model.add(Dense(56, activation='relu'))
        model.add(Dense(self.actionDimension, activation='linear'))
        # biên dịch mạng với hàm loss tùy chỉnh đã được định nghĩa trong my_loss_fn
        model.compile(optimizer=RMSprop(), loss=self.my_loss_fn, metrics=['accuracy'])
        return model
    ###########################################################################
    #   KẾT THÚC - hàm tạo mạng createNetwork()
    ###########################################################################
             
    ###########################################################################
    #   BẮT ĐẦU - hàm trainingEpisodes()
    #   - hàm này mô phỏng các episode và gọi hàm huấn luyện 
    #   - trainNetwork()
    ###########################################################################
 
    def trainingEpisodes(self):
    
        # ở đây chúng ta lặp qua các episode
        for indexEpisode in range(self.numberEpisodes):
             
            # danh sách lưu trữ thưởng của từng episode - điều này cần thiết để theo dõi sự hội tụ
            rewardsEpisode = []
                        
            print("Đang mô phỏng episode {}".format(indexEpisode))
             
            # đặt lại môi trường ở đầu mỗi episode
            (currentState, _) = self.env.reset()
                       
            # ở đây chúng ta thực hiện từ một trạng thái đến trạng thái khác
            # quá trình này sẽ lặp lại cho đến khi đạt được trạng thái kết thúc
            terminalState = False
            while not terminalState:
                                       
                # chọn một hành động dựa trên trạng thái hiện tại, được ký hiệu bằng currentState
                action = self.selectAction(currentState, indexEpisode)
                 
                # ở đây chúng ta thực hiện bước và trả về trạng thái, thưởng và cờ biểu thị xem trạng thái có phải là trạng thái kết thúc không
                (nextState, reward, terminalState, _, _) = self.env.step(action)          
                rewardsEpisode.append(reward)
          
                # thêm trạng thái hiện tại, hành động, thưởng, trạng thái kế tiếp và cờ biểu thị trạng thái kết thúc vào bộ đệm lưu trữ
                self.replayBuffer.append((currentState, action, reward, nextState, terminalState))
                 
                # huấn luyện mạng
                self.trainNetwork()
                 
                # đặt trạng thái hiện tại cho bước tiếp theo
                currentState = nextState
             
            print("Tổng thưởng {}".format(np.sum(rewardsEpisode)))        
            self.sumRewardsEpisode.append(np.sum(rewardsEpisode))
    ###########################################################################
    #   KẾT THÚC - hàm trainingEpisodes()
    ###########################################################################
             
    # ... (Các hàm tiếp theo sẽ được dịch trong các phần tiếp theo)
    # ... (Các phần trước đã được dịch ở các phần trước)
     
    ###########################################################################
    #    BẮT ĐẦU - hàm cho việc chọn hành động: phương pháp epsilon-greedy
    ###########################################################################
    # hàm này chọn một hành động dựa trên trạng thái hiện tại
    # INPUTS: 
    # state - trạng thái để tính toán hành động
    # index - index của episode hiện tại
    def selectAction(self, state, index):
        import numpy as np
         
        # trong index đầu tiên của các episode, chúng ta chọn hoàn toàn ngẫu nhiên các hành động để đảm bảo có đủ sự khám phá
        if index < 1:
            return np.random.choice(self.actionDimension)   
             
        # Trả về một số thực ngẫu nhiên trong khoảng bán mở [0.0, 1.0)
        # số này được sử dụng cho phương pháp epsilon-greedy
        randomNumber = np.random.random()
         
        # sau index episode, chúng ta bắt đầu từ từ giảm tham số epsilon
        if index > 200:
            self.epsilon = 0.999 * self.epsilon
         
        # nếu điều kiện này được đáp ứng, chúng ta đang khám phá, tức là chúng ta chọn hành động ngẫu nhiên
        if randomNumber < self.epsilon:
            # trả về một hành động ngẫu nhiên được chọn từ: 0,1,...,actionNumber-1
            return np.random.choice(self.actionDimension)            
         
        # ngược lại, chúng ta đang chọn hành động tham lam
        else:
            # chúng ta trả về index mà Qvalues[state,:] có giá trị tối đa
            # tức là, vì index xác định một hành động, chúng ta chọn hành động tham lam
                        
            Qvalues = self.mainNetwork.predict(state.reshape(1, 4))
           
            return np.random.choice(np.where(Qvalues[0, :] == np.max(Qvalues[0, :]))[0])
            # ở đây chúng ta cần trả về index nhỏ nhất vì có thể xảy ra
            # rằng có một số mục tối đa trùng nhau, ví dụ 
            # import numpy as np
            # a = [0, 1, 1, 0]
            # np.where(a == np.max(a))
            # điều này sẽ trả về [1, 2], nhưng chúng ta chỉ cần một index duy nhất
            # đó là tại sao chúng ta cần có np.random.choice(np.where(a == np.max(a))[0])
            # lưu ý rằng số không phải được thêm ở đây vì np.where() trả về một tuple
    ###########################################################################
    #    KẾT THÚC - hàm chọn hành động: phương pháp epsilon-greedy
    ###########################################################################
     
    ###########################################################################
    #    BẮT ĐẦU - hàm trainNetwork() - hàm này huấn luyện mạng
    ###########################################################################
     
    def trainNetwork(self):
 
        # nếu bộ đệm lưu trữ có ít nhất batchReplayBufferSize phần tử,
        # chúng ta sẽ tiến hành huấn luyện mô hình 
        # nếu không, đợi cho đến khi kích thước các phần tử vượt quá batchReplayBufferSize
        if len(self.replayBuffer) > self.batchReplayBufferSize:
             
            # lấy một mẫu từ bộ đệm lưu trữ
            randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
             
            # ở đây chúng ta hình thành mẫu trạng thái hiện tại 
            # và mẫu trạng thái kế tiếp
            # chúng được sử dụng làm đầu vào để dự đoán
            currentStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))
            nextStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))            
            # cái này sẽ liệt kê các mục của tuple trong randomSampleBatch
            # index sẽ lặp qua số tuple
            for index, tupleS in enumerate(randomSampleBatch):
                # mục đầu tiên của tuple là trạng thái hiện tại
                currentStateBatch[index, :] = tupleS[0]
                # mục thứ tư của tuple là trạng thái kế tiếp
                nextStateBatch[index, :] = tupleS[3]
             
            # ở đây, sử dụng mạng mục tiêu để dự đoán các giá trị Q 
            QnextStateTargetNetwork = self.targetNetwork.predict(nextStateBatch)
            # ở đây, sử dụng mạng chính để dự đoán các giá trị Q 
            QcurrentStateMainNetwork = self.mainNetwork.predict(currentStateBatch)
             
            # bây giờ, chúng ta hình thành các mẫu để huấn luyện
            # đầu vào cho huấn luyện
            inputNetwork = currentStateBatch
            # đầu ra cho huấn luyện
            outputNetwork = np.zeros(shape=(self.batchReplayBufferSize, 2))
             
            # danh sách này sẽ chứa các hành động được chọn từ mẫu 
            # danh sách này được sử dụng trong my_loss_fn để định nghĩa hàm loss
            self.actionsAppend = []            
            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                 
                # nếu trạng thái kế tiếp là trạng thái kết thúc
                if terminated:
                    y = reward                  
                # nếu trạng thái kế tiếp không phải là trạng thái kết thúc    
                else:
                    y = reward + self.gamma * np.max(QnextStateTargetNetwork[index])
                 
                # điều này cần thiết để định nghĩa hàm loss
                self.actionsAppend.append(action)
                 
                # thực ra điều này không quan trọng vì chúng ta không sử dụng tất cả các mục trong hàm loss
                outputNetwork[index] = QcurrentStateMainNetwork[index]
                # đây mới là điều quan trọng
                outputNetwork[index, action] = y
             
            # ở đây, chúng ta huấn luyện mạng
            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=0, epochs=100)     
             
            # sau updateTargetNetworkPeriod phiên huấn luyện, cập nhật hệ số 
            # của mạng mục tiêu
            # tăng bộ đếm cho việc huấn luyện mạng mục tiêu
            self.counterUpdateTargetNetwork += 1 
            if self.counterUpdateTargetNetwork > (self.updateTargetNetworkPeriod - 1):
                # sao chép trọng số đến mạng mục tiêu
                self.targetNetwork.set_weights(self.mainNetwork.get_weights())        
                print("Cập nhật mạng mục tiêu!")
                print("Giá trị bộ đếm {}".format(self.counterUpdateTargetNetwork))
                # đặt lại bộ đếm
                self.counterUpdateTargetNetwork = 0
    ###########################################################################
    #    KẾT THÚC - hàm trainNetwork() 
    ########################################################################### 

# ... (Kết thúc mã)
