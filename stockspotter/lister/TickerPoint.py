import collections


TickerPoint = collections.namedtuple( 'TickerPoint', 'name ticker')

def TickerTree():
    return collections.defaultdict(TickerTree)
