# -*- coding:<UTF-8> -*-

# v0.02 by chalco
# Created 202407120930

import pathlib
import warnings
import pandas as pd
from itertools import chain

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def judge_in_unique_stop_list(unique_stop_list, current_stop_list):
    intersection = list(set(unique_stop_list) & set(current_stop_list))
    return intersection


def stops_to_list(current_list):
    current_list = current_list.strip('[]').replace("'", "")
    return current_list.split(', ')


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_to_open = 'equivalence_stop.csv'
    df = pd.read_csv(data_folder/file_to_open)
    df = df.drop_duplicates(subset=['站点名称'], keep='first')
    unique_stop_ids = df['格式化站点编号'].tolist()
    df['等价站点'] = df.apply(lambda row:stops_to_list(row['等价站点']), axis=1)
    df['等价站点'] = df.apply(lambda row: judge_in_unique_stop_list(unique_stop_ids, row['等价站点']), axis=1)
    df.to_csv(data_folder/'unique_equivalence_stios.csv', index=False, encoding='utf-8')
