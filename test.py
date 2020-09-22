import numpy as np

roteMap = list([56,48,40,32,24,16,8,0,57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,28,20,12,4,61,53,45,37,29,21,13,5,62,54,46,38,30,22,14,6,63,55,47,39,31,23,15,7])
reveMap = list([56,57,58,59,60,61,62,63,48,49,50,51,52,53,54,55,40,41,42,43,44,45,46,47,32,33,34,35,36,37,38,39,24,25,26,27,28,29,30,31,16,17,18,19,20,21,22,23,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7])

def ReveBit(bit):
    return   ((bit << 56)|(bit << 40 & 0x00ff000000000000)|(bit << 24 & 0x0000ff0000000000)|(bit << 8 & 0x000000ff00000000)
        |(bit >> 8 & 0x00000000ff000000)|(bit >> 24 & 0x0000000000ff0000)|(bit >> 40 & 0x000000000000ff00)|(bit >> 56))

def RoteBit(bit):
    t  = 0x0f0f0f0f00000000 & (bit ^ (bit << 28))
    bit ^=       t ^ (t >> 28)
    t  = 0x3333000033330000 & (bit ^ (bit << 14))
    bit ^=       t ^ (t >> 14)
    t  = 0x5500550055005500 & (bit ^ (bit <<  7))
    b = bit ^ t ^ (t >>  7)

    t = (b ^ (b >>  7)) & 0x0101010101010101
    b ^= t ^ (t <<  7)
    t = (b ^ (b >>  5)) & 0x0202020202020202
    b ^= t ^ (t <<  5)
    t = (b ^ (b >>  3)) & 0x0404040404040404
    b ^= t ^ (t <<  3)
    t = (b ^ (b >>  1)) & 0x0808080808080808
    b ^= t ^ (t <<  1)
    return b

def Rote(x,pi):
    a = np.array([pi[roteMap[i]] for i in range(64)])
    features = []
    features.append(RoteBit(x[0]))
    features.append(RoteBit(x[1]))
    features.append(RoteBit(x[2]))
    return features,a
        
def Reve(x,pi):
    a = np.array([pi[reveMap[i]] for i in range(64)])
    features = []
    features.append(ReveBit(x[0]))
    features.append(ReveBit(x[1]))
    features.append(ReveBit(x[2]))
    return features,a

def BitArray(bit):
    jglist = list(reversed((("0" * 64) + bin(int(bit) & 0xffffffffffffffff)[2:])[-64:]))
    return np.array(jglist, dtype=int)

bits = []
bits.append(0x000f000f000f000f)
c = BitArray(bits[0])
print(c.reshape([-1,8,8]),1)
bits.append(0x000000000000ffff)
bits.append(0x000000000000ffff)
revebits,revec = Reve(bits,c)
rotebits,rotec = Rote(bits,c)
print(BitArray(revebits[0]).reshape([-1,8,8]))
print(revec.reshape([-1,8,8]))
print(BitArray(rotebits[0]).reshape([-1,8,8]))
print(rotec.reshape([-1,8,8]))

