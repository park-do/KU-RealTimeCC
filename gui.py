import wx
from threading import Thread
from time import sleep
import imageutility
from PIL import Image, ImageDraw
import detectgrid


class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d, a):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        self.a = a  # 애널라이저 객체 받음
        title = "프레임1"
        self.camIpList = []
        self.gridList = {}
        self.nowCamIP = -1
        self.nowCamIndex = 0

        title = "RealTimeCC"

        self.gridList["00"] = detectgrid.DetectGrid()
        self.gridList["00"].addRect([8, 338, 302, 490])
        self.gridList["01"] = detectgrid.DetectGrid()
        self.gridList["01"].addRect([376, 284, 586, 394])

        self.gridList["10"] = detectgrid.DetectGrid()
        self.gridList["10"].addRect([70, 354, 255, 539])
        self.gridList["11"] = detectgrid.DetectGrid()
        self.gridList["11"].addRect([173, 250, 292, 340])

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(1100, 700))  # 사이즈에 -1 넣으면 기본값 나옴
        self.startPanel = wx.Panel(self)
        # self.inputtext = wx.TextCtrl(self.startPanel, -1, "Cam ip or number", pos=(10, 300), size=(450, 60))
        button = wx.Button(self.startPanel, label="캠 추가", pos=(10, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.onAddButton, button)
        button = wx.Button(self.startPanel, label="시작", pos=(70, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.onStartButton, button)
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
                self.camIpList.append(int(dlg.GetValue()))
            except:
                self.camIpList.append(dlg.GetValue())
            print(self.camIpList)
            self.nowCamIP = self.camIpList[len(self.camIpList)-1]
            self.nowCamIndex = len(self.camIpList)-1
            print(self.nowCamIP)

            button = wx.Button(self.startPanel, label="캠 " + str(len(self.camIpList)), pos=(10 + 60 * (len(self.camIpList)-1), 55), size=(60 , 40))

            def OnCamChange(event, index=len(self.camIpList)-1):
                self.nowCamIP = self.camIpList[index]
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
                while True:
                    gridHash = str(self.nowCamIndex) + str(gridIndex)
                    if gridHash in self.gridList:
                        checkingGrid = self.gridList[gridHash]
                        color = "red"
                        if gridIndex == 1:
                            color = "blue"
                        bitmap = checkingGrid.drawGrid(bitmap, color)
                    else:
                        break
                    gridIndex+=1


                # 처음으로 불러온것이면 get com image에서 찾아온 첫 프레임을 넣어둡니다.
                self.imageCtrl = wx.StaticBitmap(self.startPanel, wx.ID_ANY, bitmap, pos=(10, 100))


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

    def onStartButton(self, e):
        camsize = (960, 540)
        # 처음으로 버튼을 누른 후 스레드가 돌아갑니다.
        self.previewThread = Thread(target=self.PreviewThreading, args=(self.imageCtrl, self.d, camsize))
        self.previewThread.start()

    # 미리보기 화면
    def PreviewThreading(self, imageCtrl, detector, size):
        #루프
        camSize = detector.getcamsize(self.nowCamIP)
        while True:
            detection_list, bitmap = detector.framedetect(camip=self.nowCamIP, size=size, drawboxes=False)
            if detection_list is None:
                break
            # ret, bitmap = detector.getcamimage(self.nowCamIP, size=size)
            self.a.add_row(detection_list)
            #if ret:

            originalSize = detector.getcamsize(self.nowCamIP)

            gridIndex = 0
            while True:
                gridHash = str(self.nowCamIndex) + str(gridIndex)
                if gridHash in self.gridList:
                    checkingGrid = self.gridList[gridHash]
                    color = "red"
                    if gridIndex == 1:
                        color = "blue"
                    bitmap = checkingGrid.drawGrid(bitmap, color)
                else:
                    break
                gridIndex += 1

            image = imageutility.WxBitmapToPilImage(bitmap)

            draw = ImageDraw.Draw(image)

            for detection in detection_list:
                if detection[0] == "person":
                    bounds = detection[2]
                    # 너무 넓은 오브젝트 거르기
                    if bounds[2] > originalSize[1] /2:
                        continue
                    gridIndex = 0
                    while True:
                        gridHash = str(self.nowCamIndex) + str(gridIndex)
                        if gridHash in self.gridList:
                            checkingGrid = self.gridList[gridHash]

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
                                draw.rectangle((ltx, lty, rbx, rby), outline=color)
                        else:
                            break

                        gridIndex+=1



            bitmap = imageutility.PIL2wx(image)
            imageCtrl.Bitmap = bitmap
            # sleep(0.0333333)

        self.a.df.to_csv('../test.csv')
        self.a.save_heatmap(camSize[0], camSize[1])
