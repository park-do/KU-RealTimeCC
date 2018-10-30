
# it is dectection grid
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import imageutility

class detectgrid:

    def __init__(self):

        self.dotList = []

    '''
    @:param dots is [x, y] pair array or a pair. it will append dotList. example : [ [1,3] [2,3] ] or [3,5]
    '''
    def addList(self, dots):
        self.dotList = self.dotList + dots

    '''
    @:param rect is (left top x, left top y, right bottom x, right bottom y). it will replace the dotList.
    '''
    def addRect(self, rect):
        self.dotList = [[rect[0], rect[1]], [rect[2], rect[1]], [rect[2], rect[3]], [rect[0], rect[3]]]

    def isInRect(self, pos):
        xcheck = self.dotList[0][0] <= pos[0] <= self.dotList[2][0]
        ycheck = self.dotList[0][1] <= pos[1] <= self.dotList[2][1]
        return xcheck and ycheck

    def setDot(self, index, pos):
        prePos = self.dotList[index]
        self.dotList[index] = pos
        for dot in self.dotList:
            if dot[0] == prePos[0]:
                dot[0] = pos[0]
            if dot[1] == prePos[1]:
                dot[1] = pos[1]

    def drawGrid(self, image, color="red"):
        # image = imageutility.wx2PIL(image)
        draw = ImageDraw.Draw(image)

        # 그려주기
        for i in range(0, len(self.dotList)-1):
            draw.line((self.dotList[i][0], self.dotList[i][1], self.dotList[i+1][0], self.dotList[i+1][1]), color, 2)

        # 닫아주기
        draw.line((self.dotList[0][0], self.dotList[0][1], self.dotList[len(self.dotList)-1][0], self.dotList[len(self.dotList)-1][1]), color, 2)

        return image  # imageutility.PIL2wx(image)
