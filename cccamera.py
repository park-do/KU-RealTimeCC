from typing import List
import detectgrid
import math

class cccamera:
    def __init__(self):
        self.gridList: detectgrid.detectgrid = []
        self.camip = ""
        self.camindex = 0

    def AddGrid(self):
        grid = detectgrid.detectgrid()
        grid.addRect([50, 50, 200, 200])
        self.gridList.append(grid)

    def GrapDot(self, pos):
        # 그리드 리스트를 돌며 그리드 확인
        for gridindex in range(0, len(self.gridList)):
            grid = self.gridList[gridindex]
            # dotList도 확인. Index를 넘겨줘야 하므로 index
            for dotindex in range(0, len(grid.dotList)):
                #근처에 있는 점이 있으면 리턴
                if abs(grid.dotList[dotindex][0] - pos[0]) < 5 and abs(grid.dotList[dotindex][1] - pos[1]) < 5:
                    return gridindex, dotindex

        #없으면 -1, -1
        return -1, -1







