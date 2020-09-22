from core import Core
from solver2 import moveAITrain
from alphabeta import moveAINN
from model import Model
import copy
import numpy as np
import random
import time
import model
import mcts
from datetime import datetime
import pickle
import os

roteMap = list([56,48,40,32,24,16,8,0,57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,28,20,12,4,61,53,45,37,29,21,13,5,62,54,46,38,30,22,14,6,63,55,47,39,31,23,15,7])
reveMap = list([56,57,58,59,60,61,62,63,48,49,50,51,52,53,54,55,40,41,42,43,44,45,46,47,32,33,34,35,36,37,38,39,24,25,26,27,28,29,30,31,16,17,18,19,20,21,22,23,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7])
bitTable = [0]*64
hash = 0x03F566ED27179461
for i in range(64):
    bitTable[ hash >> 58 ] = i
    hash <<= 1
    hash &= 0xffffffffffffffff

NUM_GAMES = 1

def bitFind(bit):
    return int((bit*hash) >> 58 )

def BitArray(bit):
    jglist = list(reversed((("0" * 64) + bin(int(bit) & 0xffffffffffffffff)[2:])[-64:]))
    return np.array(jglist, dtype=int)

def ReveBit(bit):
    return   ((bit << 56)|(bit << 40 & 0x00ff000000000000)|(bit << 24 & 0x0000ff0000000000)|(bit << 8 & 0x000000ff00000000)
        |(bit >> 8 & 0x00000000ff000000)|(bit >> 24 & 0x0000000000ff0000)|(bit >> 40 & 0x000000000000ff00)|(bit >> 56))

def RoteBit(bit):
    t  = 0x0f0f0f0f00000000 & (bit ^ (bit << 28))
    bit ^=       t ^ (t >> 28)
    t  = 0x3333000033330000 & (bit ^ (bit << 14))
    bit ^=       t ^ (t >> 14)
    t  = 0x5500550055005500 & (bit ^ (bit <<  7))
    b = bit ^ t ^ (t >>  7)

    t = (b ^ (b >>  7)) & 0x0101010101010101
    b ^= t ^ (t <<  7)
    t = (b ^ (b >>  5)) & 0x0202020202020202
    b ^= t ^ (t <<  5)
    t = (b ^ (b >>  3)) & 0x0404040404040404
    b ^= t ^ (t <<  3)
    t = (b ^ (b >>  1)) & 0x0808080808080808
    b ^= t ^ (t <<  1)
    return b

def Rote(x,pi):
    a = np.array([pi[roteMap[i]] for i in range(64)])
    features = []
    features.append(RoteBit(x[0]))
    features.append(RoteBit(x[1]))
    features.append(RoteBit(x[2]))
    return features,a
        
def Reve(x,pi):
    a = np.array([pi[reveMap[i]] for i in range(64)])
    features = []
    features.append(ReveBit(x[0]))
    features.append(ReveBit(x[1]))
    features.append(ReveBit(x[2]))
    return features,a

