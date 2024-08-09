# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407151736

import pathlib
import warnings
import pandas as pd
import itertools

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/OD")
    file_to_open = '2024-06-03.csv'
    df = pd.read_csv(data_folder/file_to_open)
    df = df.dropna(subset='格式化下车站点编号', inplace=False)
    df = df.sort_values(by=['格式化上车站点编号', '格式化下车站点编号'])

    stop_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    stop_file_to_open = 'possible_equivalence_stops.csv'
    stop_df = pd.read_csv(stop_folder/stop_file_to_open)
    stop_list = stop_df['格式化站点编号'].tolist()

    tdf = df.groupby(['格式化上车站点编号', '格式化下车站点编号']).count()
    bdf = pd.DataFrame(tdf)
    bdf.reset_index(inplace=True)
    bdf = bdf.drop(columns=['卡别', '卡号', '线路', '车牌号', '驾驶员姓名', '上下行', '上车站点名称', '刷卡时间', '下车站点名称'])
    bdf.to_csv(stop_folder/'OD_groupby.csv', index=False, encoding='utf-8')

