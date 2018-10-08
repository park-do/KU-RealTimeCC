import wx
from threading import Thread
from time import sleep


def bitmapthread(imageCtrl,detector,camip):
    #루프
    while True:
        _, bitmap = detector.framedetect(camip=camip)
        imageCtrl.Bitmap = bitmap


class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d, a):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        self.a = a  # 애널라이저 객체 받음
        title = "프레임1"

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(500, 500))  # 사이즈에 -1 넣으면 기본값 나옴
        panel = wx.Panel(self)
        button = wx.Button(panel, label="수집시작", pos=(400, 400), size=(60, 60))
        self.Bind(wx.EVT_BUTTON, self.onButton, button)

        # testing cam ip
        self.camip = 0
        # Image Control에 처음으로 넣을 프레임을 가져옵니다.
        bitmap = self.d.getcamimage(camip=self.camip)
        # get com image에서 찾아온 첫 프레임을 미리 넣어둡니다.
        self.imageCtrl = wx.StaticBitmap(panel, wx.ID_ANY, bitmap,
                                         pos=(10, 10))

        self.Show(True)
        app.MainLoop()  # gui 실행

    def onButton(self, e):
        # wx.BitmapFromImage(self.detector.getcamimage(1))

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
        '''
        # 여기는 버튼을 누른 후 스레드가 돌아갑니다.
        t = Thread(target=bitmapthread, args=(self.imageCtrl, self.d, self.camip))
        t.start()
        '''



        # self.d.framedetect('http://192.168.1.55:8080')
        # self.Close(True) #종료
