# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407181110

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
    dist = np.sqrt(648*(p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
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
    heating_families_threshold = 2000
    distance_threshold = 0.05

    # 初始化
    gdf['cluster'] = -1
    cluster_id = 0

    coords = np.array(list(zip(df['经度'], df['纬度'])))
    nbrs = NearestNeighbors(n_neighbors=len(df), algorithm='ball_tree').fit(coords)
    distance, indices = nbrs.kneighbors(coords)

    while gdf[gdf['cluster'] == -1].shape[0] > 0:
        unassigned = gdf[gdf['cluster'] == -1]
        seed_index = unassigned.index[0]
        gdf.at[seed_index, 'cluster'] = cluster_id
        current_cluster = [seed_index]
        current_units = gdf.at[seed_index, '应用热户数']

        while current_units < heating_families_threshold and len(current_cluster) > 0:
            current_point_index = current_cluster[0]
            current_point_neighbors = indices[current_point_index]
            for neighbor_index in current_point_neighbors:
                if neighbor_index != current_point_index and gdf.at[neighbor_index, 'cluster'] == -1:
                    neighbor_point = gdf.loc[neighbor_index]
                    dist = heating_weighed_distance(
                        gdf.at[current_point_index, 'geometry'],
                        neighbor_point['geometry'],
                        gdf.at[current_point_index, '应用热户数'],
                        neighbor_point['应用热户数']
                    )
                    if dist <= distance_threshold:
                        if current_units + neighbor_point['应用热户数'] <= heating_families_threshold:
                            gdf.at[neighbor_index, 'cluster'] = cluster_id
                            current_units += neighbor_point['应用热户数']
                            current_cluster.append(neighbor_index)
                if current_units >= heating_families_threshold:
                    break
            current_cluster.pop(0)
        cluster_id += 1

    df['分组'] = gdf['cluster']

    result_file_name = 'heat_supply_clusters.csv'
    result_file_to_save = data_folder/result_file_name
    df.to_csv(result_file_to_save, index=False, encoding='utf-8')

