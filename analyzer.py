import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import ast  # 데이터 프레임을 읽어서 스트링을 튜플로 만들 때 필요
from datetime import datetime
import os


class Analyzer:
    df = pd.DataFrame()  # 분석 데이터 저장할 데이터 프레임

    '''생성자'''
    def __init__(self):
        self.df = pd.DataFrame(columns=['OBJECT', 'ACCURACY', 'POSITION', 'GRIDINDEX', 'TIME'])
        # strfmt = '%y%m%d %H%M%S'
        # self.timename = str(datetime.fromtimestamp(time.time()).strftime(strfmt))
        self.timename = str(datetime.now())
        self.timename = self.timename[:self.timename.find('.')].replace(":", "").replace("-", "")
        self.csvcount = 0
        self.csvcut = 500

    '''데이터 로우 추가'''
    def add_row(self, detection_list):
        # now = str(datetime.now())
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
                dl = camera.gridList[gridIndex].dotList
                row = (camera.camindex, tuple(camera.camsize), str(camera.camindex) + str(gridIndex+1), (((dl[0][0]+dl[2][0])/2, (dl[0][1]+dl[2][1])/2, dl[2][0]-dl[0][0], dl[2][1]-dl[0][1])))
                griddf.loc[len(griddf)] = list(row)

        dirstr = "../" + str(self.timename)
        if not os.path.exists(dirstr):
            os.makedirs(dirstr)

        griddf.to_csv(dirstr + "/grid.csv")

    '''결과 저장 함수'''
    def to_csv(self):
        dirstr = "../" + str(self.timename)
        if not os.path.exists(dirstr):
            os.makedirs(dirstr)

        self.df.to_csv(dirstr + "/" + str(self.timename)+"_"+str(self.csvcount)+".csv")
        self.csvcount += 1

    '''r_x, r_y는 해상도'''
    def save_heatmap(self, r_x, r_y):
        print('save heatmap called')
        x_index = 100
        y_index = int(r_y * x_index / r_x)  # x가 100일 때 y의 비율 계산
        arr = [[0] * (y_index) for i in range(x_index)]  # 히트맵 표현용 2차원배열
        x_scaler = MinMaxScaler(feature_range=(0, x_index-1))   # 표준화 인스턴스
        y_scaler = MinMaxScaler(feature_range=(0, y_index-1))

        x_scaler.fit([[0], [r_x]])  # 해상도 최대값 설정
        y_scaler.fit([[0], [r_y]])

        pdf = self.df['POSITION'].apply(pd.Series)  # position 만을 담은 데이터프레임
        pdf.columns = ['X', 'Y', 'W', 'H']

        sdf = pdf.copy() # 표준화된 pdf
        sdf[['X', 'W']] = x_scaler.transform(pdf[['X', 'W']])
        sdf[['Y', 'H']] = y_scaler.transform(pdf[['Y', 'H']])
        sdf = sdf.astype(int)

        for row in sdf.iterrows():
            row = row[1]  # 0은 인덱스
            for i in range(row['X'] - int(row['W'] / 2), row['X'] + int(row['W'] / 2)):
                for j in range(row['Y'] - int(row['H'] / 2), row['Y'] + int(row['H'] / 2)):
                    if i >= len(arr) or i < 0 or j >= len(arr[i]) or j < 0:
                        continue
                    arr[i][j] += 1

        sns.set(rc={'figure.figsize': (10, y_index/10)})    # 출력 이미지 사이즈
        fig = sns.heatmap(arr, cbar=False, xticklabels=False, yticklabels=False).get_figure()
        fig.savefig('../test.png', dpi=100)
        print('heatmap saved')