import darknet
import analyzer
import gui

if __name__ == "__main__":
    # darknet init
    d = darknet.DarknetDetect()

    # analyzer init
    a = analyzer.Analyzer()

    # 첫번째 프레임을 실행시키고 다크넷과 애널라이저를 넘겨준다
    g = gui.FrameOne(None, d, a)


