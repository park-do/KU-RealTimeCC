import wx
from threading import Thread

def bitmapthread(imageCtrl,detector,camip):
    while True:
        _, bitmap = detector.framedetect(camip=camip)
        imageCtrl.Bitmap = bitmap

class FrameOne(wx.Frame):
    """분석 시작 버튼이 있는 프레임"""

    def __init__(self, parent, d):
        """생성자"""
        self.d = d  # 다크넷 객체 받음
        title = "프레임1"

        app = wx.App(False)  # wx 초기화
        wx.Frame.__init__(self, parent, title=title, size=(500, 500))  # 사이즈에 -1 넣으면 기본값 나옴
        panel = wx.Panel(self)
        button = wx.Button(panel, label="수집시작", pos=(400, 400), size=(60, 60))
        self.Bind(wx.EVT_BUTTON, self.onButton, button)
        self.Show(True)
        app.MainLoop()  # gui 실행

    def onButton(self, e):
        # wx.BitmapFromImage(self.detector.getcamimage(1))

        """
        이 부분을 웹캠을 넣어서 실행할 수 있으면 좋겠습니다
        #camip = 'http://192.168.0.11:8080'
        camip = 0
        _, bitmap = self.d.framedetect(camip=camip)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, bitmap,
                                         pos=(10, 40))

        t = Thread(target=bitmapthread, args=(self.imageCtrl, self.detector, camip))
        t.start()

        wx.MessageDialog(self, "종료", "종료합니다")
        """
        self.d.framedetect(0)
        self.Close(True) #종료
