import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import gym # for environment
import tensorflow as tf
import scipy.io
import matplotlib.pyplot as plt
from tensorflow import keras
from collections import deque
from keras.models import Sequential
from keras.layers import Dense # adaptive momentum 
import random

class DQLAgent(): 
    
    def __init__(self, env):
        # parameters and hyperparameters
        
        # this part is for neural network or build_model()
        self.state_size = env.observation_space.shape[0] # this is for input of neural network node size
        self.action_size = env.action_space.n # this is for out of neural network node size
        
        # this part is for replay()
        self.gamma = 0.95
        self.learning_rate = 0.001
        
        # this part is for adaptiveEGreedy()
        self.epsilon = 1 # initial exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        self.memory = deque(maxlen = 1000) # a list with 1000 memory, if it becomes full first inputs will be deleted
        
        self.model = self.build_model()
    
    def build_model(self):
        # neural network for deep Q learning
        model = Sequential()
        model.add(Dense(48, input_dim = self.state_size, activation = 'tanh')) # first hidden layer
        model.add(Dense(self.action_size, activation = 'linear')) # output layer
        model.compile(loss = 'mse', optimizer=keras.optimizers.Adam(lr = self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        # storage
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        # acting, exploit or explore
        if random.uniform(0,1) <= self.epsilon:
            return env.action_space.sample()
        else:
            act_values = self.model.predict(state)
            return np.argmax(act_values[0])
            
    
    def replay(self, batch_size):
        # training
        
        if len(self.memory) < batch_size:
            return # memory is still not full
        
        minibatch = random.sample(self.memory, batch_size) # take 16 (batch_size) random samples from memory
        for state, action, reward, next_state, done in minibatch:
            if done: # if the game is over, I dont have next state, I just have reward 
                target = reward
            else:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0]) 
                # target = R(s,a) + gamma * max Q`(s`,a`)
                # target (max Q` value) is output of Neural Network which takes s` as an input 
                # amax(): flatten the lists (make them 1 list) and take max value
            train_target = self.model.predict(state) # s --> NN --> Q(s,a)=train_target
            train_target[0][action] = target
            self.model.fit(state, train_target, verbose = 0) # verbose: dont show loss and epoch
    
    def adaptiveEGreedy(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            

if __name__ == "__main__":
    
    # initialize gym environment and agent
    env = gym.make('CartPole-v1')
    agent = DQLAgent(env)
    score = 0
    scores = []
    batch_size = 16
    EPISODES = 100
    for e in range(EPISODES):
        
        # initialize environment
        state = env.reset()
        state = np.reshape(state, [1,4])
        render_start = False
        render_end = False
        score = 0
        
        for time_p in range(500):
            if render_start:
                env.render()
    

            # act
            action = agent.act(state)
            
            # step
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1,4])
            
            # remember / storage
            agent.remember(state, action, reward, next_state, done)
            score += reward
            # update state
            state = next_state
            
            # replay
            agent.replay(batch_size)
            
            # adjust epsilon
            agent.adaptiveEGreedy()
            
            if done:
                scores.append(score)
                print('episode: {}/{}, score: {}'.format(e+1, EPISODES, score))
                break
        if render_end:
            env.close()
            
episodes = [i for i in range(len(scores))]
plt.figure(figsize=(8, 8))
plt.plot(episodes, scores)
plt.xlabel("Episodes")
plt.ylabel("Scores")
plt.title("DQL_AGENT Performance")
plt.show()
agent.model.save("qlearning.h5")