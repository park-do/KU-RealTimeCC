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
        self.cameraList: List[cccamera.CCCamera] = []   # 카메라 리스트
        # self.nowCamIP = -1                            # 현재 처리중인 Cam의 IP
        self.nowCamIndex = 0                            # 현재 처리중인 Cam의 Index
        self.gridIndex = self.dotIndex = -1             # 그리드 이동용 변수들

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
        self.camAddButton = wx.Button(self.startPanel, label="캠 추가", pos=(10, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.onAddButton, self.camAddButton)
        self.startButton= wx.Button(self.startPanel, label="시작", pos=(70, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.OnStartButton, self.startButton)
        self.saveButton = wx.Button(self.startPanel, label="저장", pos=(130, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.OnSaveButton, self.saveButton)
        self.gridAddButton = wx.Button(self.startPanel, label="그리드추가", pos=(190, 10), size=(100, 40))
        self.Bind(wx.EVT_BUTTON, self.OnGridAddButton, self.gridAddButton)
        self.csvAnalyzeButton = wx.Button(self.startPanel, label="CSV분석", pos=(290, 10), size=(80, 40))
        self.Bind(wx.EVT_BUTTON, self.OnCSVAnalyzeButton, self.csvAnalyzeButton)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.imageCtrl = None
        self.Show(True)

        self.startPanel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        app.MainLoop()  # gui 실행

    def OnEraseBackground(self, evt):
        #dc = evt.GetDC()
        evt.Skip()

    def onPaint(self, evt):
        # if self.bmp:
        if len(self.cameraList) > 0:
            nowCam = self.cameraList[self.nowCamIndex]
            bdc = wx.BufferedPaintDC(self.startPanel)
            bdc.DrawBitmap(nowCam.nowBitmap, 10, 100)

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

                # 처음으로 불러온것이면 get com image에서 찾아온 첫 프레임을 넣어둡니다.
                # self.imageCtrl = wx.StaticBitmap(self.startPanel, wx.ID_ANY, bitmap, pos=(10, 100))
                # self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftMouseButtonDown)
                # self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnLeftMouseButtonUp)

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

        self.a.grid_to_csv(self.cameraList)

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
            # self.RefreshPreview()

        self.gridIndex = self.dotIndex = -1

    def OnGridAddButton(self, mouseEvent: wx.MouseEvent):
        print("GridAddButton")
        self.cameraList[self.nowCamIndex].AddGrid()
        # self.RefreshPreview()

    def OnCSVAnalyzeButton(self, e):
        print("CSVButton")
        dlg = wx.DirDialog(self, 'Enter Csv path', 'CSV PATH', wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            # TODO: ANALYZE with the CVSs.
            print("DO SOMETHING with : " + path)


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

        while True:
            nowCam = self.cameraList[self.nowCamIndex]
            if nowCam.nowBitmap is not None:
                # imageCtrl.Bitmap = nowCam.nowBitmap
                self.Refresh(eraseBackground=False)

            detectStart = True
            for cam in self.cameraList:
                if cam.isReady is False:
                    detectStart = False
                    break
            if detectStart is True:
                timeStamp = str(datetime.now())
                for cam in self.cameraList:
                    cam.isReady = False
                    cam.timeStamp = timeStamp


            sleep(0.1)

        # self.a.df.to_csv('../test.csv')
        # self.a.save_heatmap(camSize[0], camSize[1])

    # 그리기
    # def OnPaint(self, event):
        # dc = wx.BufferedPaintDC(self, self._Buffer)