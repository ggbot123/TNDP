# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407181502

import pathlib
import warnings
import numpy as np
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")

# 创建站点对应分组的字典
dict_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
stop_to_taz_csv = pd.read_csv(dict_data_folder/'stops_to_TAZ.csv')
stop_to_taz_dict = {}
for _, row in stop_to_taz_csv.iterrows():
    key = row['格式化站点编号']
    stop_to_taz_dict[key] = row['分组']


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/OD")
    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        file_to_open = data_folder / file_name
        df = pd.read_csv(file_to_open)

        df['original_TAZ'] = df['格式化上车站点编号'].map(stop_to_taz_dict)
        df['destination_TAZ'] = df['格式化下车站点编号'].map(stop_to_taz_dict)

        result = df.groupby(['original_TAZ', 'destination_TAZ'], as_index=False)['一天内刷卡数'].sum()
        result.rename(columns={'一天内刷卡数': 'volume'}, inplace=True)

        output_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/output")
        result_file_name = file_name
        result.to_csv(output_folder/result_file_name, index=False, encoding='utf-8')

        current_date += timedelta(days=1)