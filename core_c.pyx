import cython
import time

cdef int PopCount(unsigned long long bits):
    bits = (bits & 0x5555555555555555) + (bits >> 1 & 0x5555555555555555)
    bits = (bits & 0x3333333333333333) + (bits >> 2 & 0x3333333333333333)
    bits = (bits & 0x0f0f0f0f0f0f0f0f) + (bits >> 4 & 0x0f0f0f0f0f0f0f0f)
    bits = (bits & 0x00ff00ff00ff00ff) + (bits >> 8 & 0x00ff00ff00ff00ff)
    bits = (bits & 0x0000ffff0000ffff) + (bits >>16 & 0x0000ffff0000ffff)
    return (bits & 0x00000000ffffffff) + (bits >>32 & 0x00000000ffffffff)

cdef unsigned long long JudgeL(unsigned long long player,unsigned long long masked,unsigned long long blank,int dir):
    cdef unsigned long long tmp = masked & (player << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    return blank & (tmp << dir)    

cdef unsigned long long JudgeR(unsigned long long player,unsigned long long masked,unsigned long long blank,int dir):
    cdef unsigned long long tmp = masked & (player >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    return blank & (tmp >> dir)

cdef unsigned long long Judgef(bint turn,unsigned long long black,unsigned long long white):
    cdef unsigned long long player,enemy,blank = ~(black | white)
    if turn:
        player, enemy = white, black
    else:
        enemy, player = white, black
    cdef unsigned long long h = enemy & 0x7e7e7e7e7e7e7e7e, v = enemy & 0x00ffffffffffff00, a = enemy & 0x007e7e7e7e7e7e00
    cdef unsigned long long revl = JudgeL(player, h, blank, 1)
    revl |=  JudgeL(player, v, blank, 8)
    revl |=  JudgeL(player, a, blank, 7)
    revl |=   JudgeL(player, a, blank, 9)
    revl |=   JudgeR(player, h, blank, 1)
    revl |=   JudgeR(player, v, blank, 8)
    revl |=   JudgeR(player, a, blank, 7)
    revl |=   JudgeR(player, a, blank, 9)
    return revl

cdef unsigned long long ReversedL(unsigned long long player,unsigned long long blank_masked,unsigned long long site,int dir):
    cdef unsigned long long rev = 0
    cdef unsigned long long tmp = blank_masked & (site << dir)
    tmp |= blank_masked & (tmp << dir)
    tmp |= blank_masked & (tmp << dir)
    tmp |= blank_masked & (tmp << dir)
    tmp |= blank_masked & (tmp << dir)
    tmp |= blank_masked & (tmp << dir)
    if player & (tmp << dir) == 0:
        return 0
    else:
        return tmp

cdef unsigned long long ReversedR(unsigned long long player,unsigned long long blank_masked,unsigned long long site,int dir):
    cdef unsigned long long rev = 0
    cdef unsigned long long tmp = blank_masked & (site >> dir)
    tmp |= blank_masked & (tmp >> dir)
    tmp |= blank_masked & (tmp >> dir)
    tmp |= blank_masked & (tmp >> dir)
    tmp |= blank_masked & (tmp >> dir)
    tmp |= blank_masked & (tmp >> dir)
    if player & (tmp >> dir) == 0:
        return 0
    else:
        return tmp

cdef unsigned long long Reversed(bint turn,unsigned long long black,unsigned long long white,unsigned long long site):
    cdef unsigned long long player,enemy
    if turn:
        player, enemy = white, black
    else:
        enemy, player = white, black
    cdef unsigned long long blank_h = enemy & 0x7e7e7e7e7e7e7e7e
    cdef unsigned long long blank_v = enemy & 0x00ffffffffffff00
    cdef unsigned long long blank_a = enemy & 0x007e7e7e7e7e7e00
    cdef unsigned long long rev =   ReversedL(player, blank_h, site, 1)
    rev |=   ReversedL(player, blank_v, site, 8)
    rev |=   ReversedL(player, blank_a, site, 7)
    rev |=   ReversedL(player, blank_a, site, 9)
    rev |=   ReversedR(player, blank_h, site, 1)
    rev |=   ReversedR(player, blank_v, site, 8)
    rev |=   ReversedR(player, blank_a, site, 7)
    rev |=   ReversedR(player, blank_a, site, 9)
    return rev

cdef class Core():
    cdef public unsigned long long black,white,blank,rev,put,judge
    cdef public bint turn
    def __init__(self,bint tn,unsigned long long b,unsigned long long w):
        self.turn = tn
        self.black = b
        self.white = w
        self.blank = ~(self.black | self.white)
        #self.put = []
        #self.rev = []
    
    cpdef NextBoard(self):
        if self.turn:
            self.black ^= self.rev
            self.white ^= (self.rev ^ self.put)
        else:
            self.black ^= (self.rev ^ self.put)
            self.white ^= self.rev

    cpdef NextTurn(self):
        self.turn ^= 1

    cpdef AddSite(self,unsigned long long site):
        self.put = site
        self.rev = Reversed(self.turn, self.black, self.white, site)

    cpdef AddJudge(self):
        self.judge = Judgef(self.turn, self.black, self.white)

    cpdef Undo(self):
        self.NextTurn()
        self.NextBoard()
        self.AddJudge()
        #self.put, self.rev = self.put[:-1], self.rev[:-1]

    cpdef Count(self):
        return PopCount(self.black), PopCount(self.white)

    cpdef bint PassEnd(self):
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