import os

class Report:
    def __init__(self, directory):
        self.txt = ''
        self.directory = directory

    def make_html(self):
        flis = os.listdir(self.directory) # 파일 리스트 읽어옴
        linechart = []
        stackchart = []
        boxplot = []
        heatmap = []

        for fname in flis:
            if fname.find('linechart') >= 0:
                linechart.append(fname)
            if fname.find('stackchart') >= 0:
                stackchart.append(fname)
            if fname.find('boxplot') >= 0:
                boxplot.append(fname)
            if fname.find('heatmap') >= 0:
                heatmap.append(fname)


        self.txt = '''
        <html>
        <head>
        '''
        # TODO: 셀렉트 박스 스크립트, 그리드 위치

        self.txt = '''
        </head>
        <body>
        '''
        
        # 라인 차트
        for fname in linechart:
            self.place_img(fname)
        
        # 스택 차트
        for fname in stackchart:
            self.place_img(fname)
        
        # 박스플롯
        for fname in boxplot:
            self.place_img(fname)
        
        # 히트맵
        for fname in heatmap:
            self.place_img(fname)

        self.txt += '''
        </body>
        </html>
        '''

    def place_img(self, filename):
        self.txt += '<img src="'
        self.txt += filename
        self.txt += '"/>'

    def to_report(self):
        file = open('report.html','w')
        file.write(self.txt)
        file.close()