import wx
from threading import Thread
from time import sleep
import imageutility
from PIL import Image, ImageDraw
import detectgrid
from datetime import datetime
import time
import cccamera
import analyzer
from typing import List
from wx.lib.pubsub import pub



class ProgressDialog(wx.Dialog):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Progress")
        self.Size = (300, 200)
        self.panel = wx.Panel(self, size=(100, 70))
        self.progress = wx.Gauge(self.panel, range=100, pos=(0, 50))
        self.text = wx.StaticText(self.panel, size=(100, 30), pos=(0, 20))


        # create a pubsub listener
        pub.subscribe(self.updateProgress, "update")

    # ----------------------------------------------------------------------
    def updateProgress(self, number, msg):
        """
        Update the progress bar
        """

        if number >= 100:
            self.Destroy()
        self.text.LabelText = msg
        self.progress.SetValue(number)


class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d, a):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        self.a: analyzer.Analyzer = a  # 애널라이저 객체 받음
        title = "프레임1"
        self.cameraList: List[cccamera.CCCamera] = []   # 카메라 리스트
        # self.nowCamIP = -1                            # 현재 처리중인 Cam의 IP
        self.nowCamIndex = 0                            # 현재 처리중인 Cam의 Index
        self.gridIndex = self.dotIndex = -1             # 그리드 이동용 변수들
        self.gridColorIndex = 0                         # 그리드 색 변수
        self.previewThread: Thread = None               # 미리보기 스레드

        title = "RealTimeCC"

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(1100, 700))  # 사이즈에 -1 넣으면 기본값 나옴
        self.startPanel = wx.Panel(self)
        # self.inputtext = wx.TextCtrl(self.startPanel, -1, "Cam ip or number", pos=(10, 300), size=(450, 60))
        buttonX = 10
        self.camAddButton = wx.Button(self.startPanel, label="캠 추가", pos=(buttonX, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.onAddButton, self.camAddButton)
        buttonX += 60
        self.gridAddButton = wx.Button(self.startPanel, label="그리드추가", pos=(buttonX, 10), size=(100, 40))
        self.Bind(wx.EVT_BUTTON, self.OnGridAddButton, self.gridAddButton)
        buttonX += 100
        self.startButton = wx.Button(self.startPanel, label="시작", pos=(buttonX, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.OnStartButton, self.startButton)
        self.endButton = wx.Button(self.startPanel, label="끝내기", pos=(buttonX, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.OnEndButton, self.endButton)
        self.endButton.Show(False)  # 시작과 끝은 같은 곳에 놓고 필요할때 전환
        buttonX += 60
        self.csvTempSaveButton = wx.Button(self.startPanel, label="CSV임시저장", pos=(buttonX, 10), size=(100, 40))
        self.Bind(wx.EVT_BUTTON, self.OnSaveButton, self.csvTempSaveButton)
        buttonX += 100
        self.csvAnalyzeButton = wx.Button(self.startPanel, label="CSV분석", pos=(buttonX, 10), size=(80, 40))
        self.Bind(wx.EVT_BUTTON, self.OnCSVAnalyzeButton, self.csvAnalyzeButton)
        buttonX += 60

        self.startPanel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftMouseButtonDown)
        self.startPanel.Bind(wx.EVT_LEFT_UP, self.OnLeftMouseButtonUp)
        # self.Bind(wx.EVT_PAINT, self.onPaint)
        self.imageCtrl = None
        self.Show(True)

        self.startPanel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        app.MainLoop()  # gui 실행

    def OnEraseBackground(self, evt):
        #dc = evt.GetDC()
        evt.Skip()

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

            # 카메라 초기화
            newCamera = cccamera.CCCamera()
            newCamera.camip = nowcamip
            self.nowCamIP = nowcamip
            newCamera.camindex = len(self.cameraList)
            newCamera.AddGrid()
            newCamera.StartCamPlay(self.d, self.a)

            self.cameraList.append(newCamera)

            self.RefreshGridColor()

            button = wx.Button(self.startPanel, label="캠 " + str(len(self.cameraList)), pos=(10 + 60 * (len(self.cameraList)-1), 55), size=(60 , 40))

            def OnCamChange(event, index=len(self.cameraList)-1):
                self.nowCamIP = self.cameraList[index].camip
                self.nowCamIndex = index
                print(self.nowCamIP)

            self.Bind(wx.EVT_BUTTON, OnCamChange, button)

            self.Layout()

            # 변경할 캠사이즈
            camsize = (960, 540)

            # Image Control에 처음으로 넣을 프레임을 가져옵니다.
            if self.imageCtrl is None:
                _, bitmap = self.d.getcamimage(camip=self.nowCamIP, size=camsize)

                # 처음으로 버튼을 누른 후 미리보기 스레드가 돌아갑니다.
                self.previewThread = Thread(target=self.PreviewThreading, args=(self.imageCtrl, ))
                self.previewThread.start()
        else:
            return

        dlg.Destroy()

        # self.d.framedetect('http://192.168.1.55:8080')
        # self.Close(True) #종료

    def OnSaveButton(self, e):
        self.a.to_csv()  # df.to_csv('../test.csv')

    def OnStartButton(self, e):
        timeStamp = str(datetime.now())
        for camera in self.cameraList:
            camera.isDetecting = True
            camera.isReady = False
            camera.timeStamp = timeStamp

        self.startButton.Show(False)
        self.camAddButton.Show(False)
        self.gridAddButton.Show(False)
        self.csvAnalyzeButton.Show(False)
        self.endButton.Show(True)

        self.a.grid_to_csv(self.cameraList)

    def OnEndButton(self, e):
        for camera in self.cameraList:
            camera.StopCam()
        self.previewEnd = True

        self.a.to_csv()

        # 모든 스레드가 멈춘 후에 분석 시작
        self.previewThread.join()
        for camera in self.cameraList:
            camera.camThread.join()

        # self.a.to_csv()
        self.AnalyzeProcess()


    def OnLeftMouseButtonDown(self, mouseEvent : wx.MouseEvent):
        if len(self.cameraList) <= 0:
            return
        camera = self.cameraList[self.nowCamIndex]
        mousePos = mouseEvent.GetPosition()
        mousePos[0] -= 10
        mousePos[1] -= 100
        self.gridIndex, self.dotIndex = camera.GrapDot(mousePos)
        print((self.gridIndex, self.dotIndex))


    def OnLeftMouseButtonUp(self, mouseEvent: wx.MouseEvent):
        print("Up : " + str(mouseEvent.GetPosition()))
        # 이전 Down에서 맞는 grid 점을 찾았을 경우
        if self.gridIndex != -1 and self.dotIndex != -1:
            # 위치조정
            mousePos = mouseEvent.GetPosition()
            mousePos[0] -= 10
            mousePos[1] -= 100
            # DOT 세팅해주고
            self.cameraList[self.nowCamIndex].gridList[self.gridIndex].setDot(self.dotIndex, mousePos)

        self.gridIndex = self.dotIndex = -1

    def OnGridAddButton(self, mouseEvent: wx.MouseEvent):
        print("GridAddButton")
        self.cameraList[self.nowCamIndex].AddGrid()
        self.RefreshGridColor()

    def RefreshGridColor(self):
        colorIndex = 0
        for ci in range(0, len(self.cameraList)):
            # colorIndex += 1  # 빈칸을 위한 스킵
            for gi in range(0, len(self.cameraList[ci].gridList)):
                self.cameraList[ci].gridList[gi].color = analyzer.colorList[colorIndex]
                colorIndex += 1  # 다음 색

    def OnCSVAnalyzeButton(self, e):
        print("CSVButton")
        dlg = wx.DirDialog(self, 'Enter Csv path', 'CSV PATH', wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.a.saveDirectory = path
            self.AnalyzeProcess()
            # print("DO SOMETHING with : " + path)

    def AnalyzeProcess(self):

        dlg = ProgressDialog()
        dlg.Show()
        analyzeThread = Thread(target=self.AnalyzeThread())
        analyzeThread.start()
        # analyzeThread.join()

    def AnalyzeThread(self):
        path = self.a.saveDirectory + "/"
        pub.sendMessage("update", number=1, msg="Reading Directory")
        sleep(0)
        self.a.read_directory(path)

        pub.sendMessage("update", number=15, msg="Saving Linechart")
        sleep(0)
        self.a.save_linechart()

        pub.sendMessage("update", number=45, msg="Saving Boxplot")
        sleep(0)
        self.a.save_boxplot()

        pub.sendMessage("update", number=30, msg="Saving Statckchart")
        sleep(0)
        self.a.save_stackchart()


        pub.sendMessage("update", number=60, msg="Saving Heatmap")
        sleep(0)
        self.a.save_heatmap(path)

        pub.sendMessage("update", number=90, msg="Saving report")
        sleep(0)
        self.a.save_report()

        pub.sendMessage("update", number=100, msg="END")

    def RefreshPreview(self):
        _, bitmap = self.d.getcamimage(camip=self.nowCamIP, size=(960, 540))

        gridImage = imageutility.wx2PIL(bitmap)

        gridIndex = 0
        for checkingGrid in self.cameraList[self.nowCamIndex].gridList:
            color = "red"
            if gridIndex == 1:
                color = "blue"
            if gridIndex == 2:
                color = "green"
            if gridIndex == 3:
                color = "yellow"
            gridImage = checkingGrid.drawGrid(gridImage, color)

            gridIndex += 1
        bitmap = imageutility.PIL2wx(gridImage)
        self.imageCtrl.Bitmap = bitmap

    # 미리보기 화면
    def PreviewThreading(self, imageCtrl: wx.Bitmap):
        # 루프
        self.previewEnd = False

        while True:
            nowCam = self.cameraList[self.nowCamIndex]
            if nowCam.nowBitmap is not None:
                dc = wx.ClientDC(self.startPanel)
                dc.DrawBitmap(nowCam.nowBitmap, 10, 100)

            detectStart = True
            for cam in self.cameraList:
                if cam.isReady is False:
                    detectStart = False
                    break
            if detectStart is True:
                timeStamp = str(datetime.now())
                # timeStamp = timeStamp[:timeStamp.find('.')].replace(":", " ").replace("-", " ")
                for cam in self.cameraList:
                    cam.isReady = False
                    cam.timeStamp = timeStamp
                sleep(0.5)
            else:
                sleep(0.001)

            if self.previewEnd:
                break
        # self.a.df.to_csv('../test.csv')
        # self.a.save_heatmap(camSize[0], camSize[1])

    # 그리기
    # def OnPaint(self, event):
        # dc = wx.BufferedPaintDC(self, self._Buffer)