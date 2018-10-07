
# it is dectection grid
class detectgrid:

    def __init__(self):

        self.dotList = []

    '''
    @:param dots is [x, y] pair array or a pair. it will append dotList. example : [ [1,3] [2,3] ] or [3,5]
    '''
    def addList(self, dots):
        self.dotList = self.dotList + dots

    '''
    @:param rect is [left top x, left top y, right bottom x, right bottom y]. it will replace the dotList.
    '''
    def addRect(self, rect):
        self.dotList = [[rect[0], rect[1], [rect[2], rect[1]], [rect[2], rect[3]], rect[0], rect[3]]]


