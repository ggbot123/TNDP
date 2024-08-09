# -*- coding:<UTF-8> -*-

# v0.02 by chalco
# Created 202407120930

import pathlib
import warnings
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def possible_alighting_stops(group):
    line_dir_stop_list = group['格式化站点编号'].tolist()

    def find_alighting_list(row_number):
        possible_alighting_list = line_dir_stop_list[row_number:]
        return possible_alighting_list

    group['可能的下车站点'] = group.apply(lambda row: find_alighting_list(row['单程序号']), axis=1)
    return group


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_to_open = 'equivalence_stop.csv'
    df = pd.read_csv(data_folder/file_to_open)

    df = df.groupby(['线路名称', '线路方向']).apply(possible_alighting_stops)
    df.to_csv(data_folder/'possible_equivalence_stops.csv', index=False, encoding='utf-8')
