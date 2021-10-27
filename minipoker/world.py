import random

from minipoker.player import Player


class World:

    ZHIHU = ['惜朝','瀚师','聪师','卞师','瓜师','铁师','杨师','然师','情师','达云','继新','周源','申申',
            '梁指','湖玛','张亮','心岩','芯宁','斗斗','开复','世奇','斯蒂法尼', ]

    BLV = ['云师','jimmy仔','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁',
                '刘凯龙','蘑师','包大师','胡济民','阿鬼',]

    ENTRE = ['周鸿祎','雷军','马化腾','马斯克','Zuckerberg','乔布斯','王兴','王小川','贝索斯']

    FTB = ['Mbappé','Haaland','Ronaldo','Messi','Zidane','Pelé','Neymar',
                    'Maradona','Rooney','Pogba','Benzema','Modric','Ramos','Bale',]

    MOVIE = ['马龙白兰度','迪卡普里奥','德普','汤姆克鲁斯','乔治克鲁尼','肖恩康纳利','伊斯特伍德',
                    '布鲁斯威利斯','成龙','周星驰','姜文','宁浩','贾樟柯']

    RNR = ['Thom Yorke','Jonny Greenwood','Colin Greenwood','Slash',
                    'Bob Dylan','John Lennon','George Harrison','Ringo Starr',
                    'Paul McCartney','Sting','黄家驹','崔健','谢强']

    NETRED = ['特师','公孙玉龙','李诞','徐志胜','梁文道','窦文涛','李承鹏','李海鹏','连岳','银教授',]

    def __init__(self, game, names=ZHIHU):
        random.shuffle(names)
        players = [Player(game, name=name) for name in names]
        random.shuffle(players)
        self.PLAYERS = set(players)

    def __repr__(self):
        pl = '\n'.join([p.NAME for p in self.PLAYERS])
        return f'世界上的玩家：\n\n{pl}'

    def pop(self):
        return self.PLAYERS.pop()

    def Add(self, p):
        self.PLAYERS.add(p)
