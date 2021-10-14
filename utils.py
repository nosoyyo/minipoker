import random


DEBUG = False


def Shuffle():
    global RawCards
    num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    suit_list = ['s', 'h', 'c', 'd']
    RawCards = [x + y for x in num_list for y in suit_list]
    # once is enough yeah but
    random.shuffle(RawCards)
    random.shuffle(RawCards)
    random.shuffle(RawCards)
    return RawCards


CORPUS = {
    'FOLD':['弃牌','🈚️了','没我了','扔掉','白白👋🏻','再见',],
    'CHECK':['过','敲敲','叩叩','nb，过了','先过吧','我过',],
    'CALL':['跟','跟上','跟起来','我跟','跟他妈的','跟了啊',],
    'RAISE':['加','加他妈的','加起来','加啊',],
    'ALLIN':['全押！','ALLIN！！','推他妈的！！','就这些了啊！！','我数数啊',],
    'SMALLTALK':['哈哈','nb','日了','牌不行','荷官给点力啊','这啥牌','我吐了','我吐了呀','我服了','我他妈吐了','我他妈吐了啊',],
    'TRASHTALK':['加油啊','能行吗','放松点','没关系，输就输了','敢玩吗','还能玩动吗',]
}