from solverfunc import Judgef, Reversed, Reversect, Reverse, PopCount
import time
import random
import numpy as np

scr = np.array([30,-12,0,-1,-1,0,-12,30,
    -12,-15,-3,-3,-3,-3,-15,-12,
    0,-3,0,-1,-1,0,-3,0,
    -1,-3,-1,-1,-1,-1,-3,-1,
    -1,-3,-1,-1,-1,-1,-3,-1,
    0,-3,0,-1,-1,0,-3,0,
    -12,-15,-3,-3,-3,-3,-15,-12,
    30,-12,0,-1,-1,0,-12,30])

def BitArray(bit):
    return np.array(list(reversed((("0" * 64) + bin(bit)[2:])[-64:])), dtype=np.uint8)

def tab(black, white, turn, nmTurn, alpha, beta, model):
    jg =  Judgef(turn,black,white)
    key = (black,white)
    if key in gtable:
        lower, upper = gtable[key]
        if lower >= beta: return lower
        if upper <= alpha or upper == lower: return upper
        alpha = max(alpha,lower)
        beta = min(beta,upper)
    else:
        lower = -200
        upper = 200
    
    if not jg:
        turn ^= 1
        jg =  Judgef(turn,black,white)
        if not jg:
            nb = PopCount(black)
            nw = PopCount(white)
            v = nw - nb
            if v > 0:
                v = (v+64)
            else:
                v = (v-64)
            return v
    maxScore = -200
    minScore = 200
    value = 0
    a = alpha
    b = beta
    if nmTurn == 0:
        features = np.zeros([3, 64], dtype=np.float)
        turn = turn
        if turn:
            player = BitArray(white)
            enemy = BitArray(black)
        else:
            enemy = BitArray(white)
            player = BitArray(black)
        features[0] = player
        features[1] = enemy
        features[2] = BitArray(jg)       
        score = model.predict(features)
        return score*128

    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        score = tab(black,white,turn^1,nmTurn-1,a,b,model)
        black,white =  Reverse(turn,black,white,bit,rev)
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

def tab2(black, white, turn, nmTurn, alpha, beta):
    jg =  Judgef(turn,black,white)
    key = (black,white)
    if key in gtable:
        lower, upper = gtable[key]
        if lower >= beta: return lower
        if upper <= alpha or upper == lower: return upper
        alpha = max(alpha,lower)
        beta = min(beta,upper)
    else:
        lower = -1000
        upper = 1000
    
    if not jg:
        turn ^= 1
        jg =  Judgef(turn,black,white)
        if not jg:
            nb = PopCount(black)
            nw = PopCount(white)
            v = nw - nb
            if v > 0:
                v = (v+64)
            else:
                v = (v-64)
            return v
    maxScore = -1000
    minScore = 1000
    value = 0
    a = alpha
    b = beta
    if nmTurn == 0:
        if turn:
            legal = PopCount(jg)*4
        else:
            legal = -PopCount(jg)*4
        sw = np.sum(BitArray(white)*scr)
        sb = np.sum(BitArray(black)*scr)
        score = sw-sb+legal
        return score

    if nmTurn == 1:
        if turn:
            legal = PopCount(jg)*4
        else:
            legal = -PopCount(jg)*4
        while jg:
            bit = jg & (-jg)
            rev =  Reversed(turn,black,white,bit)
            black,white =  Reverse(turn,black,white,bit,rev)
            score = tab2(black,white,turn^1,nmTurn-1,a,b) + legal
            black,white =  Reverse(turn,black,white,bit,rev)
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

    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        score = tab2(black,white,turn^1,nmTurn-1,a,b)
        black,white =  Reverse(turn,black,white,bit,rev)
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

def mtdf(black, white, turn, nmTurn, f):
    lower = -100
    upper = 100
    bound = f
    while lower < upper:
        value = tab2(black,white,turn,nmTurn,bound-1,bound)
        if value < bound:
            upper = value   # (lower, value)
        else:
            lower = value   # (value, upper)
        if lower == value:
            bound = value + 1
        else:
            bound = value
    return value

def moveAINN(black, white, turn, nmTurn, table, f, model):
    global gtable
    gtable = table
    start = time.time()
    jg =  Judgef(turn,black,white)
    maxScore = -200
    move = jg & (-jg)
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        if turn:
            score = tab(black,white,turn^1,nmTurn-1,-200,200,model)
        else:
            score = -tab(black,white,turn^1,nmTurn-1,-200,200,model)
        #print(score,hex(bit))
        black,white =  Reverse(turn,black,white,bit,rev)
        if score > maxScore:
            maxScore = score
            f = maxScore
            move = bit
        jg &= ~bit
    #print(time.time()-start)
    return move, maxScore, gtable

def moveAIinit(black, white, turn, nmTurn, table, f):
    global gtable
    gtable = table
    start = time.time()
    jg =  Judgef(turn,black,white)
    maxScore = -1000
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        if turn:
            score = mtdf(black,white,turn^1,nmTurn-1,f)
        else:
            score = -mtdf(black,white,turn^1,nmTurn-1,f)
        black,white =  Reverse(turn,black,white,bit,rev)
        print(score)
        if score > maxScore:
            maxScore = score
            f = maxScore
            move = bit
        jg &= ~bit
    print(time.time()-start)
    return move, maxScore, gtable

def moveAIiniTrain(black, white, turn, nmTurn, table):
    global gtable
    gtable = table
    start = time.time()
    jg =  Judgef(turn,black,white)
    sumScore = 0
    maxScore = -1000
    move = []
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        if turn:
            score = tab2(black,white,turn^1,nmTurn-1,-1000,1000) + random.randrange(-30, 30)
        else:
            score = -tab2(black,white,turn^1,nmTurn-1,-1000,1000) + random.randrange(-30, 30)
        black,white =  Reverse(turn,black,white,bit,rev)
        if score > maxScore:
            maxScore = score
            f = maxScore
            site = bit
        jg &= ~bit
    return site, gtable