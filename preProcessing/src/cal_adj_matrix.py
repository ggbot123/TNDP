import pandas as pd
from geopy.distance import geodesic
import numpy as np
from tqdm import tqdm
from path import root_dir

def manhattan(lat1, lon1, lat2, lon2):
    lat_dis = geodesic((lat1, lon1), (lat2, lon1)).km
    lon_dis = geodesic((lat2, lon1), (lat2, lon2)).km
    return lat_dis + lon_dis 

def euclid(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

if __name__ == '__main__':
    df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\unique_equivalence_stios.csv')
    # 只看主城区内站点
    df = df[df['在主城区'] == True]
    adj_matrix = pd.DataFrame(-1*np.ones([len(df), len(df)]), columns = df['格式化站点编号'], index=df['格式化站点编号'])
    df.index = df['格式化站点编号']
    for stop1 in tqdm(df.index):
        for stop2 in df.index:
            dis = manhattan(df.loc[stop1, '纬度'], df.loc[stop1, '经度'], df.loc[stop2, '纬度'], df.loc[stop2, '经度'])
            route_of_stop1, pos_of_stop1 = (df.loc[stop1, '格式化站点编号'].split('_')[0:2], df.loc[stop1, '格式化站点编号'].split('_')[2])
            route_of_stop2, pos_of_stop2 = (df.loc[stop2, '格式化站点编号'].split('_')[0:2], df.loc[stop2, '格式化站点编号'].split('_')[2])
            is_adj_stop = route_of_stop1 == route_of_stop2 and abs(int(pos_of_stop1) - int(pos_of_stop2)) == 1
            adj_matrix.loc[stop1, stop2] = dis if (dis < 1 and dis > 0.15) or is_adj_stop else -1

    adj_matrix.to_csv(f'{root_dir}\\preProcessing\\data\\manhattan_distance_matrix_downtown.csv')
    # adj_matrix.to_csv(f'{root_dir}\\preProcessing\\data\\manhattan_distance_matrix.csv')
    # adj_matrix.to_csv(f'{root_dir}\\preProcessing\\data\\distance_matrix.csv')