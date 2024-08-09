# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407181120

import pathlib
import warnings
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import geojson

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    with open('TAZ_division.geojson', 'r', encoding='utf-8') as f:
        data = geojson.load(f)

    for idx, feature in enumerate(data['features']):
        feature['properties']['分组'] = idx + 1

    with open('TAZ_division_grouped.geojson', 'w', encoding='utf-8') as f:
        geojson.dump(data, f, ensure_ascii=False, indent=4)

