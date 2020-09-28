import cython
import time
from cpython cimport array as cpython_array

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

cdef int tab(unsigned long long black,unsigned long long white,bint turn,int nmTurn,int alpha,int beta):
    cdef int lower,upper
    cdef unsigned long long jg =  Judgef(turn,black,white)
    key = (black,white)
    if key in gtable:
        lower, upper = gtable[key]
        if lower >= beta: return lower
        if upper <= alpha or upper == lower: return upper
        alpha = max(alpha,lower)
        beta = min(beta,upper)
    else:
        lower = -100
        upper = 100
    
    cdef int nb,nw
    if not jg:
        turn ^= 1
        jg =  Judgef(turn,black,white)
        if not jg:
            nb = PopCount(black)
            nw = PopCount(white)
            return nw - nb
    cdef int maxScore = -100
    cdef int minScore = 100
    cdef int value = 0
    cdef int a = alpha
    cdef int b = beta
    cdef unsigned long long rev
    if nmTurn < 2:
        rev =  Reversed(turn,black,white,jg)
        if turn:
            black ^= rev
            white ^= (rev ^ jg)
        else:
            black ^= (rev ^ jg)
            white ^= rev
        nb = PopCount(black)
        nw = PopCount(white)
        return nw - nb

    cdef unsigned long long bit
    cdef int score
    if nmTurn < 6:
        while jg:
            bit = jg & (-jg)
            rev =  Reversed(turn,black,white,bit)
            if turn:
                black ^= rev
                white ^= (rev ^ bit)
            else:
                black ^= (rev ^ bit)
                white ^= rev
            score = tab(black,white,turn^1,nmTurn-1,a,b)
            if turn:
                black ^= rev
                white ^= (rev ^ bit)
            else:
                black ^= (rev ^ bit)
                white ^= rev
            jg &= ~bit
            if turn:
                if score >= b:
                    return score
                if score > maxScore:
                    a = max(a,score)
                    maxScore = score
                    value = score
            else:
                if score <= a:
                    return score
                if score < minScore:
                    b = min(b,score)
                    minScore = score
                    value = score
        if value <= alpha: gtable[key] = (lower, value)
        elif value >= beta: gtable[key] = (value, upper)
        else: gtable[key] = (value,value)

        return value

    cdef int numjg = PopCount(jg)
    cdef int tmp,j
    cdef cpython_array.array scores = cpython_array.array('i', range(numjg))
    cdef cpython_array.array bits = cpython_array.array('Q', range(numjg))
    for i in range(numjg):
        bit = jg&(-jg)
        rev = Reversed(turn,black,white,bit)
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        scores[i] = PopCount(Judgef(turn,black,white))
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        jg &= ~bit
        bits[i] = bit
    
    for i in range(1,numjg):
        tmp = scores[i]
        tmp2 = bits[i]
        if tmp > scores[i-1]:
            j = i
            while True:
                scores[j] = scores[j-1]
                bits[j] = bits[j-1]
                j -= 1
                if j == 0 or tmp <= scores[j-1]:
                    break
            scores[j] = tmp
            bits[j] = tmp2
    
    for i in range(numjg):
        rev =  Reversed(turn,black,white,bits[i])
        if turn:
            black ^= rev
            white ^= (rev ^ bits[i])
        else:
            black ^= (rev ^ bits[i])
            white ^= rev
        score = tab(black,white,turn^1,nmTurn-1,a,b)
        if turn:
            black ^= rev
            white ^= (rev ^ bits[i])
        else:
            black ^= (rev ^ bits[i])
            white ^= rev
        if turn:
            if score >= b:
                return score
            if score > maxScore:
                a = max(a,score)
                maxScore = score
                value = score
        else:
            if score <= a:
                return score
            if score < minScore:
                b = min(b,score)
                minScore = score
                value = score
    if value <= alpha: gtable[key] = (lower, value)
    elif value >= beta: gtable[key] = (value, upper)
    else: gtable[key] = (value,value)

    return value

cdef int mtdf(unsigned long long black,unsigned long long white,bint turn,int nmTurn,int f):
    cdef int lower = -100
    cdef int upper = 100
    cdef int bound = f
    cdef int value
    while lower < upper:
        value = tab(black,white,turn,nmTurn,bound-1,bound)
        if value < bound:
            upper = value
        else:
            lower = value
        if lower == value:
            bound = value + 1
        else:
            bound = value
    return value

def moveAI(black, white, turn, nmTurn, table, f):
    global gtable
    gtable = table
    jg =  Judgef(turn,black,white)
    maxScore = -100
    start = time.time()
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        score = mtdf(black,white,turn^1,nmTurn-1,f)
        print(score,hex(bit))
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        if score > maxScore:
            maxScore = score
            f = maxScore
            move = bit
        jg &= ~bit
    print(time.time()-start)
    return move, maxScore, gtable

def movebAI(black, white, turn, nmTurn, table, f):
    global gtable
    gtable = table
    jg =  Judgef(turn,black,white)
    maxScore = -100
    start = time.time()
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        score = mtdf(black,white,turn^1,nmTurn-1,f)
        score = -score
        print(score,hex(bit))
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        if score > maxScore:
            maxScore = score
            f = maxScore
            move = bit
        jg &= ~bit
    print(time.time()-start)
    return move, gtable

def moveAITrain(black, white, turn, nmTurn, table, f):
    global gtable
    gtable = table
    jg =  Judgef(turn,black,white)
    maxScore = -100
    sumScore = 0
    move = []
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        if turn:
            score = mtdf(black,white,turn^1,nmTurn-1,f)
        else:
            score = -mtdf(black,white,turn^1,nmTurn-1,f)
        if turn:
            black ^= rev
            white ^= (rev ^ bit)
        else:
            black ^= (rev ^ bit)
            white ^= rev
        if score > maxScore:
            maxScore = score
            f = maxScore
        if score > 0:
            score = 2.0**(score+192)
        elif score < 0:
            score = 2.0**(score+64)
        move.append([score,bit])
        sumScore += score
        jg &= ~bit
    return move,maxScore,sumScore,gtable