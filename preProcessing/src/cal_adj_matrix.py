import pandas as pd
from geopy.distance import geodesic
import numpy as np
from tqdm import tqdm

def manhattan(lat1, lon1, lat2, lon2):
    lat_dis = geodesic((lat1, lon1), (lat2, lon1)).km
    lon_dis = geodesic((lat2, lon1), (lat2, lon2)).km
    return lat_dis + lon_dis 

def euclid(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

df = pd.read_csv('../data/unique_equivalence_stios.csv')
# 只看主城区内站点
df = df[df['在主城区'] == True]
adj_matrix = pd.DataFrame(-1*np.ones([len(df), len(df)]), columns = df['格式化站点编号'], index=df['格式化站点编号'])
df.index = df['格式化站点编号']
for stop1 in tqdm(df.index):
    for stop2 in df.index:
        dis = manhattan(df.loc[stop1, '纬度'], df.loc[stop1, '经度'], df.loc[stop2, '纬度'], df.loc[stop2, '经度'])
        adj_matrix.loc[stop1, stop2] = dis if dis < 1 and dis > 0.15 else -1

adj_matrix.to_csv('../data/manhattan_distance_matrix_downtown.csv')
# adj_matrix.to_csv('../data/manhattan_distance_matrix.csv')
# adj_matrix.to_csv('../data/distance_matrix.csv')