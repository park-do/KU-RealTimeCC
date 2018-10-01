import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns


class Analyzer:
    df = pd.DataFrame()  # 분석 데이터 저장할 데이터 프레임

    '''생성자'''
    def __init__(self):
        self.df = pd.DataFrame(columns=['OBJECT', 'ACCURACY', 'POSITION', 'TIME'])

    '''데이터 로우 추가'''
    def add_row(self, detection):
        now = str(datetime.now())
        for row in detection:
            if row[0] == 'person':  # 사람만 추가함
                row = list(row)  # tuple을 list로
                row.append(now)  # 현재 시간 추가
                self.df.loc[len(self.df)] = row

    '''결과 저장 함수'''
    def to_csv(self):
        self.df.to_csv('c:/test/test.csv')

