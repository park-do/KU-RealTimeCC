import wx
from threading import Thread
from time import sleep
import detectgrid


class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d, a):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        self.a = a  # 애널라이저 객체 받음
        title = "프레임1"
        self.camIpList = []
        self.gridList = []
        self.nowCamIP = -1

        title = "RealTimeCC"

        mygrid = detectgrid.DetectGrid()
        mygrid.addRect([30, 30, 6, 6])

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(900, 600))  # 사이즈에 -1 넣으면 기본값 나옴
        self.startPanel = wx.Panel(self)
        # self.inputtext = wx.TextCtrl(self.startPanel, -1, "Cam ip or number", pos=(10, 300), size=(450, 60))
        button = wx.Button(self.startPanel, label="캠 추가", pos=(10, 10), size=(60, 40))
        self.Bind(wx.EVT_BUTTON, self.onButton, button)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.imageCtrl = None
        self.Show(True)
        app.MainLoop()  # gui 실행

    def onPaint(self, event=None):
        dc = wx.PaintDC(self.startPanel)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        dc.DrawLine(0, 0, 50, 50)

    def onButton(self, e):
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
            print(self.nowCamIP)

            button = wx.Button(self.startPanel, label="캠 " + str(len(self.camIpList)), pos=(10 + 70 * (len(self.camIpList)-1), 55), size=(60 , 40))

            def OnCamChange(event, index=len(self.camIpList)-1):
                self.nowCamIP = self.camIpList[index]
                print(self.nowCamIP)

            self.Bind(wx.EVT_BUTTON, OnCamChange, button)

            self.Layout()

            # 변경할 캠사이즈
            camsize = (480, 270)

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
                # 처음으로 불러온것이면 get com image에서 찾아온 첫 프레임을 넣어둡니다.
                self.imageCtrl = wx.StaticBitmap(self.startPanel, wx.ID_ANY, bitmap, pos=(10, 100))

                # 처음으로 버튼을 누른 후 스레드가 돌아갑니다.
                self.previewThread = Thread(target=self.PreviewThreading, args=(self.imageCtrl, self.d, camsize))
                self.previewThread.start()
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

        for i in range(0, 5):
            sleep(1)
            detection_list, bitmap = self.d.framedetect(camip=self.camip)
            self.imageCtrl.Bitmap = bitmap  # 이미지컨트롤에 bitmap을 넣습니다.
            self.a.add_row(detection_list)
            self.a.df.to_csv('C:/Users/이동우/Desktop/test.csv')
        self.a.show_heatmap()
        # '''

            # '''


            # '''


        else:
            return

        dlg.Destroy()

        """
        이 부분을 웹캠을 넣어서 실행할 수 있으면 좋겠습니다
        #camip = 'http://192.168.0.11:8080'
        camip = 0
        _, bitmap = self.d.framedetect(camip=camip)


        t = Thread(target=bitmapthread, args=(self.imageCtrl, self.detector, camip))
        t.start()

        wx.MessageDialog(self, "종료", "종료합니다")
        """




        # self.d.framedetect('http://192.168.1.55:8080')
        # self.Close(True) #종료




    # 미리보기 화면
    def PreviewThreading(self, imageCtrl, detector, size):
        #루프
        while True:
            # _, bitmap = detector.framedetect(camip=camip, size=size)
            ret, bitmap = detector.getcamimage(self.nowCamIP, size=size)
            if ret:
                imageCtrl.Bitmap = bitmap
            sleep(0.0333333)

