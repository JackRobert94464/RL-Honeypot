# tested on     
# gym==0.26.2
# gym-notices==0.0.8
 
#gymnasium==0.27.0
#gymnasium-notices==0.0.1
 
# classical gym 
import gym
# instead of gym, import gymnasium 
#import gymnasium as gym
import numpy as np
import time
 
 
# create environment
env=gym.make('CartPole-v1',render_mode='human')
# reset the environment, 
# returns an initial state
(state,_)=env.reset()
# states are
# cart position, cart velocity 
# pole angle, pole angular velocity
