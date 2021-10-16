from typing import List
from thpoker.core import Table


AI_NAMES = ['云师','jimmy仔','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁','刘凯龙',]

AI_NAMES_ENTRE = ['姆巴佩','哈兰德','马化腾','马斯克','Zuckerberg','乔布斯',]

AI_NAMES_FTB = ['Mbappé','Haaland','Ronaldo','Messi','Zidane','Pelé','Neymar',
                'Maradona','Rooney','Pogba','Benzema','Modric','Ramos','Bale',]

AI_NAMES_MOVIE = ['马龙白兰度','迪卡普里奥','德普','汤姆克鲁斯','乔治克鲁尼','肖恩康纳利','伊斯特伍德',
                  '布鲁斯威利斯','成龙','周星驰','姜文','宁浩','贾樟柯']

AI_NAMES_RNR = ['Thom Yorke','Jonny Greenwood','Colin Greenwood','Slash',
                'Bob Dylan','John Lennon','George Harrison','Ringo Starr',
                'Paul McCartney','Sting','黄家驹','崔健','谢强']

CORPUS = {
    'FOLD':['弃牌','🈚️了','没我了','扔掉','白白👋🏻','再见','无我了','这局没我','你们玩','算了，免费看戏',
    '看你们表演',],

    'CHECK':['过','敲敲','叩叩','nb，过了','先过吧','我过','没牌不得过么',],

    'CALL':['跟','跟上','跟起来','我跟','跟他妈的','跟了啊',],

    'RAISE':['加','加他妈的','加起来','加啊','就干你',],

    'ALLIN':['走起来！','ALLIN！！','推他妈的！！','就这些了啊！！','我数数啊','我看看谁不服哈','我小红牌呢',],

    'SMALLTALK':['哈哈','nb','日了','牌不行','荷官给点力啊','这啥牌','我吐了','我吐了呀','我服了',
    '我他妈吐了','我他妈吐了啊',],

    'TRASHTALK':['加油啊','能行吗','放松点，别紧张','没关系，输就输了呀','敢玩吗','还能玩动吗','不行歇会儿啊',
                 '是不困了啊','来个红牛不',]
}


def ShowHand(slashstring) -> Table:
    '''
    :slashstring: e.g. like '6d/As/Th' in TABLE
    '''
    string = ''
    for i in range(len(slashstring)):
        string += slashstring[i] + '/'
    return(Table(string[:-1]))


def SortCombo(combos: list) -> List:
    '''
    :return: player index in game.PLAYERS
    '''
    n = len(combos)
    for i in range(n):
        for j in range(0, n-i-1):
            if combos[j] > combos[j+1]:
                combos[j], combos[j+1] = combos[j+1], combos[j]
    return combos
    