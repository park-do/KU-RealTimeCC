import wx
import darknet
from threading import Thread


def bitmapthread(imageCtrl,detector,camip):
    while True:
        _, bitmap = detector.framedetect(camip=camip)
        imageCtrl.Bitmap = bitmap

class MyPanel(wx.Panel):

    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)

        b = wx.Button(self, label='Btn', pos=(150, 10))
        b.Bind(wx.EVT_BUTTON, self.btnclk)
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        self.t1 = wx.TextCtrl(self, pos=(20, 11), size=(120, 23))
        self.detector = darknet.DarknetDetect()


        # img = Image(240, 240)
        # wx.BitmapFromImage(self.detector.getcamimage(1))
        camip = 'http://192.168.0.11:8080'
        _, bitmap = self.detector.framedetect(camip=camip)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, bitmap,
                                         pos=(10, 40))

        t = Thread(target=bitmapthread, args=(self.imageCtrl, self.detector, camip))
        t.start()

    def OnButtonClicked(self, e):
        self.detector.framedetect('')
        print('Panel received click event. propagated to Frame class')
        e.Skip()

    def btnclk(self, e):
        print("Button received click event. propagated to Panel class")
        e.Skip()

class Example(wx.Frame):

    def __init__(self, parent):
        super(Example, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        mpnl = MyPanel(self)
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)

        self.SetTitle('Event propagation demo')
        self.Centre()
        self.Show(True)

    def OnButtonClicked(self, e):
        print('click event received by frame class')
        e.Skip()


def openWindow():
    ex = wx.App()
    Example(None)
    ex.MainLoop()

if __name__ == "__main__":
    # gui init
    openWindow()