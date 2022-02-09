import gym
from gym import spaces
import numpy as np
import cv2
import random
import time
from collections import deque

SNAKE_LEN_GOAL = 30

def collision_with_apple(apple_position, score):
	apple_position = [random.randrange(1,50)*10,random.randrange(1,50)*10]
	score += 1
	return apple_position, score

def collision_with_boundaries(snake_head):
	if snake_head[0]>=500 or snake_head[0]<0 or snake_head[1]>=500 or snake_head[1]<0 :
		return 1
	else:
		return 0

def collision_with_self(snake_position):
	snake_head = snake_position[0]
	if snake_head in snake_position[1:]:
		return 1
	else:
		return 0
	
class SnekEnv(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self):
        super(SnekEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(4)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=-500, high=500,
											shape=(5 + SNAKE_LEN_GOAL,), dtype=np.float32)

    def step(self, action):
        self.prev_actions.append(action)
        
        self.img = np.zeros((500,500,3),dtype='uint8')
        # Display Apple
        cv2.rectangle(self.img,(self.apple_position[0],self.apple_position[1]),(self.apple_position[0]+10, self.apple_position[1]+10),(0,0,255),3)
        # Display Snake
        for position in self.snake_position:
            cv2.rectangle(self.img,(position[0],position[1]),(position[0]+10,position[1]+10),(0,255,0),3)

        prev_apple_d_x = self.snake_head[0] - self.apple_position[0]
        prev_apple_d_y = self.snake_head[1] - self.apple_position[1]
                
        # 0-Left, 1-Right, 3-Up, 2-Down, q-Break
        # a-Left, d-Right, w-Up, s-Down

        # Change the head position based on the button direction
        if action == 1:
            self.snake_head[0] += 10
        elif action == 0:
            self.snake_head[0] -= 10
        elif action == 2:
            self.snake_head[1] += 10
        elif action == 3:
            self.snake_head[1] -= 10

        apple_reward = 0
        # Increase Snake length on eating apple
        if self.snake_head == self.apple_position:
            self.apple_position, score = collision_with_apple(self.apple_position, self.score)
            self.snake_position.insert(0,list(self.snake_head))
            apple_reward = 1000

        else:
            self.snake_position.insert(0,list(self.snake_head))
            self.snake_position.pop()
            
        # On collision kill the snake and print the score
        if collision_with_boundaries(self.snake_head) == 1 or collision_with_self(self.snake_position) == 1:
            self.img = np.zeros((500,500,3),dtype='uint8')
            self.done = True

        head_x = self.snake_head[0]
        head_y = self.snake_head[1]

        apple_d_x = head_x - self.apple_position[0]
        apple_d_y = head_y - self.apple_position[1]

        snake_length = len(self.snake_position)

        self.observation = [head_x, head_y, apple_d_x, apple_d_y, snake_length] + list(self.prev_actions)
        self.observation = np.array(self.observation)

        if abs(prev_apple_d_x) > abs(apple_d_x) or abs(prev_apple_d_y) > abs(apple_d_y):
            dir_reward = 10
        else:
            dir_reward = -5

        if self.done:
            self.reward = -100
        else:
            self.reward = apple_reward + dir_reward

        info = {}
        return self.observation, self.reward, self.done, info

    def reset(self):
        self.done = False
        self.img = np.zeros((500,500,3),dtype='uint8')

        # Initial Snake and Apple position
        self.snake_position = [[250,250],[240,250],[230,250]]
        self.apple_position = [random.randrange(1,50)*10,random.randrange(1,50)*10]
        self.score = 0
        self.reward= 0
        self.prev_button_direction = 1
        self.button_direction = 1
        self.snake_head = [250,250]

        #head_x, head_y, apple_d_x, apple_d_y, snake_length, previous moves
        head_x = self.snake_head[0]
        head_y = self.snake_head[1]

        apple_d_x = head_x - self.apple_position[0]
        apple_d_y = head_y - self.apple_position[1]

        snake_length = len(self.snake_position)

        self.prev_actions = deque(maxlen=SNAKE_LEN_GOAL)
        for _ in range(SNAKE_LEN_GOAL):
            self.prev_actions.append(-1)

        self.observation = [head_x, head_y, apple_d_x, apple_d_y, snake_length] + list(self.prev_actions)
        self.observation = np.array(self.observation)


        return self.observation  # reward, done, info can't be included

    def render(self):
        cv2.imshow('a', self.img)
        cv2.waitKey(100)