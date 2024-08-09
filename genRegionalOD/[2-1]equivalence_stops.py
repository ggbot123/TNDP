# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407101714

import pathlib
import warnings
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from itertools import chain

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def is_within_main_city(geometry):
    # 判断站点是否在主城区内
    return geometry.within(convex_main_city)


def calculate_equivalent_stations(stop, all_stops):
    # 计算等价站点
    equivalents = []
    station_point = stop.geometry
    if is_within_main_city(station_point)[0]:
        threshold = 0.004  # 400米
    else:
        threshold = 0.008  # 800米

    for idx, other_station in all_stops.iterrows():
        if stop['站点编号'] != other_station['站点编号']:
            other_point = other_station.geometry
            distance = station_point.distance(other_point)
            if distance <= threshold:
                equivalents.append(other_station['站点编号'])
    return equivalents


if __name__ == '__main__':
    # 读文件
    stops_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")
    geo_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")

    main_city = gpd.read_file(geo_data_folder / '主城区.geojson', endcoing='utf-8')
    convex_main_city = main_city.convex_hull  # 凸包算得快一点

    df = pd.DataFrame(columns=['格式化站点编号', '站点名称', '等价站点', '线路名称',
                               '线路方向', '单程序号', '经度', '纬度', '在主城区'])

    lines = list(chain(range(1, 34), range(35, 39), [81], range(101, 104), range(105, 110), range(111, 114)))
    ud = ['_up', '_down']
    all_stops = []
    for line in lines:
        for direction in ud:
            file_path = stops_data_folder / f"{line}{direction}.csv"
            if file_path.exists():
                stops = pd.read_csv(file_path)
                all_stops.append(stops)
    stops_df = pd.concat(all_stops, ignore_index=True)
    stops_gdf = gpd.GeoDataFrame(stops_df, geometry=gpd.points_from_xy(stops_df['中国经度'], stops_df['中国纬度']),
                                 crs='EPSG:4326')

    for idx, station in stops_gdf.iterrows():
        equivalent_stations = calculate_equivalent_stations(station, stops_gdf)
        in_main_city = is_within_main_city(station.geometry)[0]
        new_row = {
            '格式化站点编号': station['站点编号'],
            '站点名称': station['站点名称'],
            '等价站点': equivalent_stations,
            '线路名称': station['线路名称'],
            '线路方向': station['线路方向'],
            '单程序号': station['单程序号'],
            '经度': station['中国经度'],
            '纬度': station['中国纬度'],
            '在主城区': in_main_city
        }
        df = df.append(new_row, ignore_index=True)

    # 导出结果为CSV文件
    df.to_csv(geo_data_folder/"equivalence_stop.csv", index=False, encoding='utf-8')
    # convex_main_city = gpd.GeoDataFrame(convex_main_city, crs='EPSG:4326', geometry=convex_main_city)


