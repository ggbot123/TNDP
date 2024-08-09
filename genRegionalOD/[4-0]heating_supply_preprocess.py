# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407171641

import pathlib
import warnings
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import NearestNeighbors


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = '热力筛选.csv'
    file_to_open = data_folder/file_name
    df = pd.read_csv(file_to_open)

    df = df.drop(columns=['序号', '单位地址', '新编序号', '用户简称'])
    df.rename(columns={'维度': '纬度'}, inplace=True)
    df.to_csv(data_folder/'heating_supply.csv', index=False, encoding='utf-8')

    # file_name = 'heating_supply.csv'
    # file_to_open = data_folder/file_name
    # df = pd.read_csv(file_to_open)

    # print(df['应用热户数'].sum())
    # print(df['实用热户数'].sum())