class SelfPlay(Core):

    def __init__(self):
        super().__init__(0, 0x0000001008000000, 0x0000000810000000)
        self.start = time.time()
        self.model = Model()
        self.model.load("model/Gen" + str(0))
        self.score = 0
        self.table = {}
        self.history = []
        self.currentNode = mcts.Node(mcts.FakeNode(), 0, 0, Core(self.turn, self.black, self.white))
        self.currentNode.isGameRoot = True
        self.currentNode.isSearchRoot = True
        self.mctsBatch = mcts.MCTSBatch(self.model)
        self.table = {}

    def InputPlayer(self):
        nb, nw = self.Count()
        nmTurn = 64 - nb - nw
        if nmTurn < 54:
            self.currentNode = mcts.Node(mcts.FakeNode(), 0, self.turn, Core(self.turn, self.black, self.white))
            self.currentNode.isGameRoot = True
            self.currentNode.isSearchRoot = True
            pi = self.mctsBatch.alpha([self.currentNode],  0.98^(nb+nw))[0]

            self.addHistory(pi,self.turn)

            self.currentNode = self.makeMove(self.currentNode,int(np.argmax(pi)))
        else:
            while True:
                move = random.randrange(0, 64)
                site = 1 << move
                if self.judge & site:
                    # self.AddSite(site)
                    self.currentNode = self.makeMove(self.currentNode,move)
                    break            

    def addHistoryRote(self):
        temp = copy.deepcopy(self.history)
        for i in temp:
            features = i[0]
            pi = i[1]
            features,pi = Rote(features,pi)
            self.history.append([features,pi,i[2]])
            features,pi = Rote(features,pi)
            self.history.append([features,pi,i[2]])
            features,pi = Rote(features,pi)
            self.history.append([features,pi,i[2]])
            features,pi = Reve(features,pi)
            self.history.append([features,pi,i[2]])
            features,pi = Rote(features,pi)
            self.history.append([features,pi,i[2]])
            features,pi = Rote(features,pi)
            self.history.append([features,pi,i[2]])
            features,pi = Rote(features,pi)
            self.history.append([features,pi,i[2]])

    def addHistory(self,pi,val):
        features = []
        features.append(self.black)
        features.append(self.white)
        features.append(self.judge)
        self.history.append([features,pi,val])

    def addValue(self,his,val):
        for i in range(len(his)):
            if his[i][2]:
                his[i][2] = val
            else:
                his[i][2] = -val
            

    def InputEnemy(self):
        nb, nw = self.Count()
        nmTurn = 64 - nb - nw
        if nmTurn < 14:
            site,maxScore,sumScore,self.table = moveAITrain(self.black,self.white,self.turn, nmTurn, self.table, nw-nb)
            if maxScore > 0:
                maxScore = (maxScore+64)/128
            elif maxScore < 0:
                maxScore = (maxScore-64)/128
            pi = np.zeros([64])
            for move in site:
                pi[bitFind(move[1])] = move[0]/sumScore
            self.addHistory(pi,self.turn)
            temp = copy.deepcopy(self.history)
            self.addValue(self.history,maxScore)

            for i in range(len(site)//4+1):
                history2 = copy.deepcopy(temp)
                self.AddSite(site[i][1])
                self.NextBoard()
                site2,maxScore2,sumScore2,self.table = moveAITrain(self.black,self.white,self.turn^1, nmTurn-1, self.table, nw-nb)
                self.NextBoard()
                maxScore2 = -maxScore2
                if maxScore2 > 0:
                    maxScore2 = (maxScore2+64)/128
                elif maxScore2 < 0:
                    maxScore2 = (maxScore2-64)/128
                pi2 = np.zeros([64])
                for move2 in site2:
                    pi2[bitFind(move2[1])] = move2[0]/sumScore2
                features = []
                features.append(self.black)
                features.append(self.white)
                features.append(self.judge)
                history2.append([features,pi2,self.turn^1])
                self.addValue(history2,maxScore2)
                self.history.extend(history2)



            self.AddSite(0)
        elif nmTurn < 54:
            self.currentNode = mcts.Node(mcts.FakeNode(), 0, self.turn, Core(self.turn, self.black, self.white))
            self.currentNode.isGameRoot = True
            self.currentNode.isSearchRoot = True
            pi = self.mctsBatch.alpha([self.currentNode],  0.98^(nb+nw))[0]

            self.addHistory(pi/np.sum(pi),self.turn)
            
            self.currentNode = self.makeMove(self.currentNode,int(np.argmax(pi)))
        else:
            while True:
                move = random.randrange(0, 64)
                site = 1 << move
                if self.judge & site:
                    # self.AddSite(site)
                    self.currentNode = self.makeMove(self.currentNode,move)
                    break
        
    def makeMove(self, node, move):
        if move not in node.childNodes:
            node = mcts.Node(node, move, node.turn^1)
        else:
            node = node.childNodes[move]
        node.isSearchRoot = True
        node.parent.childNodes.clear()
        node.parent.isSearchRoot = False
        site = 1 << move
        if self.judge & site:
            self.AddSite(site)
        else:
            print("いや,打てへんやん")
            exit()
        return node

    def Input(self, black, white):
        if not self.turn:
            black()
        else:
            white()

    def gameFlow(self):
        while True:
            if self.PassEnd():
                self.addHistoryRote()
                return self.history
            self.Input(self.InputPlayer, self.InputEnemy)
            if not self.put:
                self.addHistoryRote()
                return self.history
            self.NextBoard()
            self.NextTurn()

def writeData(history):
    now = datetime.now()
    os.makedirs('./data/', exist_ok=True)
    path = './data/{:04}{:02}{:02}{:02}{:02}.history'.format(
        now.year, now.month, now.day, now.hour, now.minute)
    with open(path, mode='wb') as f:
        pickle.dump(history, f)

if __name__ == "__main__":
    history = []
    for i in range(NUM_GAMES):
        print()
        game = SelfPlay()
        history.extend(game.gameFlow())
        print(time.time()-game.start)
    writeData(history)