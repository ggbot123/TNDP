# -*- coding:<UTF-8> -*-

# v0.03 by chalco
# Created 202407160921

import pathlib
import warnings
import pandas as pd
from itertools import chain

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    stop_name_file = 'possible_equivalence_stops.csv'
    stop_name_df = pd.read_csv(data_folder/stop_name_file)

    stop_name_list = stop_name_df['站点名称'].unique()

    # 站点名称和同名站点的字典
    stop_name_to_same_name_dict = {}
    for stop_name in stop_name_list:
        sdf = stop_name_df[stop_name_df['站点名称'] == stop_name]
        stop_id_list = sdf['格式化站点编号'].tolist()
        stop_name_to_same_name_dict[stop_name] = stop_id_list

    # 站点编号和站点名称的字典
    stop_id_to_name_dict = {}
    for _, row in stop_name_df.iterrows():
        stop_id_to_name_dict[row['格式化站点编号']] = row['站点名称']
