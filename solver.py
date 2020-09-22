from core import Core
import time
def PopCount(bits):
    bits = (bits & 0x5555555555555555) + (bits >> 1 & 0x5555555555555555)
    bits = (bits & 0x3333333333333333) + (bits >> 2 & 0x3333333333333333)
    bits = (bits & 0x0f0f0f0f0f0f0f0f) + (bits >> 4 & 0x0f0f0f0f0f0f0f0f)
    bits = (bits & 0x00ff00ff00ff00ff) + (bits >> 8 & 0x00ff00ff00ff00ff)
    bits = (bits & 0x0000ffff0000ffff) + (bits >>16 & 0x0000ffff0000ffff)
    return (bits & 0x00000000ffffffff) + (bits >>32 & 0x00000000ffffffff)    

def tab(black, white, turn, nmTurn, alpha, beta):
    game = Core(turn,black,white)
    game.AddJudge()
    jg = game.judge
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
        game.NextTurn()
        game.AddJudge()
        jg = game.judge
        if not jg:
            nb,nw = game.Count()
            v = nw - nb
            return v
    maxScore = -100
    minScore = 100
    value = 0
    a = alpha
    b = beta
    if nmTurn < 2:
        game.AddSite(jg)
        game.NextBoard()
        nb,nw = game.Count()
        score = nw - nb
        return score

    while jg:
        bit = jg & (-jg)
        game.AddSite(bit)
        game.NextBoard()
        score = tab(game.black,game.white,game.turn^1,nmTurn-1,a,b)
        game.NextBoard()
        jg &= ~bit
        if game.turn:
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
    game = Core(turn,black,white)
    game.AddJudge()
    jg = game.judge
    maxScore = -100
    start = time.time()
    while jg:
        bit = jg & (-jg)
        game.AddSite(bit)
        game.NextBoard()
        score = mtdf(game.black,game.white,game.turn^1,nmTurn-1,f)
        print(score,hex(bit))
        game.NextBoard()
        if score > maxScore:
            maxScore = score
            f = maxScore
            move = bit
        jg &= ~bit
    print(time.time()-start)
    return move, gtable

def ab(black, white, turn, nmTurn, alpha, beta):
    game = Core(turn,black,white)
    game.AddJudge()
    jg = game.judge
    if not jg:
            game.NextTurn()
            game.AddJudge()
            jg = game.judge
            if not jg:
                nb,nw = game.Count()
                v = nw - nb
                return v 
    maxScore = -100
    minScore = 100
    value = 0
    moveScore = []
    if nmTurn > 100:
        while jg:
            bit = jg & (-jg)
            jg &= ~bit
            game.AddSite(bit)
            game.NextBoard()
            game.AddJudge()
            moveScore.append([PopCount(game.judge),bit])
            game.NextBoard()
        moveScore.sort()
        for siteScore in moveScore:
            site = siteScore[1]
            game.AddSite(site)
            game.NextBoard()
            score = ab(game.black,game.white,game.turn^1,nmTurn-1,alpha,beta)
            game.NextBoard()
            if game.turn:
                if score >= beta:
                    return score
                if score > maxScore:
                    alpha = max(alpha,score)
                    maxScore = score
                    value = score
            else:
                if score <= alpha:
                    return score
                if score < minScore:
                    beta = min(beta,score)
                    minScore = score
                    value = score
    elif nmTurn > 0:
        while jg:
            bit = jg & (-jg)
            game.AddSite(bit)
            game.NextBoard()
            score = ab(game.black,game.white,game.turn^1,nmTurn-1,alpha,beta)
            game.NextBoard()
            jg &= ~bit
            if game.turn:
                if score >= beta:
                    return score
                if score > maxScore:
                    alpha = max(alpha,score)
                    maxScore = score
                    value = score
            else:
                if score <= alpha:
                    return score
                if score < minScore:
                    beta = min(beta,score)
                    minScore = score
                    value = score
    else:
        while jg:
            bit = jg & (-jg)
            game.AddSite(bit)
            game.NextBoard()
            game.NextTurn()
            game.AddSite(game.blank)
            if game.rev == game.blank:
                game.NextTurn()
                game.AddSite(game.blank)
                if game.rev == game.blank:
                    nb,nw = game.Count()
                else:
                    game.NextBoard()
                    nb,nw = game.Count()
            else:
                game.NextBoard()
                nb,nw = game.Count()
            
            score = nw - nb
            if turn:
                if score >= beta:
                    return score
                if score > maxScore:
                    maxScore = score
            else:
                if score <= alpha:
                    return score
                if score < minScore:
                    minScore = score
            jg &= ~bit  
        value = max(minScore,maxScore)

    return value

# def nab(black, white, turn, nmTurn, alpha, beta):
#     game = core(turn,black,white)
#     game.AddJudge()
#     jg = game.judge
#     isPass = 0
#     if not jg:
#             game.NextTurn()
#             game.AddJudge()
#             jg = game.judge
#             if not jg:
#                 nb,nw = game.Count()
#                 v = nw - nb
#                 return v 
#             else:
#                 isPass = 1

#     maxScore = -100
#     a = alpha
#     moveScore = []
#     if nmTurn > 6:
#         while jg:
#             bit = jg & (-jg)
#             jg &= ~bit
#             game.AddSite(bit)
#             game.NextBoard()
#             game.AddJudge()
#             moveScore.append([PopCount(game.judge),bit])
#             game.NextBoard()
#         moveScore.sort()
#         for siteScore in moveScore:
#             site = siteScore[1]
#             game.AddSite(site)
#             game.NextBoard()
#             if isPass:
#                 score = nab(game.black,game.white,game.turn^1,nmTurn-1,a,beta)
#             else:
#                 score = -nab(game.black,game.white,game.turn^1,nmTurn-1,-beta,-a)
#             game.NextBoard()
#             if score >= beta:
#                 return score
#             if score > maxScore:
#                 a = max(a,score)
#                 maxScore = score
#     elif nmTurn > 0:
#         while jg:
#             bit = jg & (-jg)
#             game.AddSite(bit)
#             game.NextBoard()
#             if isPass:
#                 score = nab(game.black,game.white,game.turn^1,nmTurn-1,a,beta)
#             else:
#                 score = -nab(game.black,game.white,game.turn^1,nmTurn-1,-beta,-a)
#             game.NextBoard()
#             if score >= beta:
#                 return score
#             if score > maxScore:
#                 a = max(a,score)
#                 maxScore = score
#             jg &= ~bit
#     else:
#         while jg:
#             bit = jg & (-jg)
#             game.AddSite(bit)
#             game.NextBoard()
#             game.NextTurn()
#             game.AddJudge()
#             if not game.judge:
#                 game.NextTurn()
#                 game.AddJudge()
#                 if game.judge:
#                     game.AddSite(game.blank)
#                     game.NextBoard()
#             else:
#                 game.AddSite(game.blank)
#                 game.NextBoard()
#             nb,nw = game.Count()
#             v = nw - nb
#             if maxScore < v:
#                 maxScore = v
#             jg &= ~bit

#     return maxScore