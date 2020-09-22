from solverfunc import Judgef, Reversed, Reversect, Reverse, PopCount
import time

def tab(black, white, turn, nmTurn, alpha, beta):
    jg =  Judgef(turn,black,white)
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
    
    if not jg:
        turn ^= 1
        jg =  Judgef(turn,black,white)
        if not jg:
            nb = PopCount(black)
            nw = PopCount(white)
            v = nw - nb
            return v
    maxScore = -100
    minScore = 100
    value = 0
    a = alpha
    b = beta
    if nmTurn < 2:
        rev =  Reversed(turn,black,white,jg)
        nb,nw =  Reversect(turn,black,white,jg,rev)
        score = nw - nb
        return score

    while jg:
        bit = jg & (-jg)
        rev =  Reversed(turn,black,white,bit)
        black,white =  Reverse(turn,black,white,bit,rev)
        score = tab(black,white,turn^1,nmTurn-1,a,b)
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
        value = tab(black,white,turn,nmTurn,bound-1,bound)
        if value < bound:
            upper = value   # (lower, value)
        else:
            lower = value   # (value, upper)
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
        black,white =  Reverse(turn,black,white,bit,rev)
        score = mtdf(black,white,turn^1,nmTurn-1,f)
        print(score,hex(bit))
        black,white =  Reverse(turn,black,white,bit,rev)
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
        black,white =  Reverse(turn,black,white,bit,rev)
        score = mtdf(black,white,turn^1,nmTurn-1,f)
        score = -score
        print(score,hex(bit))
        black,white =  Reverse(turn,black,white,bit,rev)
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
        black,white =  Reverse(turn,black,white,bit,rev)
        if turn:
            score = mtdf(black,white,turn^1,nmTurn-1,f)
        else:
            score = -mtdf(black,white,turn^1,nmTurn-1,f)
        black,white =  Reverse(turn,black,white,bit,rev)
        if score > maxScore:
            maxScore = score
            f = maxScore
        if score > 0:
            score = float(score+192)**32
        elif score < 0:
            score = float(score+64)**32
        move.append([score,bit])
        sumScore += score
        jg &= ~bit
    return move,maxScore,sumScore,gtable