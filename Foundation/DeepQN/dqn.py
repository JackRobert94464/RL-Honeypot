# Nhập các thư viện cần thiết
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
    # ĐẦU VÀO: 
    # env - Môi trường Cart Pole
    # gamma - tỷ lệ chiết khấu
    # epsilon - tham số cho phương pháp epsilon-greedy
    # numberEpisodes - tổng số episode mô phỏng
     
             
    def __init__(self, env, gamma, epsilon, numberEpisodes):
         
         
        self.env = env
        self.gamma = gamma
        self.epsilon = epsilon
        self.numberEpisodes = numberEpisodes
         
        # Kích thước trạng thái
        self.stateDimension = 4
        # Kích thước hành động
        self.actionDimension = 2
        # Đây là kích thước tối đa của bộ đệm lưu trữ trạng thái (replay buffer)
        self.replayBufferSize = 300
        # Đây là kích thước của lô huấn luyện được lấy ngẫu nhiên từ bộ đệm lưu trữ (replay buffer)
        self.batchReplayBufferSize = 100
         
        # Biến này được sử dụng để lưu tổng của các phần thưởng thu được trong mỗi episode huấn luyện
        self.sumRewardsEpisode = []
         
        # Bộ đệm lưu trữ trạng thái (replay buffer)
        self.replayBuffer = deque(maxlen=self.replayBufferSize)
         
        # Đây là mạng chính (main network). DQN dùng mạng này cho cả 2 việc sau:
        # 1. Dự đoán giá trị Q cho một trạng thái - Target network
        # 2. Lựa chọn hành động tốt nhất cho trạng thái tiếp theo dựa trên kết quả của mạng Target - Main network
        # Tạo mạng
        self.mainNetwork = self.createNetwork()
         
        # Danh sách này được sử dụng trong hàm chi phí để chọn các mục cụ thể của ma trận dự đoán và mẫu thực sự để tạo hàm loss
        self.actionsAppend = []
     
    ###########################################################################
    #   KẾT THÚC - hàm __init__
    ###########################################################################
     
    ###########################################################################
    # BẮT ĐẦU - hàm định nghĩa hàm loss (cost function)
    # ĐẦU VÀO: 
    #
    # y_true - ma trận có kích thước (self.batchReplayBufferSize, 2) - đây là mục tiêu dự đoán cần đạt
    # y_pred - ma trận có kích thước (self.batchReplayBufferSize, 2) - đây là dự đoán của mạng
    # 
    # - hàm này sẽ chọn một số mục cụ thể từ y_true và y_pred để tạo đầu ra 
    # việc chọn lựa này được thực hiện dựa trên index các hành động của danh sách self.actionsAppend (lấy các hành động được chọn từ các lần huấn luyện trước)
    # - hàm này được sử dụng trong hàm createNetwork(self) để tạo mạng
    #
    # ĐẦU RA: 
    #    
    # - loss - chú ý ở đây, đây là một vector có kích thước (self.batchReplayBufferSize, 1), 
    # với mỗi mục là bình phương sai số (mean square error) giữa các mục của y_true và y_pred
    # sau đó, TensorFlow sẽ tính toán giá trị scalar từ vector này (mean squared error)
    ###########################################################################    
     
    def my_loss_fn(self, y_true, y_pred):
         
        s1, s2 = y_true.shape
        #print(s1, s2)
         
        # ma trận này xác định index của tập hợp các mục mà chúng ta muốn 
        # trích xuất từ y_true và y_pred
        # s2=2
        # s1=self.batchReplayBufferSize
        indices = np.zeros(shape=(s1, s2))
        indices[:, 0] = np.arange(s1)
        indices[:, 1] = self.actionsAppend
         
        # gather_nd và mean_squared_error là các hàm TensorFlow
        loss = mean_squared_error(gather_nd(y_true, indices=indices.astype(int)), gather_nd(y_pred, indices=indices.astype(int)))
        #print(loss)
        return loss    
    ###########################################################################
    #   KẾT THÚC - của hàm my_loss_fn
    ###########################################################################
     
    ###########################################################################
    #   BẮT ĐẦU - hàm tạo mạng (createNetwork())
    # hàm này tạo mạng
    ###########################################################################
     
    # tạo một mạng neural
    def createNetwork(self):
        model = Sequential()
        model.add(Dense(128, input_dim=self.stateDimension, activation='relu'))
        model.add(Dense(56, activation='relu'))
        model.add(Dense(self.actionDimension, activation='linear'))
        # biên dịch mạng với hàm loss tùy chỉnh được định nghĩa trong my_loss_fn
        model.compile(optimizer=RMSprop(), loss=self.my_loss_fn, metrics=['accuracy'])
        return model
    ###########################################################################
    #   KẾT THÚC - hàm tạo mạng (createNetwork())
    ###########################################################################
             
    ###########################################################################
    #   BẮT ĐẦU - hàm trainingEpisodes()
    #   - hàm này mô phỏng các episode và gọi hàm huấn luyện 
    #   - trainNetwork()
    ###########################################################################

    def trainingEpisodes(self):
        for indexEpisode in range(self.numberEpisodes):
            rewardsEpisode = []
            print("Đang mô phỏng episode {}".format(indexEpisode))
            (currentState, _) = self.env.reset()
            terminalState = False
            while not terminalState:
                action = self.selectAction(currentState, indexEpisode)
                (nextState, reward, terminalState, _, _) = self.env.step(action)
                rewardsEpisode.append(reward)
                self.replayBuffer.append((currentState, action, reward, nextState, terminalState))
                self.trainNetwork()
                currentState = nextState
            print("Tổng phần thưởng {}".format(np.sum(rewardsEpisode)))
            self.sumRewardsEpisode.append(np.sum(rewardsEpisode))

    ###########################################################################
    #   KẾT THÚC - hàm trainingEpisodes()
    ###########################################################################
             
        
    ###########################################################################
    #    BẮT ĐẦU - hàm chọn hành động: phương pháp epsilon-greedy
    ###########################################################################
    # hàm này chọn một hành động dựa trên trạng thái hiện tại 
    # ĐẦU VÀO: 
    # state - trạng thái để tính toán hành động
    # index - index của episode hiện tại
    def selectAction(self, state, index):
        import numpy as np
         
        # trong những episode đầu tiên, chúng ta chọn các hành động hoàn toàn ngẫu nhiên để khám phá
        # có thể tăng số index này lên để khám phá nhiều hơn
        if index < 1:
            return np.random.choice(self.actionDimension)   
             
        # Trả về một số thực ngẫu nhiên trong khoảng [0.0, 1.0)
        # số này dùng cho phương pháp epsilon-greedy
        randomNumber = np.random.random()
         
        # sau số lượng episode index nhất định, chúng ta bắt đầu từ từ giảm tham số epsilon
        if index > 200:
            self.epsilon = 0.999 * self.epsilon
         
        # nếu điều kiện này được đáp ứng, chúng ta đang thăm dò, tức là chúng ta chọn các hành động ngẫu nhiên
        if randomNumber < self.epsilon:
            # trả về một hành động ngẫu nhiên được chọn từ: 0,1,...,actionNumber-1
            return np.random.choice(self.actionDimension)            
         
        # nếu không, chúng ta đang chọn các hành động tham lam
        else:
            # chúng ta trả về index trong đó Qvalues[state,:] có giá trị lớn nhất
            # tức là, vì index đại diện cho một hành động, chúng ta chọn các hành động tham lam
                        
            Qvalues = self.mainNetwork.predict(state.reshape(1, 4))
           
            return np.random.choice(np.where(Qvalues[0, :] == np.max(Qvalues[0, :]))[0])
            # ở đây chúng ta cần trả về index tối thiểu vì có thể xảy ra
            # rằng có một số mục cực đại giống nhau, ví dụ 
            # import numpy as np
            # a = [0, 1, 1, 0]
            # np.where(a == np.max(a))
            # điều này sẽ trả về [1, 2], nhưng chúng ta chỉ cần một index duy nhất
            # đó là lý do tại sao chúng ta cần có np.random.choice(np.where(a == np.max(a))[0])
            # lưu ý rằng phải thêm số không ở đây vì np.where() trả về một tuple
    ###########################################################################
    #    KẾT THÚC - hàm chọn hành động: phương pháp epsilon-greedy
    ###########################################################################
     
    ###########################################################################
    #    BẮT ĐẦU - hàm trainNetwork() - hàm này huấn luyện mạng
    ###########################################################################

    def trainNetwork(self):
        if len(self.replayBuffer) > self.batchReplayBufferSize:
            randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
            
            currentStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))
            nextStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))

            for index, tupleS in enumerate(randomSampleBatch):
                currentStateBatch[index, :] = tupleS[0]
                nextStateBatch[index, :] = tupleS[3]

            QcurrentStateMainNetwork = self.mainNetwork.predict(currentStateBatch)
            QnextStateMainNetwork = self.mainNetwork.predict(nextStateBatch)

            inputNetwork = currentStateBatch
            outputNetwork = np.zeros(shape=(self.batchReplayBufferSize, self.actionDimension))

            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                self.actionsAppend.append(action)  # Thêm hành động vào danh sách
                target = reward

                if not terminated:
                    target += self.gamma * np.max(QnextStateMainNetwork[index])

                outputNetwork[index] = QcurrentStateMainNetwork[index]
                outputNetwork[index, action] = target

            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=0, epochs=1)

    ###########################################################################
    #    KẾT THÚC - hàm trainNetwork() 
    ########################################################################### 
