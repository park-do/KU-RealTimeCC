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

    g = gui.FrameOne(None, 'test', d)
    g.openWindow()

    '''
    for i in range(0,5):
        time.sleep(5)
        a.add_row(d.framedetect(0))
        a.df.to_csv('C:/Users/이동우/Desktop/test.csv')
    '''

