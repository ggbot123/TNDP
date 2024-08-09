# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407171641

import pathlib
import warnings

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import NearestNeighbors

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


# 加权距离计算
def heating_weighed_distance(p1, p2, w1, w2):
    dist = np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
    weight = (w1 + w2) / 2
    return dist / weight


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = 'heating_supply.csv'
    file_to_open = data_folder / file_name
    df = pd.read_csv(file_to_open)

    geometry = [Point(xy) for xy in zip(df['经度'], df['纬度'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.crs = {'init': 'epsg:4326'}

    # 供热户数的阈值和聚类距离阈值
    heating_families_threshold = 12000
    distance_threshold = 1

    # 初始化
    gdf['cluster'] = -1
    cluster_id = 0

    while gdf[gdf['cluster'] == -1].shape[0] > 0:
        unassigned = gdf[gdf['cluster'] == -1]
        seed_index = unassigned.index[0]
        gdf.at[seed_index, 'cluster'] = cluster_id
        current_cluster = [seed_index]
        current_units = gdf.at[seed_index, '应用热户数']

        while current_units < heating_families_threshold and len(current_cluster) > 0:
            current_point = gdf.loc[current_cluster[0]]
            neighbors = unassigned.loc[unassigned.index.difference(current_cluster)]
            distances = neighbors.apply(
                lambda row: heating_weighed_distance(current_point.geometry, row.geometry,
                                                     current_point['应用热户数'], row['应用热户数']), axis=1)
            nearest_neighbor = distances.idxmin()

            # 检查距离阈值
            if distances[nearest_neighbor] <= distance_threshold:
                if current_units + gdf.at[nearest_neighbor, '应用热户数'] <= heating_families_threshold:
                    gdf.at[nearest_neighbor, 'cluster'] = cluster_id
                    current_units += gdf.at[nearest_neighbor, '应用热户数']
                    current_cluster.append(nearest_neighbor)
            current_cluster.pop(0)
        cluster_id += 1

    df['分组'] = gdf['cluster']

    # 合并小聚类
    min_cluster_size = 4
    cluster_counts = df['分组'].value_counts()
    small_clusters = cluster_counts[cluster_counts < min_cluster_size].index
    for small_cluster in small_clusters:
        df.loc[df['分组'] == small_cluster, '分组'] = -1
    unassigned = df[df['分组'] == -1]
    for index, row in unassigned.iterrows():
        nearest_cluster = gdf.apply(
            lambda r: heating_weighed_distance(Point(row['经度'], row['纬度']), r.geometry,
                                               row['应用热户数'], r['应用热户数']), axis=1)
        df.at[index, '分组'] = gdf.at[nearest_cluster, 'cluster']

    result_file_name = 'heat_supply_clusters.csv'
    result_file_to_save = data_folder/result_file_name
    df.to_csv(result_file_to_save, index=False, encoding='utf-8')

