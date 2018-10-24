import wx
from threading import Thread
from time import sleep
import imageutility
from PIL import Image, ImageDraw
import detectgrid
from datetime import datetime
import time
import cccamera
from typing import List

class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d, a):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        self.a = a  # 애널라이저 객체 받음
        title = "프레임1"
        self.cameraList: List[cccamera.cccamera] = [] #카메라 리스트
        # self.nowCamIP = -1                            #현재 처리중인 Cam의 IP
        self.nowCamIndex = 0                          #현재 처리중인 Cam의 Index
        self.gridIndex = self.dotIndex = -1           #그리드 이동용 변수들

        title = "RealTimeCC"

        # self.gridList["00"] = detectgrid.DetectGrid()
        # # self.gridList["00"].addRect([600, 300, 800, 400]) # 새로운 영상
        # self.gridList["00"].addRect([8, 338, 302, 490])
        # self.gridList["01"] = detectgrid.DetectGrid()
        # # self.gridList["01"].addRect([600, 420, 800, 530]) # 새로운 영상
        # self.gridList["01"].addRect([376, 284, 586, 394])
        #
        # self.gridList["10"] = detectgrid.DetectGrid()
        # self.gridList["10"].addRect([70, 354, 255, 539])
        # self.gridList["11"] = detectgrid.DetectGrid()
        # self.gridList["11"].addRect([173, 250, 292, 340])

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(1100, 700))  # 사이즈에 -1 넣으면 기본값 나옴
        self.startPanel = wx.Panel(self)
        # self.inputtext = wx.TextCtrl(self.startPanel, -1, "Cam ip or number", pos=(10, 300), size=(450, 60))
        button = wx.Button(self.startPanel, label="캠 추가", pos=(10, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.onAddButton, button)
        button = wx.Button(self.startPanel, label="시작", pos=(70, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.OnStartButton, button)
        button = wx.Button(self.startPanel, label="저장", pos=(130, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.OnSaveButton, button)
        button = wx.Button(self.startPanel, label="그리드추가", pos=(190, 10), size=(100, 40))
        self.Bind(wx.EVT_BUTTON, self.OnGridAddButton, button)
        button = wx.Button(self.startPanel, label="CSV분석", pos=(290, 10), size=(80, 40))
        self.Bind(wx.EVT_BUTTON, self.OnCSVAnalyzeButton, button)
        self.imageCtrl = None
        self.Show(True)
        app.MainLoop()  # gui 실행

    def onAddButton(self, e):
        # wx.BitmapFromImage(self.detector.getcamimage(1))

        dlg = wx.TextEntryDialog(self, 'Enter Cam IP', 'Add Cam')
        dlg.SetValue("http://")
        if dlg.ShowModal() == wx.ID_OK:
            print('You entered: %s\n' % dlg.GetValue())

            try:
                nowcamip = int(dlg.GetValue())
            except:
                nowcamip = dlg.GetValue()

            newCamera = cccamera.cccamera()
            newCamera.camip = nowcamip
            self.nowCamIP = nowcamip
            newCamera.camindex = len(self.cameraList)
            newCamera.AddGrid()

            self.cameraList.append(newCamera)

            button = wx.Button(self.startPanel, label="캠 " + str(len(self.cameraList)), pos=(10 + 60 * (len(self.cameraList)-1), 55), size=(60 , 40))

            def OnCamChange(event, index=len(self.cameraList)-1):
                self.nowCamIP = self.cameraList[index].camip
                self.nowCamIndex = index
                print(self.nowCamIP)

            self.Bind(wx.EVT_BUTTON, OnCamChange, button)

            self.Layout()

            # 변경할 캠사이즈
            camsize = (960, 540)

            # testing cam ip
            # self.camip = 'http://192.168.1.55:8080'
            # try:
            #     self.camip = int(self.inputtext.GetLineText(0))
            # except:
            #     self.camip = self.inputtext.GetLineText(0)
            # print(self.camip)

            # Image Control에 처음으로 넣을 프레임을 가져옵니다.
            if self.imageCtrl is None:
                _, bitmap = self.d.getcamimage(camip=self.nowCamIP, size=camsize)

                gridIndex = 0
                for checkingGrid in self.cameraList[self.nowCamIndex].gridList:
                    color = "red"
                    if gridIndex == 1:
                        color = "blue"
                    if gridIndex == 2:
                        color = "green"
                    if gridIndex == 3:
                        color = "yellow"
                    bitmap = checkingGrid.drawGrid(bitmap, color)

                    gridIndex+=1


                # 처음으로 불러온것이면 get com image에서 찾아온 첫 프레임을 넣어둡니다.
                self.imageCtrl = wx.StaticBitmap(self.startPanel, wx.ID_ANY, bitmap, pos=(10, 100))
                self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftMouseButtonDown)
                self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnLeftMouseButtonUp)


            '''
            # 여기는 버튼을 누를 때 갱신됩니다. 
            # detect결과를 가져옵니다.
            # 첫번째 return이 detect리스트입니다. 빈칸으로, 두번째 return이 처리된 이미지입니다.
            _, bitmap = self.d.framedetect(camip=self.camip, size = camsize)
            # 이미지컨트롤에 bitmap을 넣습니다.
            self.imageCtrl.Bitmap = bitmap
            # '''

            '''
            # '''
            # 여기는 버튼을 누를 때 갱신됩니다.
            # detect결과를 가져옵니다.
            # 첫번째 return이 detect리스트입니다. 빈칸으로, 두번째 return이 처리된 이미지입니다.

            # for i in range(0, 5):
            #     sleep(1)
            #     detection_list, bitmap = self.d.framedetect(camip=self.camip)
            #     self.imageCtrl.Bitmap = bitmap  # 이미지컨트롤에 bitmap을 넣습니다.
            #     self.a.add_row(detection_list)
            #     self.a.df.to_csv('C:/Users/이동우/Desktop/test.csv')
            # self.a.show_heatmap()
            # '''


        else:
            return

        dlg.Destroy()

        # self.d.framedetect('http://192.168.1.55:8080')
        # self.Close(True) #종료

    def OnSaveButton(self, e):
        self.a.df.to_csv('../test.csv')

    def OnStartButton(self, e):
        camsize = (960, 540)
        # 처음으로 버튼을 누른 후 스레드가 돌아갑니다.
        self.previewThread = Thread(target=self.PreviewThreading, args=(self.imageCtrl, self.d, camsize))
        self.previewThread.start()

    def OnLeftMouseButtonDown(self, mouseEvent : wx.MouseEvent):
        camera = self.cameraList[self.nowCamIndex]
        self.gridIndex, self.dotIndex = camera.GrapDot(mouseEvent.GetPosition())
        print((self.gridIndex, self.dotIndex))


    def OnLeftMouseButtonUp(self, mouseEvent: wx.MouseEvent):
        print("Up : " + str(mouseEvent.GetPosition()))
        # 이전 Down에서 맞는 grid 점을 찾았을 경우
        if self.gridIndex != -1 and self.dotIndex != -1:
            # DOT 세팅해주고
            self.cameraList[self.nowCamIndex].gridList[self.gridIndex].setDot(self.dotIndex, mouseEvent.GetPosition())
            # 리프레시
            self.RefreshPreview()

        self.gridIndex = self.dotIndex = -1

    def OnGridAddButton(self, mouseEvent: wx.MouseEvent):
        print("GridAddButton")
        self.cameraList[self.nowCamIndex].AddGrid()
        self.RefreshPreview()

    def OnCSVAnalyzeButton(self, e):
        print("CSVButton")
        dlg = wx.DirDialog(self, 'Enter Csv path', 'CSV PATH', wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            # TODO: ANALYZE with the CVSs.
            print("DO SOMETHING with : " + path)


    def RefreshPreview(self):
        _, bitmap = self.d.getcamimage(camip=self.nowCamIP, size=(960, 540))

        gridIndex = 0
        for checkingGrid in self.cameraList[self.nowCamIndex].gridList:
            color = "red"
            if gridIndex == 1:
                color = "blue"
            if gridIndex == 2:
                color = "green"
            if gridIndex == 3:
                color = "yellow"
            bitmap = checkingGrid.drawGrid(bitmap, color)

            gridIndex += 1

        self.imageCtrl.Bitmap = bitmap

    # 미리보기 화면
    def PreviewThreading(self, imageCtrl, detector, size):
        #루프
        camSize = detector.getcamsize(self.nowCamIP)
        jjj = 0
        while True:
            # if jjj == 10:
            #     break
            # jjj+=1
            t0 = time.clock()
            now = str(datetime.now())
            detection_list, bitmap = detector.framedetect(camip=self.nowCamIP, size=size, drawboxes=False)
            analyze_list = []
            term = 10

            if detection_list is None:
                break
            # ret, bitmap = detector.getcamimage(self.nowCamIP, size=size)
            #if ret:

            originalSize = detector.getcamsize(self.nowCamIP)

            gridIndex = 0
            for checkingGrid in self.cameraList[self.nowCamIndex].gridList:
                color = "red"
                if gridIndex == 1:
                    color = "blue"
                if gridIndex == 2:
                    color = "green"
                if gridIndex == 3:
                    color = "yellow"
                bitmap = checkingGrid.drawGrid(bitmap, color)

                gridIndex += 1

            image = imageutility.WxBitmapToPilImage(bitmap)

            draw = ImageDraw.Draw(image)

            for detection in detection_list:
                analyze_list = []
                if detection[0] == "person":
                    bounds = detection[2]
                    # 너무 넓은 오브젝트 거르기
                    if bounds[2] > originalSize[1] / 2:
                        continue
                    gridIndex = 0
                    for checkingGrid in self.cameraList[self.nowCamIndex].gridList:

                        # Left Top X,Y
                        ltx = bounds[0]-bounds[2]/2
                        lty = bounds[1]-bounds[3]/2

                        # Right Bottom X,Y
                        rbx = bounds[0] + bounds[2] / 2
                        rby = bounds[1] + bounds[3] / 2

                        if size[0] is not 0:
                            ratio = [size[0] / originalSize[0], size[1] / originalSize[1]]
                            ltx *= ratio[0]
                            rbx *= ratio[0]
                            lty *= ratio[1]
                            rby *= ratio[1]

                        if checkingGrid.isInRect(((ltx + rbx)/2, rby)):
                            color = "red"
                            if gridIndex == 1:
                                color = "blue"
                            if gridIndex == 2:
                                color = "green"
                            if gridIndex == 3:
                                color = "yellow"
                            # draw.rectangle((ltx, lty, rbx, rby), outline=color)
                            analyze_list.append(detection + (gridIndex, now))

                        gridIndex+=1

                if len(analyze_list) <= 0:
                    analyze_list.append(detection + (-1, now))
                self.a.add_row(analyze_list)


            # bitmap = imageutility.PIL2wx(image)
            # imageCtrl.Bitmap = bitmap
            print(time.clock()-t0)
            sleeptime = term - (time.clock()-t0)
            if sleeptime >= 0:
                sleep(sleeptime)

        self.a.df.to_csv('../test.csv')
        # self.a.save_heatmap(camSize[0], camSize[1])
