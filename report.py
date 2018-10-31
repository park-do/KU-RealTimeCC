import os

class Report:
    def __init__(self, directory, txtlis):
        self.txt = ''
        self.directory = directory + '/'
        self.txtlis = txtlis

    def make_html(self):
        flis = os.listdir(self.directory) # 파일 리스트 읽어옴
        linechart = []
        stackchart = []
        boxplot = []
        heatmap = []
        cam = []

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
            if fname.find('cam') >= 0:
                cam.append(fname)

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

        for fname in cam:
            self.place_img(fname)
        self.txt += '<br/>'

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
        self.txt += self.txtlis[3] + '<p/>'
        '''
        출력예제:
        가장 혼잡한 구역은 01 입니다.
        가장 한적한 구역은 11 입니다.
        01 영역의 평균인원은 2.675 표준편차는 0.503
        02 영역의 평균인원은 2.388 표준편차는 0.915
        '''

        # TODO: 셀렉트박스로 만들기
        # 스케쥴링
        self.txt += '<select id ="schedule" onchange="changeSchedule()">'
        # for in range():
        self.txt += '<option>'
        self.txt += self.txtlis[4]
        self.txt += '</option>'
        self.txt += '<div id="sch">'
        self.txt += '</div>'

        self.txt += '''
        </body>
        </html>
        '''
        self.to_report()

    def place_img(self, filename):
        self.txt += '<img src="'
        self.txt += self.directory + filename
        self.txt += '"/>'

    def to_report(self):
        file = open(self.directory + 'report.html', 'w')
        file.write(self.txt)
        file.close()

        os.startfile('report.html')


