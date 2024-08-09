# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407081433

import pathlib
import warnings
import pandas as pd
from itertools import chain

lines = list(chain(range(1, 34), range(35, 39), [81], range(101, 104), range(105, 110), range(111, 114)))

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def format_line_name(line_name):
    number_part = ''.join(filter(str.isdigit, str(line_name)))
    return number_part.zfill(3)


def format_single_trip_number(single_trip_number):
    return str(single_trip_number).zfill(2)


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_to_open = data_folder/"线路站点_zch.xlsx"
    df = pd.read_excel(file_to_open)

    df = df.drop(['站点自编号', '国际经度', '国际纬度', '线路轨迹', '第三方单程序号', '第三方双程序号'], axis=1)

    df['格式化线路名称'] = df['线路名称'].apply(format_line_name)
    df['格式化单程序号'] = df['单程序号'].apply(format_single_trip_number)

    for line in lines:
        formatted_line_name = format_line_name(line)

        up_line_df = df[(df['格式化线路名称'] == formatted_line_name) & (df['线路方向'] == '上行')].copy()
        down_line_df = df[(df['格式化线路名称'] == formatted_line_name) & (df['线路方向'] == '下行')].copy()

        # 添加上下行标记
        up_line_df['上下行'] = 'U'
        down_line_df['上下行'] = 'D'

        # 生成新的站点编号
        up_line_df['站点编号'] = up_line_df.apply(
            lambda x: f"{x['格式化线路名称']}_{x['上下行']}_{x['格式化单程序号']}", axis=1)
        down_line_df['站点编号'] = down_line_df.apply(
            lambda x: f"{x['格式化线路名称']}_{x['上下行']}_{x['格式化单程序号']}", axis=1)

        # 保存为CSV文件
        save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")
        up_line_df.to_csv(save_folder / f"{line}_up.csv", index=False, encoding='utf-8')
        down_line_df.to_csv(save_folder / f"{line}_down.csv", index=False, encoding='utf-8')
