from func import Func
import numpy as np

class Core(Func):
    def __init__(self, turn, black, white):
        self.turn = turn
        self.black = black
        self.white = white
        self.blank = ~(self.black | self.white)
        #self.put = []
        #self.rev = []
    
    def NextBoard(self):
        self.black, self.white = self.Reverse(self.turn, self.black, self.white, self.put, self.rev)

    def NextTurn(self):
        self.turn ^= 1

    def AddSite(self, site):
        self.put = site
        self.rev = self.Reversed(self.turn, self.black, self.white, site)

    def AddJudge(self):
        self.judge = self.Judgef(self.turn, self.black, self.white)

    def Undo(self):
        self.NextTurn()
        self.NextBoard()
        self.AddJudge()
        #self.put, self.rev = self.put[:-1], self.rev[:-1]

    def Count(self):
        return self.PopCount(self.black), self.PopCount(self.white)

    def PassEnd(self):
        self.AddJudge()
        if not self.judge:
            self.NextTurn()
            self.AddJudge()
            if not self.judge:
                return True
            else:
                return False
        else:
            return False