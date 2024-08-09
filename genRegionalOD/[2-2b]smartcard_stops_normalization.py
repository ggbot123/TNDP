# -*- coding:<UTF-8> -*-

# v0.40 by chalco
# Created 202407111507

import pathlib
import warnings
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def find_stop_file(stop_folder_path, line, direction):
    stop_folder_path, line, direction = str(stop_folder_path), str(int(line)), str(direction)
    if direction == '上行':
        dir = '_up'
    elif direction == '下行':
        dir = '_down'
    else:
        dir = ''
    stop_file_name = f"{stop_folder_path}/{line}{dir}.csv"
    return stop_file_name


def match_normalized_stop_name(stop_file_name, stop_name):
    df_stops = pd.read_csv(stop_file_name)
    condition = df_stops['站点名称'] == stop_name
    normalized_stop_name = df_stops.loc[condition, '站点编号'].values
    return normalized_stop_name[0] if len(normalized_stop_name) > 0 else None


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/boarding_stop_inference")
    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        file_to_open = data_folder / file_name
        df = pd.read_csv(file_to_open)
        df = df.drop(columns=['班次', '更新提醒'])

        id_list = df['卡号'].unique()
        df['一天内刷卡数'] = 0
        for id in id_list:
            same_id_condition = df['卡号'] == id
            df.iloc[same_id_condition, 8] = len(df[same_id_condition])

        stop_folder_path = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")
        df['格式化上车站点编号'] = df.apply(lambda row: match_normalized_stop_name(
            find_stop_file(stop_folder_path, row['线路'], row['上下行']), row['上车站点名称']),axis=1)

        save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/normalized_boarding")
        df.to_csv(save_folder / file_name, index=False, encoding='utf-8')

        current_date += timedelta(days=1)
