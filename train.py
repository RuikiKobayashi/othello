from core import Core
from solver2 import moveAITrain
from alphabeta import moveAINN
from model import Model
import numpy as np
import model
import mcts
import pickle
import os
from pathlib import Path
from keras.utils import plot_model


def BitArray(bits):
    jglist = np.zeros([3,8,8],dtype='f4')
    jglist[0] = np.array(list(reversed((("0" * 64) + bin(bits[0] & 0xffffffffffffffff)[2:])[-64:]))).reshape([8,8])
    jglist[1] = np.array(list(reversed((("0" * 64) + bin(bits[1] & 0xffffffffffffffff)[2:])[-64:]))).reshape([8,8])
    jglist[2] = np.array(list(reversed((("0" * 64) + bin(bits[0] & 0xffffffffffffffff)[2:])[-64:]))).reshape([8,8])
    return jglist

def loadData():
    historyPath = sorted(Path('./data').glob('*.history'))[-1]
    with historyPath.open(mode='rb') as f:
        return pickle.load(f)

class Train:
    def __init__(self,modelGen = None):
        self.model = Model()
        if modelGen != None:
            self.model.load("model/Gen" + str(modelGen))
            self.modelGen = modelGen
    
    def train(self):
        history = loadData()
        xsbit, policies, values = zip(*history)
        xs = np.array([BitArray(x) for x in xsbit])
        self.model.fit(xs,np.array(policies),np.array(values))
        self.model.save("model/Gen" + str(0))

if __name__ == "__main__":
    game = Train(0)
    game.train()
    

