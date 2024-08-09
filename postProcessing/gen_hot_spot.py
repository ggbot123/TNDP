import pandas as pd
import numpy as np
import ast

def create_csv():
    df = pd.DataFrame(-1*np.ones([118, 2]), columns=['交通小区编号', '主要发生/吸引源示例'])
    df1 = pd.read_csv(r'D:\learning\workspace\python\TNDP\postProcessing\result\TAZ1.csv')
    df2 = pd.read_csv(r'D:\learning\workspace\python\TNDP\postProcessing\result\TAZ2.csv')
    for i in range(len(df1)):
        df.loc[2*i, :] = df1.loc[i, :]
    for i in range(len(df2)):
        df.loc[2*i+1, :] = df2.loc[i, :]
    df['交通小区编号'] = df['交通小区编号'].astype(int)

    df.to_csv(r'D:\learning\workspace\python\TNDP\postProcessing\result\TAZ.csv')

# create_csv()
df = pd.read_csv(r'D:\learning\workspace\python\TNDP\postProcessing\result\TAZ.csv')
routes = []
with open(r'D:\learning\workspace\python\TNDP\TNDP-Heuristic\result\txt\routes-Final-revised.txt', 'r') as f:
    for line in f:
        routes.append(ast.literal_eval(line.strip()))
with open(r'D:\learning\workspace\python\TNDP\postProcessing\result\routes_main_TAZ.txt', 'w') as f:
    for route in routes:
        TAZs = [df.loc[i, '主要发生/吸引源示例'] for i in route]
        for TAZ in TAZs:
            f.write(f'{TAZ}，')
        f.write('\n')
