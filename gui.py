import wx
from threading import Thread
from time import sleep
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg


def bitmapthread(imageCtrl,detector,camip,size):
    #루프
    while True:
        _, bitmap = detector.framedetect(camip=camip, size=size)
        imageCtrl.Bitmap = bitmap


class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d, a):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        self.a = a  # 애널라이저 객체 받음
        title = "프레임1"

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(600, 600))  # 사이즈에 -1 넣으면 기본값 나옴
        self.startPanel = wx.Panel(self)
        self.inputtext = wx.TextCtrl(self.startPanel, -1, "Cam ip or number", pos=(10, 300), size=(450, 60))
        button = wx.Button(self.startPanel, label="수집시작", pos=(500, 300), size=(60, 60))
        self.Bind(wx.EVT_BUTTON, self.onButton, button)
        self.imageCtrl = None
        self.Show(True)
        app.MainLoop()  # gui 실행

    def onButton(self, e):
        # 변경할 캠사이즈
        camsize = (480, 270)

        # testing cam ip
        # self.camip = 'http://192.168.1.55:8080'
        try:
            self.camip = int(self.inputtext.GetLineText(0))
        except:
            self.camip = self.inputtext.GetLineText(0)
        print(self.camip)
        # Image Control에 처음으로 넣을 프레임을 가져옵니다.
        if self.imageCtrl is None:
            self.secondPanel = wx.Panel(self)
            self.secondPanel.SetSize([600, 600])
            self.startPanel.Hide()
            self.secondPanel.Show()
            self.Layout()

            bitmap = self.d.getcamimage(camip=self.camip, size = camsize)
            # 처음으로 불러온것이면 get com image에서 찾아온 첫 프레임을 넣어둡니다.
            self.imageCtrl = wx.StaticBitmap(self.secondPanel, wx.ID_ANY, bitmap,
                                         pos=(10, 10))

        for i in range(0, 5):
            detection_list, bitmap = self.d.framedetect(camip=self.camip)
            self.imageCtrl.Bitmap = bitmap  # 이미지컨트롤에 bitmap을 넣습니다.
            self.a.add_row(detection_list)
            self.a.df.to_csv('C:/Users/이동우/Desktop/test.csv')

        r_x,r_y = self.d.getcamsize(0)
        fig = self.a.save_heatmap(r_x=r_x,r_y=r_y)
        FigureCanvasWxAgg(self.imageCtrl, -1, fig)

        '''
        #여기는 버튼을 누른 후 스레드가 돌아갑니다.
        #t = Thread(target=bitmapthread, args=(self.imageCtrl, self.d, self.camip, camsize))
        #t.start()
        '''



        # self.d.framedetect('http://192.168.1.55:8080')
        # self.Close(True) #종료


