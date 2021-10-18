import random

from player import Player


class World:

    AI_NAMES = ['惜朝','云师','jimmy仔','瀚师','聪师','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁',
                '刘凯龙','蘑师','包大师','胡济民','胡姐',]

    AI_NAMES_ENTRE = ['姆巴佩','哈兰德','马化腾','马斯克','Zuckerberg','乔布斯',]

    AI_NAMES_FTB = ['Mbappé','Haaland','Ronaldo','Messi','Zidane','Pelé','Neymar',
                    'Maradona','Rooney','Pogba','Benzema','Modric','Ramos','Bale',]

    AI_NAMES_MOVIE = ['马龙白兰度','迪卡普里奥','德普','汤姆克鲁斯','乔治克鲁尼','肖恩康纳利','伊斯特伍德',
                    '布鲁斯威利斯','成龙','周星驰','姜文','宁浩','贾樟柯']

    AI_NAMES_RNR = ['Thom Yorke','Jonny Greenwood','Colin Greenwood','Slash',
                    'Bob Dylan','John Lennon','George Harrison','Ringo Starr',
                    'Paul McCartney','Sting','黄家驹','崔健','谢强']

    AI_NAMES_NETRED = ['特师',]

    def __init__(self, game):
        random.shuffle(self.AI_NAMES)
        players = [Player(game, name=name) for name in self.AI_NAMES]
        random.shuffle(players)
        self.PLAYERS = set(players)

    def __repr__(self):
        pl = '\n'.join([p.NAME for p in self.PLAYERS])
        return f'世界上的玩家：\n\n{pl}'

    def pop(self):
        return self.PLAYERS.pop()
