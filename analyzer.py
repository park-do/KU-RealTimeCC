import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import ast  # 데이터 프레임을 읽어서 스트링을 튜플로 만들 때 필요
from datetime import datetime
from dateutil.parser import parse
import os
from PIL import Image, ImageDraw
from threading import Lock
from typing import List

# 그래프 등에 쓰이는 색 리스트
colorList: List[str] = ["#ff0000", "#ffff00", "#ff00ff", "#00ffff", "#00ff00", "#abcdef", "#fedcba", "#abefcd", "#cdbaef"]

class Analyzer:
    # df = pd.DataFrame()  # 데이터를 수집해서 저장하는 프레임
    # df2 = pd.DataFrame()  # 분석용 데이터 프레임
    '''생성자'''
    def __init__(self):
        self.df = pd.DataFrame(columns=['OBJECT', 'ACCURACY', 'POSITION', 'GRIDINDEX', 'TIME'])
        # strfmt = '%y%m%d %H%M%S'
        # self.timename = str(datetime.fromtimestamp(time.time()).strftime(strfmt))
        self.timename = str(datetime.now())
        self.timename = self.timename[:self.timename.find('.')].replace(":", "").replace("-", "")
        self.saveDirectory = "../" + str(self.timename)
        self.csvcount = 0
        self.csvcut = 500
        self.lock = Lock() #LOCK

    '''데이터 로우 추가'''
    def add_row(self, detection_list):
        # now = str(datetime.now())
        with self.lock:
            for row in detection_list:
                if row[0] == 'person':  # 사람만 추가함
                    row = list(row)  # tuple을 list로
                    # row.append(now)  # 현재 시간 추가 # PJK: 시간 추가를 gui처리부로 옮깁니다.
                    self.df.loc[len(self.df)] = row
                    # POSITION: (x,y)(w,h)

    '''row 길이 체크'''
    def after_add_row(self):
        if self.df.size >= self.csvcut * 6:
            self.to_csv()
            self.df = pd.DataFrame(columns=['OBJECT', 'ACCURACY', 'POSITION', 'GRIDINDEX', 'TIME'])

    def grid_to_csv(self, cameraList):
        griddf = pd.DataFrame(columns=['CAMID', 'CAMSIZE', 'GRIDID', 'POSITION'])
        for camera in cameraList:
            for gridIndex in range(0, len(camera.gridList)):
                xModify = camera.camsize[0] / 960
                yModify = camera.camsize[1] / 560
                dl = camera.gridList[gridIndex].dotList
                row = (camera.camindex, tuple(camera.camsize), str(camera.camindex) + str(gridIndex+1),
                       (((dl[0][0]+dl[2][0])/2 * xModify,
                         (dl[0][1]+dl[2][1])/2 * yModify,
                         dl[2][0]-dl[0][0] * xModify,
                         dl[2][1]-dl[0][1] * yModify)))
                griddf.loc[len(griddf)] = list(row)


        if not os.path.exists(self.saveDirectory):
            os.makedirs(self.saveDirectory)

        griddf.to_csv(self.saveDirectory + "/grid.csv")

    '''결과 저장 함수'''
    def to_csv(self):

        if not os.path.exists(self.saveDirectory):
            os.makedirs(self.saveDirectory)

        self.df.to_csv(self.saveDirectory + "/" + str(self.timename) + "_" + str(self.csvcount) + ".csv")
        self.csvcount += 1

    '''디렉토리 읽어서 초기화'''
    def read_directory(self, directory):
        print('read directory called')
        flis = os.listdir(directory)
        csvlis = [s for s in flis if s.find('.csv') > 0]  # csv 중
        csvlis = [s for s in csvlis if s.find('grid') < 0]  # 그리드가 아닌거
        i = 0
        for name in csvlis:
            tmpdf = pd.read_csv(directory + name, engine='python', index_col=0, dtype={'GRIDINDEX': str})
            if i == 0:
                tmpdf = tmpdf.pivot_table(columns='TIME', index='GRIDINDEX', aggfunc={'OBJECT': 'count'},
                                          fill_value=0).unstack().to_frame().reset_index()
                tmpdf.drop(columns='level_0', inplace=True)
                tmpdf.rename(columns={0: 'OBJECT'}, inplace=True)
                resdf = tmpdf
                i = 1
                continue
            tmpdf = tmpdf.pivot_table(columns='TIME', index='GRIDINDEX', aggfunc={'OBJECT': 'count'},
                                      fill_value=0).unstack().to_frame().reset_index()
            tmpdf.drop(columns='level_0', inplace=True)
            tmpdf.rename(columns={0: 'OBJECT'}, inplace=True)
            resdf = pd.concat([resdf, tmpdf])  # 합치기

        df2 = resdf.groupby(['TIME', 'GRIDINDEX']).agg({'OBJECT': 'sum'}).reset_index()
        df2.rename(columns={'OBJECT': 'COUNT'}, inplace=True)

        # 최고시간 최저시간의 차를 계산한 후 10개 구간으로 나눔
        maxt = round(parse(df2.TIME.unique().max()).timestamp())
        mint = round(parse(df2.TIME.unique().min()).timestamp())
        td = (maxt - mint) / 20  # 구간 개수 설정

        # 타임 간격에 맞는 날짜 포맷 설정
        if td < 60:  # 60초보다 시간 간격이 짧으면 초 단위도 표시함
            strfmt = '%y-%m-%d %H:%M:%S'
        else:
            strfmt = '%y-%m-%d %H:%M'

        lis = []
        for t in df2.TIME:
            tmp = int((parse(t).timestamp() - mint) / td)  # 20개 구간 중 몇 번째 구간이낙?
            if tmp >= 20: tmp = 19  # 20을 넘어가면 그냥 19로
            tmpt = mint + tmp * td
            lis.append(datetime.fromtimestamp(tmpt).strftime(strfmt))
        df2['TIMEINDEX'] = lis
        tmpdf = df2.pivot_table(columns='TIMEINDEX', index='GRIDINDEX', aggfunc={'COUNT': 'mean'},
                               fill_value=0).unstack().to_frame().reset_index()
        tmpdf.rename(columns={0: 'COUNT'}, inplace=True)
        self.df2 = df2.groupby(['TIMEINDEX', 'GRIDINDEX']).agg({'COUNT': 'mean'}).reset_index()
        print('read directory finished')

    '''라인차트 저장'''
    def save_linechart(self):
        # plt 설정
        fig, ax1 = plt.subplots()
        fig.set_size_inches(8, 8)
        ax1.set_title('Time series analysis')

        # x축 설정
        tmpdf = self.df2[self.df2['GRIDINDEX'] == '00']
        y = tmpdf['COUNT']

        x = np.arange(y.shape[0])
        my_xticks = tmpdf.TIMEINDEX
        frequency = 2
        #plt.xticks(x[::frequency], my_xticks[::frequency])
        plt.xticks(x, my_xticks)
        plt.xticks(rotation=40)

        # 주 축
        ax1.set_ylabel('number of person in each section')
        color_idx = 0
        for i in self.df2.GRIDINDEX.unique():
            if i[-1:] == '0': continue
            y = self.df2[self.df2['GRIDINDEX'] == i]['COUNT']
            ax1.plot(x, y, alpha=1, label='section ' + i, c=colorList[color_idx])
            color_idx += 1

        # 보조 축(전체)

        ax2 = ax1.twinx()
        ax2.set_ylabel('total number of person')
        # y = df2[df2['GRIDINDEX']=='00']['COUNT']
        y = self.df2.groupby('TIMEINDEX').agg({'COUNT': 'sum'})['COUNT']
        ax2.bar(x, y, alpha=0.1, label='total')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        fig.tight_layout()
        plt.savefig(self.saveDirectory + '/linechart.png')
        print('save linechart finished')

    '''스택차트를 저장하는 함수'''
    def save_stackchart(self,param=0):

        # plt 설정
        fig, ax1 = plt.subplots()
        fig.set_size_inches(8, 8)
        ax1.set_title('Cumulative sum')

        # x축 설정
        tmpdf = self.df2[self.df2['GRIDINDEX'] == '00']
        y = tmpdf['COUNT']

        x = np.arange(y.shape[0])
        my_xticks = tmpdf.TIMEINDEX
        #frequency = 2
        #plt.xticks(x[::frequency], my_xticks[::frequency])
        plt.xticks(x, my_xticks)
        plt.xticks(rotation=40)

        # y축 설정
        stacked_list = []
        cumsum_stacked_list = []
        labels = []
        rest_lis = []
        grid_lis = []
        for s in self.df2.GRIDINDEX.unique():
            if s[1:] == '0':
                rest_lis.append(s)
            else:
                grid_lis.append(s)
        '''
        파라미터가 0이면 그냥 스택 차트
        파라미터가 0이 아니면 누계
        '''
        if param == 0:
            for i in grid_lis:
                stacked_list.append(self.df2[self.df2['GRIDINDEX'] == i]['COUNT'].tolist())  # 리스트로 만들어 스택드리스트에 저장
                labels.append('section ' + str(i))
            for i in rest_lis:
                stacked_list.append(self.df2[self.df2['GRIDINDEX'] == i]['COUNT'].tolist())  # 리스트로 만들어 스택드리스트에 저장
                labels.append(str(i) + ' camera rest')
        else:
            for i in self.df2.GRIDINDEX.unique():
                cumsum = np.cumsum(self.df2[self.df2['GRIDINDEX'] == i]['COUNT'].tolist())  # 누계를 구함
                stacked_list.append(cumsum)  # 리스트로 만들어 스택드리스트에 저장
                if i[-1:] != '0':
                    labels.append(str(i) + ' camera rest')

        y = np.vstack(stacked_list)
        ax1.stackplot(x, y, labels=labels)
        ax1.legend(loc='upper left')
        ax1.set_ylabel('number of person')
        fig.tight_layout()
        plt.savefig(self.saveDirectory + '/stackchart.png')
        ax1.remove()
        print('save stackchart finished')

    '''박스 플롯 저장'''
    def save_boxplot(self):
        tmpdf1 = self.df2[self.df2['GRIDINDEX'].str[-1:] == '0']  # 나머지 영역
        tmpdf2 = self.df2[self.df2['GRIDINDEX'].str[-1:] != '0']  # 그리드 영역

        tmpdf1.rename(columns={'GRIDINDEX': 'CAMERA'}, inplace=True)
        tmpdf2.rename(columns={'GRIDINDEX': 'SECTION'}, inplace=True)

        fig = plt.figure()
        fig.set_size_inches(8, 8)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        ax1.set_title('Box plot')

        sns.boxplot(x='CAMERA', y='COUNT', data=tmpdf1, ax=ax1, hue="CAMERA")
        sns.boxplot(x="SECTION", y="COUNT", data=tmpdf2, ax=ax2, palette=colorList, hue="SECTION")
        plt.savefig(self.saveDirectory + '/boxplot.png')
        print('save boxplot finished')

    def save_heatmap(self,directory):
        flis = os.listdir(directory)
        griddf = pd.read_csv(directory + 'grid.csv', engine='python', index_col=0)

        csvlis = [s for s in flis if s.find('.csv') > 0]  # csv 중
        csvlis = [s for s in csvlis if s.find('grid') < 0]  # 그리드가 아닌거

        # griddf의 포지션을 튜플로
        lis = []
        for i in griddf.POSITION:
            lis.append(ast.literal_eval(i))
        griddf.POSITION = lis

        # camdf 설정
        camdf = griddf[['CAMID', 'CAMSIZE']].drop_duplicates()
        camlis = camdf.CAMID.unique().tolist()
        lis = []
        for i in camdf.CAMSIZE:
            lis.append(ast.literal_eval(i))
        camdf.CAMSIZE = lis

        '''캠 개수만큼 반복'''
        for camidx in camlis:
            print('cam',+ camidx, 'make heatmap')
            r_x = camdf[camdf['CAMID'] == camidx].CAMSIZE.tolist()[0][0]  # cam의 영상 너비
            r_y = camdf[camdf['CAMID'] == camidx].CAMSIZE.tolist()[0][1]  # cam의 영상 높이

            x_index = 100
            y_index = int(r_y * x_index / r_x)  # x가 100일 때 y의 비율 계산
            arr = [[0] * (x_index) for i in range(y_index)]  # 히트맵 표현용 2차원배열
            x_scaler = MinMaxScaler(feature_range=(0, x_index - 1))  # 표준화 인스턴스
            y_scaler = MinMaxScaler(feature_range=(0, y_index - 1))

            x_scaler.fit([[0], [r_x]])  # 해상도 최대값 설정
            y_scaler.fit([[0], [r_y]])

            '''csv 개수만큼 반복'''
            for name in csvlis:
                df = pd.read_csv(directory + name, engine='python', index_col=0, dtype={'GRIDINDEX': str})
                if len(df) <= 0:
                    continue
                lis = []
                for i in df.POSITION:
                    lis.append(ast.literal_eval(i))
                df['POSITION'] = lis
                tmpdf = df[df['GRIDINDEX'].str[:1] == str(camlis[camidx])]
                if len(tmpdf) <= 0:
                    continue

                pdf = tmpdf['POSITION'].apply(pd.Series)  # position 만을 담은 데이터프레임
                pdf.columns = ['X', 'Y', 'W', 'H']  # 튜플을 데이터 프레임으로

                sdf = pdf.copy()  # 표준화된 pdf
                sdf[['X', 'W']] = x_scaler.transform(pdf[['X', 'W']])
                sdf[['Y', 'H']] = y_scaler.transform(pdf[['Y', 'H']])
                sdf = sdf.astype(int)

                '''arr의 카운트를 높이는 부분'''
                for row in sdf.iterrows():
                    row = row[1]  # 0은 인덱스, 1에 위치 데이터가 들어있음
                    for i in range(row['X'] - int(row['W'] / 2), row['X'] + int(row['W'] / 2)):
                        for j in range(row['Y'] - int(row['H'] / 2), row['Y'] + int(row['H'] / 2)):
                            if j >= len(arr) or j < 0 or i >= len(arr[j]) or i < 0:
                                continue
                            arr[j][i] += 1


            heatmap = sns.heatmap(arr, cbar=False, xticklabels=False, yticklabels=False)
            fig = heatmap.get_figure()
            fig.set_size_inches((r_x/100, r_y/100))
            plt.tight_layout(0)
            fig.savefig(self.saveDirectory + '/heatmap' + str(camidx) + '.png', dpi=100)

        # Grid 영역 그리기
        camid = griddf.CAMID.unique().tolist()
        for i in camid:  # camID만큼 반복
            image = Image.open(directory + 'heatmap' + str(i) + '.png')
            draw = ImageDraw.Draw(image)
            gridid = griddf[griddf['CAMID'] == i]['GRIDID'].unique().tolist()
            for j in gridid: #  gridID 만큼 반복
                color_idx = 0
                dotList = []
                pdf = griddf[griddf['GRIDID'] == j]['POSITION'].apply(pd.Series)  # position 만을 담은 데이터프레임
                pdf.columns = ['X', 'Y', 'W', 'H']  # 튜플을 데이터 프레임으로
                # 1번 점
                dotList.append([pdf['X'].iloc[0] - pdf['W'].iloc[0] / 2, pdf['Y'].iloc[0] - pdf['H'].iloc[0] / 2])
                # 2번 점
                dotList.append([pdf['X'].iloc[0] + pdf['W'].iloc[0] / 2, pdf['Y'].iloc[0] - pdf['H'].iloc[0] / 2])
                # 3번 점
                dotList.append([pdf['X'].iloc[0] + pdf['W'].iloc[0] / 2, pdf['Y'].iloc[0] + pdf['H'].iloc[0] / 2])
                # 4번 점
                dotList.append([pdf['X'].iloc[0] - pdf['W'].iloc[0] / 2, pdf['Y'].iloc[0] + pdf['H'].iloc[0] / 2])
                # 라인 그리기
                for k in range(0, len(dotList) - 1):
                    draw.line((dotList[k][0], dotList[k][1], dotList[k + 1][0], dotList[k + 1][1]), 
                              colorList[color_idx], 2)
                # 닫아주기
                draw.line((dotList[0][0], dotList[0][1], dotList[len(dotList) - 1][0], dotList[len(dotList) - 1][1]),
                          colorList[color_idx], 2)
                color_idx += 1

            image.save(self.saveDirectory + '/heatmap' + str(i) + '.png')



    '''리포트 저장'''
    def save_report(self):
        txtlis = []
        df3 = self.df2.pivot_table(index='TIMEINDEX', columns='GRIDINDEX', aggfunc=np.mean)
        df3['SUM'] = df3.sum(axis=1)
        df3.columns = df3.columns.levels[1].tolist()

        '''##########################그리드 별 혼잡한 시간, 한적한 시간 찾기##########################'''
        txt = ''
        for i in df3.columns.tolist()[:-1]:
            txt += str(i) + " 혼잡 " + df3[df3.loc[:, i] == df3.loc[:, i].max()].index[0] + '\n'  # 0번 섹션의 최고 혼잡 시간 찾기
            txt += str(i) + " 한적 " + df3[df3.loc[:, i] == df3.loc[:, i].min()].index[0] + '\n'  # 0번 섹션의 최고 한적 시간 찾기
        '''
        출력예제:
        00 혼잡 18-10-29 04:45:14
        00 한적 18-10-29 04:48:01
        01 혼잡 18-10-29 04:47:05
        01 한적 18-10-29 04:48:01
        02 혼잡 18-10-29 04:47:42
        '''
        txtlis.append(txt)

        '''##########################가장 혼잡한 지역은? 그리고 비율은?##########################'''
        txt = ''
        df4 = df3.mean(axis=0).to_frame().reset_index()  # 함계행만 데이터 프레임으로
        df4.rename(columns={0: 'COUNT', 'index': 'GRIDINDEX'}, inplace=True)
        df4.iloc[-1, 0] = 'SUM'
        df4.set_index('GRIDINDEX', inplace=True)

        tmp = df4.loc['SUM', 'COUNT']
        for i in df4.index[:-1]:
            txt += str(i) + "번 구역에 " + str(df4.loc[i].COUNT / tmp) + "%\n"
        '''
        출력예제:
        00 번 구역에 0.14318618042226486 %
        01 번 구역에 0.12399232245681382 %
        02 번 구역에 0.10978886756238003 %
        '''
        txtlis.append(txt)

        tmplis = []
        for i in df4.index[:-1]:
            if i[-1:] != '0':
                tmplis.append(i)
        txt = ''
        txt += "가장 혼잡한 구역은 " + df4[df4.COUNT == df4[df4.index.isin(tmplis)].max().COUNT].index[0] + "입니다.\n"
        txt += "가장 한적한 구역은 " + df4[df4.COUNT == df4[df4.index.isin(tmplis)].min().COUNT].index[0] + "입니다.\n"
        '''
        출력예제:
        가장 혼잡한 구역은 01 입니다.
        가장 한적한 구역은 11 입니다.
        '''
        txtlis.append(txt)

        '''##########################평균 표준편차##########################'''
        txt = ''
        for i in tmplis:
            txt += str(i) + "영역의 평균인원은 " + str(round(df3[i].mean(), 3)) + ", 표준편차는 " + str(round(df3[i].std(), 3)) + '\n'
        txtlis.append(txt)
        '''
        출력예제:
        01 영역의 평균인원은 2.675 표준편차는 0.503
        02 영역의 평균인원은 2.388 표준편차는 0.915
        '''
        '''##########################스케쥴링##########################'''
        txt = ''

        df5 = df3.copy()
        for c in range(len(df5.columns)):  # 컬럼
            for r in range(len(df5)):  # 로우
                df5.iloc[r, c] = df5.iloc[r, c] / df3.sum(axis=0)[c]
        df5.rename(columns={'': 'SUM'}, inplace=True)

        for i in df5.columns[:-1]:
            if i[-1:] == '0':
                df5.drop(columns=i, inplace=True)

        gridlen = len(df5.columns) - 1  # 영역이 몇 개 있는 지

        for r in range(len(df5) - gridlen):  # 로우 수 만큼 반복
            tmpdf = df5.iloc[r:r + gridlen, 0:-1]
            txt += str(tmpdf.index[0]) + "시간에 방문시\n"
            reslis = []
            for i in range(gridlen):
                tmp = tmpdf.iloc[i] == tmpdf.iloc[i].min()  # i 번째 행에서 최소값
                minc = tmpdf.iloc[i][tmp].index[0]  # 최소 컬럼 저장
                tmpdf.loc[:, minc] = 1  # 방문한 컬럼은 1로 최대화 해버림
                reslis.append(minc)
            for i in reslis:
                txt += str(i) + "영역 → "
            txt += " 순으로 방문 하시는 게 좋습니다.\n\n"
        '''
        출력예제:
        18-10-29 04:41:52 시간에 방문시
        11 영역 → 02 영역 → 12 영역 → 02 영역 → 순으로 방문 하시는 게 좋습니다.
        
        18-10-29 04:42:10 시간에 방문시
        11 영역 → 02 영역 → 12 영역 → 02 영역 → 순으로 방문 하시는 게 좋습니다.

        '''
        txtlis.append(txt)
