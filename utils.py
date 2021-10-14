DEBUG = False


def Shuffle() -> List:
    global RawCards
    num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    suit_list = ['s', 'h', 'c', 'd']
    RawCards = [x + y for x in num_list for y in suit_list]
    # once is enough yeah but
    random.shuffle(RawCards)
    random.shuffle(RawCards)
    random.shuffle(RawCards)
    return RawCards