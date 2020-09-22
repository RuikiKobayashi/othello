    
def PopCount(bits):
    bits = (bits & 0x5555555555555555) + (bits >> 1 & 0x5555555555555555)
    bits = (bits & 0x3333333333333333) + (bits >> 2 & 0x3333333333333333)
    bits = (bits & 0x0f0f0f0f0f0f0f0f) + (bits >> 4 & 0x0f0f0f0f0f0f0f0f)
    bits = (bits & 0x00ff00ff00ff00ff) + (bits >> 8 & 0x00ff00ff00ff00ff)
    bits = (bits & 0x0000ffff0000ffff) + (bits >>16 & 0x0000ffff0000ffff)
    return (bits & 0x00000000ffffffff) + (bits >>32 & 0x00000000ffffffff)
def JudgeL(player,masked,blank,dir):
    tmp = masked & (player << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    tmp |= masked & (tmp << dir)
    return blank & (tmp << dir)       
def JudgeR(player,masked,blank,dir):
    tmp = masked & (player >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    tmp |= masked & (tmp >> dir)
    return blank & (tmp >> dir)
def Judgef(turn, black, white):
    if turn:
        player, enemy = white, black
    else:
        enemy, player = white, black
    blank = ~(black | white)
    h = enemy & 0x7e7e7e7e7e7e7e7e
    v = enemy & 0x00ffffffffffff00
    a = enemy & 0x007e7e7e7e7e7e00
    revl =  JudgeL(player, h, blank, 1)
    revl |=  JudgeL(player, v, blank, 8)
    revl |=  JudgeL(player, a, blank, 7)
    revl |=   JudgeL(player, a, blank, 9)
    revl |=   JudgeR(player, h, blank, 1)
    revl |=   JudgeR(player, v, blank, 8)
    revl |=   JudgeR(player, a, blank, 7)
    revl |=   JudgeR(player, a, blank, 9)
    return revl

def ReversedL( player, blank_masked, site, dir):
    rev = 0
    tmp = ~(player | blank_masked) & (site << dir)
    if tmp:
        for i in range(6):
            tmp <<= dir
            if tmp & blank_masked:
                break
            elif tmp & player:
                rev |= tmp >> dir
                break
            else:
                tmp |= tmp >> dir
    return rev
def ReversedR( player, blank_masked, site, dir):
    rev = 0
    tmp = ~(player | blank_masked) & (site >> dir)
    if tmp:
        for i in range(6):
            tmp >>= dir
            if tmp & blank_masked:
                break
            elif tmp & player:
                rev |= tmp << dir
                break
            else:
                tmp |= tmp << dir
    return rev
def Reversed( turn, black, white, site):
    if turn:
        player, enemy = white, black
    else:
        enemy, player = white, black
    blank_h = ~(player | enemy & 0x7e7e7e7e7e7e7e7e)
    blank_v = ~(player | enemy & 0x00ffffffffffff00)
    blank_a = ~(player | enemy & 0x007e7e7e7e7e7e00)
    rev =   ReversedL(player, blank_h, site, 1)
    rev |=   ReversedL(player, blank_v, site, 8)
    rev |=   ReversedL(player, blank_a, site, 7)
    rev |=   ReversedL(player, blank_a, site, 9)
    rev |=   ReversedR(player, blank_h, site, 1)
    rev |=   ReversedR(player, blank_v, site, 8)
    rev |=   ReversedR(player, blank_a, site, 7)
    rev |=   ReversedR(player, blank_a, site, 9)
    return rev

def Reverse( turn, black, white, site, rev):
    if turn:
        return black ^ rev, white ^ (rev ^ site)
    else:
        return black ^ (rev ^ site), white ^ rev
def Reversect( turn, black, white, site, rev):
    if turn:
        return  PopCount(black ^ rev),  PopCount(white ^ (rev ^ site))
    else:
        return  PopCount(black ^ (rev ^ site)),  PopCount(white ^ rev)