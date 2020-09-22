from solverfunc import Judgef, Reversed, Reversect, Reverse, PopCount
import numpy as np
import time
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
        lower = -10
        upper = 10
    
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
    maxScore = -10
    minScore = 10
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
        Pi, score = model.predict(features)
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

def mtdf(black, white, turn, nmTurn, f, model):
    lower = -100
    upper = 100
    bound = f
    while lower < upper:
        value = tab(black,white,turn,nmTurn,bound-1,bound,model)
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
    jg =  Judgef(turn,black,white)
    maxScore = -100
    start = time.time()
    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        score = tab(black,white,turn^1,nmTurn-1,-10,10,model)
        #print(score,hex(bit))
        black,white =  Reverse(turn,black,white,bit,rev)
        if score > maxScore:
            maxScore = score
            f = maxScore
            move = bit
        jg &= ~bit
    print(time.time()-start)
    return move, maxScore, gtable