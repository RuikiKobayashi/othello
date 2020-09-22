from core import Core
from solver2 import moveAI,movebAI
from alphabeta import moveAINN
from model import Model
import numpy as np
import random
import time
import model
import mcts

class Othello(Core):

    def __init__(self):
        self.start = time.time()
        super().__init__(0, 0x0000000810000000, 0x0000001008000000)
        self.model = Model()
        self.model.load("model/Gen" + str(0))
        self.score = 0
        self.table = {}
        self.currentNode = mcts.Node(mcts.FakeNode(), 0, 0, Core(self.turn, self.black, self.white))
        self.currentNode.isGameRoot = True
        self.currentNode.isSearchRoot = True
        self.mctsBatch = mcts.MCTSBatch(self.model)

    def ShowBoard(self):
        print("—" * 38)
        for i in range(10):
            for j in range(10):
                mask = 2**(63-(j-1)-8*(i-1))
                if i == 0 or i == 9:
                    if j == 0 or j == 9:
                        print(" ", end=" | ")
                    else:
                        print(str(j), end=" | ")
                elif j == 0 or j == 9:
                    print(str(i), end=" | ")
                elif mask & self.black:
                    print('\033[30m' + "B" + '\033[39m', end=" | ")
                elif mask & self.white:
                    print('\033[37m' + "W" + '\033[39m', end=" | ")
                elif mask & self.judge:
                    print('\033[34m' + "x" + '\033[39m', end=" | ")
                else:
                    print(" ", end=" | ")
            print("\n" + "-" * 38)
        print(hex(self.black), hex(self.white))

    def ShowStone(self):
        nb, nw = self.Count()
        print("Black:{} vs White:{}".format(nb, nw))

    def ShowResult(self):
        """Show the result."""
        nb, nw = self.Count()
        if nb == nw:
            print("Game over\tDraw")
        else:
            winner = "Black" if nb > nw else "White"
            print("Game Over\t{} Won".format(winner))

    def InputPlayer(self):
        print(time.time()-self.start)
        # nb, nw = self.Count()
        # nmTurn = 64 - nb - nw
        # if nmTurn < 14:
        #     site, socre, self.table = moveAI(self.black,self.white,self.turn, nmTurn, self.table, self.score)
        #     self.score = socre
        #     self.AddSite(site)
        # else:
        #     # site, score, self.table = moveAINN(self.black,self.white,self.turn, 2, self.table, self.score,self.model)
        #     # self.score = score
        #     # self.AddSite(site)
        #     pi = self.mctsBatch.alpha([self.currentNode],  0.9 ** (nb + nw - 6))[0]
        #     self.currentNode = self.makeMove(self.currentNode,int(np.argmax(pi)))
        # nb, nw = self.Count()
        # nmTurn = 64 - nb - nw
        # if nmTurn < 14:
        #     site, socre, self.table = movebAI(self.black,self.white,self.turn, nmTurn, self.table, self.score)
        #     self.score = socre
        #     self.AddSite(site)
        # else:
        #     while True:
        #         move = random.randrange(0, 64)
        #         site = 1 << move
        #         if self.judge & site:
        #             # self.AddSite(site)
        #             self.currentNode = self.makeMove(self.currentNode,move)
        #             break

        # while True:
        #     rawSite = input('ij:(row, col) = (i, j), 0:undo  >>> ')
        #     try:
        #         _site = int(rawSite)
        #     except Exception as e:
        #         print(e)
        #         continue
        #     row, col = (_site // 10), (_site % 10)
        #     if 0 < row < 9 and 0 < col < 9:
        #         move = (63-(col-1)-8*(row-1))
        #         site = 1 << move
        #         if self.judge & site:
        #             self.currentNode = self.makeMove(self.currentNode,move)
        #             #self.AddSite(site)
        #             break
        #     elif not _site:
        #         if self.put:
        #             self.Undo()
        #             self.ShowBoard()
        #         else:
        #             print("It has already been initialized")
        #     else:
        #         print("You cannot put there")

    def InputEnemy(self):
        nb, nw = self.Count()
        nmTurn = 64 - nb - nw
        if nmTurn < 14:
            site, socre, self.table = moveAI(self.black,self.white,self.turn, nmTurn, self.table, self.score)
            self.score = socre
            self.AddSite(site)
        else:
            # site, score, self.table = moveAINN(self.black,self.white,self.turn, 3, self.table, self.score,self.model)
            # self.score = score
            # self.AddSite(site)
            self.currentNode = mcts.Node(mcts.FakeNode(), 0, self.turn, Core(self.turn, self.black, self.white))
            self.currentNode.isGameRoot = True
            self.currentNode.isSearchRoot = True
            pi = self.mctsBatch.alpha([self.currentNode],  0.9 ** (nb + nw - 6))[0]
            print(pi)
            self.currentNode = self.makeMove(self.currentNode,int(np.argmax(pi)))

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
            print("いや打てへんやん")
            exit()
        return node

    def Input(self, black, white):
        if not self.turn:
            black()
        else:
            white()

    def Pass(self):
        print("turn passed")

    def game_flow(self):
        while True:
            if self.PassEnd():
                self.ShowBoard()
                self.ShowStone()
                self.ShowResult()
                break
            self.ShowBoard()
            self.ShowStone()
            self.Input(self.InputPlayer, self.InputEnemy)
            self.NextBoard()
            self.NextTurn()


if __name__ == "__main__":
    game = Othello()
    game.game_flow()