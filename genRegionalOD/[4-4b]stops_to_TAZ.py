# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407181120

import pathlib
import warnings

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = 'possible_equivalence_stops.csv'
    file_to_open = data_folder / file_name
    df = pd.read_csv(file_to_open)
    df = df.drop(columns=['等价站点', '线路名称', '线路方向', '单程序号', '在主城区', '可能的下车站点'])

    taz_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    taz_file_name = 'TAZ_division_grouped.geojson'
    taz_to_open = taz_folder / taz_file_name
    taz = gpd.read_file(taz_to_open, endcoding='utf-8')
    # taz = taz.drop(columns=['质心经度', '应用热户数', '质心纬度'])

    geometry = [Point(xy) for xy in zip(df['经度'], df['纬度'])]
    gdf_stops = gpd.GeoDataFrame(df, geometry=geometry)
    gdf_stops.crs = {'init': 'epsg:4326'}

    gdf_stops = gpd.sjoin(gdf_stops, taz[['geometry', '分组']], how='left', predicate='within')
    gdf_stops = gdf_stops.drop(columns=['geometry', 'index_right'])

    gdf_stops['分组'].fillna(value=-1, inplace=True)

    result_file_name = 'stops_to_TAZ.csv'
    result_file_to_save = data_folder/result_file_name
    gdf_stops.to_csv(result_file_to_save, index=False)
