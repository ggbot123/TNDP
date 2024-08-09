# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407181529

import pathlib
import warnings
from shapely.geometry import Polygon
from scipy.spatial import Voronoi
import geopandas as gpd
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = 'TAZ_division.geojson'
    file_to_open = data_folder / file_name

    boundary_file_name = 'boundary.geojson'
    boundary_file_to_open = data_folder/boundary_file_name

    gdf = gpd.read_file(file_to_open)
    boundary_gdf = gpd.read_file(boundary_file_to_open)
    boundary_polygon = boundary_gdf.unary_union

    gdf = gdf.intersection(boundary_polygon)

    gdf.to_file('TAZ_division.geojson', driver='Geojson')


