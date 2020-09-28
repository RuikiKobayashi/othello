import math

import numpy as np
from core_c import Core

C_PUCT = 1.0
NOISE_WEIGHT = 0.25
NOISE_ALPHA = 0.5


class FakeNode:
    def __init__(self):
        self.parent = None
        self.edgeN = np.zeros([64], dtype=float)
        self.edgeW = np.zeros([64], dtype=float)

def BitArray(bit):
    jglist = list(reversed((("0" * 64) + bin(int(bit) & 0xffffffffffffffff)[2:])[-64:]))
    return np.array(jglist, dtype=int)

class Node:
    def __init__(self, parent, move, turn, game:Core = None):
        self.parent = parent
        self.expanded = False
        self.move = move
        self.turn = turn
        if game:
            self.game = game
            game.AddJudge()
        else: 
            bitMove = 1 << int(move)
            self.parent.game.AddSite(bitMove)
            self.parent.game.NextBoard()
            self.game = Core(turn,self.parent.game.black,self.parent.game.white)
            self.game.AddJudge()

        self.legalMoves = BitArray(self.game.judge)
        self.childNodes = {}
        self.isGameRoot = False
        self.isSearchRoot = False
        self.isTerminal = False
        self.pi = np.zeros([64], dtype=float)
        self.edgeN = np.zeros([64], dtype=float)
        self.edgeW = np.zeros([64], dtype=float)
        self.edgeP = np.zeros([64], dtype=float)

    @property
    def edgeQ(self):
        return self.edgeW / (self.edgeN + (self.edgeN == 0))

    @property
    def edgeU(self):
        return C_PUCT * self.edgeP * math.sqrt(max(1, self.selfN)) / (1 + self.edgeN)

    @property
    def edgeUNoise(self):
        noise = NormalizeMask(np.random.dirichlet([NOISE_ALPHA] * 64), self.legalMoves)
        pWithNoise = self.edgeP * (1 - NOISE_WEIGHT) + noise * NOISE_WEIGHT
        return C_PUCT * pWithNoise * math.sqrt(max(1, self.selfN)) / (1 + self.edgeN)

    @property
    def edgeQU(self):
        if self.isSearchRoot:
            return self.edgeQ * self.turn + self.edgeUNoise + self.legalMoves * 1000
        else:
            return self.edgeQ * self.turn + self.edgeU + self.legalMoves * 1000

    @property
    def selfN(self):
        return self.parent.edgeN[self.move]

    @selfN.setter
    def selfN(self, n):
        self.parent.edgeN[self.move] = n

    @property
    def selfW(self):
        return self.parent.edgeW[self.move]

    @selfW.setter
    def selfW(self, w):
        self.parent.edgeW[self.move] = w

    def toFeatures(self):
        features = np.zeros([3, 64], dtype=float)
        turn = self.turn
        if turn:
            features[0] = BitArray(self.game.white)
            features[1] = BitArray(self.game.black)
        else:
            features[0] = BitArray(self.game.black)
            features[1] = BitArray(self.game.white)
        features[2] = self.legalMoves

        return features

class MCTSBatch:
    def __init__(self, model, numMcts):
        self.numMcts = numMcts
        self.model = model

    def select(self, nodes):
        bestNodesBatch = [None] * len(nodes)
        for i, node in enumerate(nodes):
            current = node
            while current.expanded:
                bestEdge = np.argmax(current.edgeQU)
                if bestEdge not in current.childNodes:
                    current.childNodes[bestEdge] = Node(current, bestEdge, current.turn^1)
                if current.isTerminal:
                    break
                if bestEdge == 64 and current.childNodes[bestEdge].legalMoves == 0:
                    current.isTerminal = True
                    break
                current = current.childNodes[bestEdge]
            bestNodesBatch[i] = current
        return bestNodesBatch

    def ExpandEvaluate(self, nodesBatch):
        featuresBatch = np.zeros([len(nodesBatch), 3, 64], dtype=float)
        for i, node in enumerate(nodesBatch):
            node.expanded = True
            featuresBatch[i] = node.toFeatures()
        pBatch, vBatch = self.model.predict(featuresBatch)
           
        for i, node in enumerate(nodesBatch):
            node.edgeP = NormalizeMask(pBatch[i], node.legalMoves)
        
        return vBatch

    def backup(self, nodesBatch, vBatch):
        for i, node in enumerate(nodesBatch):
            current = node
            while True:
                current.selfN += 1
                current.selfW += vBatch
                if current.isSearchRoot:
                    break
                current = current.parent

    def search(self, nodes):
        bestNodesBatch = self.select(nodes)
        vBatch = self.ExpandEvaluate(bestNodesBatch)
        self.backup(bestNodesBatch, vBatch)
    
    def alpha(self, nodes, temperature):
        for i in range(self.numMcts):
            self.search(nodes)

        piBatch = np.zeros([len(nodes), 64], dtype='f4')
        for i, node in enumerate(nodes):
            nTemperature = node.edgeN**(1 / temperature)
            sumnTemperature = np.sum(nTemperature)
            if sumnTemperature == 0:
                node.pi = np.zeros([64], dtype='f4')
            else:
                node.pi = nTemperature / sumnTemperature
            piBatch[i] = node.pi
        return piBatch
    

def NormalizeMask(x, mask):
    masked = np.multiply(x, mask)
    normalized = masked / np.sum(masked)
    return normalized
