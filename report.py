import os

class Report:
    def __init__(self, directory, txtlis):
        self.txt = ''
        self.directory = directory
        self.txtlis = txtlis

    def make_html(self):
        flis = os.listdir(self.directory) # 파일 리스트 읽어옴
        linechart = []
        stackchart = []
        boxplot = []
        heatmap = []

        # 디렉토리 안에 차트 그림파일이 있는가?
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
        # TODO: 셀렉트 박스 스크립트

        self.txt = '''
        </head>
        <body>
        '''

        # TODO: 사진 집어넣기


        # 히트맵
        for fname in heatmap:
            self.place_img(fname)
        self.txt += '<br/>'

        # 라인 차트
        for fname in linechart:
            self.place_img(fname)
        self.txt += '<br/>'
        self.txt += self.txtlis[0] + '<p/>'
        '''
        00 혼잡 18-10-29 04:45:14
        00 한적 18-10-29 04:48:01
        '''
        
        # 스택 차트
        for fname in stackchart:
            self.place_img(fname)
        self.txt += '<br/>'
        self.txt += self.txtlis[1] + '<p/>'
        '''
        00 번 구역에 0.14318618042226486 %
        01 번 구역에 0.12399232245681382 %
        '''

        # 박스플롯
        # TODO: 표준편차 넣기
        for fname in boxplot:
            self.place_img(fname)
        self.txt += '<br/>'
        self.txt += self.txtlis[2] + '<p/>'
        '''
        출력예제:
        가장 혼잡한 구역은 01 입니다.
        가장 한적한 구역은 11 입니다.
        '''

        # TODO: 셀렉트박스로 만들기
        # 스케쥴링
        self.txt += '<select>'
        # for in range():
        self.txt += '<option>'
        self.txt += self.txtlis[3]
        self.txt += '</option>'
        self.txt += '<div id="sch">'
        self.txt += '</div>'

        self.txt += '''
        </body>
        </html>
        '''

    def place_img(self, filename):
        self.txt += '<img src="'
        self.txt += filename
        self.txt += '"/>'

    def to_report(self):
        file = open('report.html', 'w')
        file.write(self.txt)
        file.close()
