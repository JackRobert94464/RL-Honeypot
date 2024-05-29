import os
import numpy as np
import random
from keras.layers import InputLayer, Input, Dense, Concatenate
from keras.models import Sequential, Model
from keras.optimizers import RMSprop, Adam
from collections import deque 
from tensorflow import gather_nd
from keras.losses import mean_squared_error, huber
from math import factorial
import keras
import pandas as pd
import time
import tensorflow as tf

class DoubleDeepQLearning:
    def __init__(self, stateDimension, actionDimension):
        self.stateDimension = stateDimension
        self.actionDimension = actionDimension

        self.network = self.createNetwork()


    def ddqn_loss_fn(y_true, y_pred):
        loss = tf.losses.categorical_crossentropy(y_true, y_pred)
        return loss


    def createNetwork(self):
        # Define input layers for each type of input data
        observable_input = tf.keras.layers.Input(shape=(self.stateDimension,))
        epss_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        ntpg_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        
        # First interpretation model
        obs = tf.keras.layers.Dense(32, activation='relu')(observable_input)

        # Branch 2: Process EPSS matrix
        epss = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(epss_input)
        epss = tf.keras.layers.BatchNormalization()(epss)
        epss = tf.keras.layers.GlobalAveragePooling1D()(epss)

        # Branch 3: Process ntpg penetration graph
        ntpg = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(ntpg_input)
        ntpg = tf.keras.layers.BatchNormalization()(ntpg)
        ntpg = tf.keras.layers.GlobalAveragePooling1D()(ntpg)

        # Concatenate the outputs of all branches
        concatenated = tf.keras.layers.Concatenate()([obs, epss, ntpg])

        
        # Giu nguyen cac lop nay de cho cac model sau nay
        # Interpreting the concatenated data
        x = tf.keras.layers.Dense(64, activation='relu')(concatenated)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)

        # model output
        output = tf.keras.layers.Dense(self.actionDimension, activation='tanh')(x)

        # Create model
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)

        # Compile model
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer='adam', metrics=['accuracy'])
        print("Created network:", model.summary())
        # os.system("pause")
        return model

if __name__ == '__main__':
    batch_size = 16
    stateDimension = 10
    actionDimension = 100

    obs = np.random.rand(batch_size, stateDimension)
    epss = np.random.rand(batch_size, stateDimension, stateDimension)
    ntpg = np.random.rand(batch_size, stateDimension, stateDimension)

    dqn = DoubleDeepQLearning(stateDimension, actionDimension)

    output = dqn.network([obs, epss, ntpg])
    print(output)