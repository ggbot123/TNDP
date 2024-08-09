# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407171641

import pathlib
import warnings

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def centroid_calculator(gruop):
    total_heating_families = gruop['应用热户数'].sum()
    weights = gruop['应用热户数']/total_heating_families

    centroid_longitude = (gruop['经度'] * weights).sum()
    centroid_latitude = (gruop['纬度'] * weights).sum()

    gruop_name = gruop['分组'].iloc[0]

    centroid_data = {
        '质心经度': centroid_longitude,
        '质心纬度': centroid_latitude,
        '分组': gruop_name,
        '应用热户数': total_heating_families
    }
    return pd.DataFrame(centroid_data, index=[0])


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = 'heat_supply_clusters.csv'
    file_to_open = data_folder / file_name
    df = pd.read_csv(file_to_open)

    centroid = df.groupby('分组').apply(centroid_calculator).reset_index(drop=True)

    # print(centroid)

    result_file_name = 'grouped_heat_supply_clusters.csv'
    result_file_to_save = data_folder/result_file_name
    centroid.to_csv(result_file_to_save, index=False, encoding='utf-8')

