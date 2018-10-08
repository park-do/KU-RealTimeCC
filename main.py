import darknet
import analyzer
import gui
import time

if __name__ == "__main__":
    # gui init

    # darknet init
    d = darknet.DarknetDetect()

    # analyzer init
    a = analyzer.Analyzer()

    # 첫번째 프레임을 실행시키고 다크넷과 애널라이저를 넘겨준다
    g = gui.FrameOne(None, d, a)

    '''
    for i in range(0,5):
        time.sleep(5)
        a.add_row(d.framedetect(0))
        a.df.to_csv('C:/Users/이동우/Desktop/test.csv')
    '''

