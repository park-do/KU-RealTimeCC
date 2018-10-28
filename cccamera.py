from typing import List
import detectgrid
import math
import darknet
from threading import Thread
import imageutility
from PIL import Image, ImageDraw
import time
from datetime import datetime
import analyzer
from time import sleep
import wx

class CCCamera:
    def __init__(self):
        self.gridList: detectgrid.detectgrid = []
        self.camip = ""
        self.camindex = 0
        self.camsize = (10,10)
        self.nowBitmap: wx.Bitmap = None
        self.isDetecting = False
        self.isReady = False
        self.previewThread = None
        self.timeStamp = ""

    def AddGrid(self):
        grid = detectgrid.detectgrid()
        grid.addRect([50, 50, 200, 200])
        self.gridList.append(grid)

    def GrapDot(self, pos):
        grabRange = 10
        # 그리드 리스트를 돌며 그리드 확인
        for gridindex in range(0, len(self.gridList)):
            grid = self.gridList[gridindex]
            # dotList도 확인. Index를 넘겨줘야 하므로 index
            for dotindex in range(0, len(grid.dotList)):
                #근처에 있는 점이 있으면 리턴
                if abs(grid.dotList[dotindex][0] - pos[0]) <= grabRange and abs(grid.dotList[dotindex][1] - pos[1]) <= grabRange:
                    return gridindex, dotindex

        #없으면 -1, -1
        return -1, -1

    def StartCamPlay(self, detector: darknet.DarknetDetect, analyzerInst: analyzer.Analyzer):
        self.previewThread = Thread(target=self.CamPlayThread, args=(detector, analyzerInst))
        self.previewThread.start()

    def CamPlayThread(self, detector: darknet.DarknetDetect, analyzerInst: analyzer.Analyzer):
        camsize = detector.getcamsize(self.camip)
        self.camsize = camsize
        size = (960, 540)
        while True:
            detection_list = []
            analyze_list = []
            term = 1

            t0 = time.clock()
            if self.isDetecting is True:
                while self.isReady is True:
                    sleep(0)
                t0 = time.clock()
                detection_list, bitmap = detector.framedetect(camip=self.camip, size=size, drawboxes=False)
            else:
                term = 5
                _, bitmap = detector.getcamimage(self.camip, size=size)

            if detection_list is None:
                break

            originalSize = detector.getcamsize(self.camip)

            gridImage = imageutility.wx2PIL(bitmap)

            gridIndex = 0
            for checkingGrid in self.gridList:
                color = "red"
                if gridIndex == 1:
                    color = "blue"
                if gridIndex == 2:
                    color = "green"
                if gridIndex == 3:
                    color = "yellow"
                gridImage = checkingGrid.drawGrid(gridImage, color)

                gridIndex += 1

            # image = imageutility.WxBitmapToPilImage(bitmap)

            draw = ImageDraw.Draw(gridImage)

            for detection in detection_list:
                analyze_list = []
                if detection[0] == "person":
                    bounds = detection[2]
                    # 너무 넓은 오브젝트 거르기
                    if bounds[2] > originalSize[1] / 2:
                        continue
                    gridIndex = 0
                    for checkingGrid in self.gridList:

                        # Left Top X,Y
                        ltx = bounds[0] - bounds[2] / 2
                        lty = bounds[1] - bounds[3] / 2

                        # Right Bottom X,Y
                        rbx = bounds[0] + bounds[2] / 2
                        rby = bounds[1] + bounds[3] / 2

                        if size[0] is not 0:
                            ratio = [size[0] / originalSize[0], size[1] / originalSize[1]]
                            ltx *= ratio[0]
                            rbx *= ratio[0]
                            lty *= ratio[1]
                            rby *= ratio[1]

                        if checkingGrid.isInRect(((ltx + rbx) / 2, rby)):
                            color = "red"
                            if gridIndex == 1:
                                color = "blue"
                            if gridIndex == 2:
                                color = "green"
                            if gridIndex == 3:
                                color = "yellow"
                            draw.rectangle((ltx, lty, rbx, rby), outline=color)
                            camgrid = str(self.camindex)+""+str(gridIndex+1)
                            analyze_list.append(detection + (camgrid, self.timeStamp))

                        gridIndex += 1

                if len(analyze_list) <= 0:
                    camgrid = str(self.camindex) + "0"
                    analyze_list.append(detection + (camgrid, self.timeStamp))
                analyzerInst.add_row(analyze_list)
            analyzerInst.after_add_row()
            self.nowBitmap = imageutility.PIL2wx(gridImage)
            # imageCtrl.Bitmap = bitmap
            print(time.clock() - t0)
            sleeptime = term - (time.clock() - t0)
            if sleeptime >= 0:
                sleep(sleeptime)

            if self.isDetecting is True:
                self.isReady = True






