# -*- coding:<UTF-8> -*-

# v1.20 by chalco
# Created 202407151520

import pathlib
import warnings
import pandas as pd
import ast
from datetime import timedelta, datetime
from tqdm import tqdm

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")

# 先创建字典
dict_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
equivalence_stop = pd.read_csv(dict_data_folder / 'possible_equivalence_stops.csv')
equivalence_stops_dict = {}
possible_alighting_stops_dict = {}
stop_name_dict = {}

for _, row in equivalence_stop.iterrows():
    key = row['格式化站点编号']
    equivalence_stops_dict[key] = ast.literal_eval(row['等价站点'])  # 创建站点等价关系字典
    possible_alighting_stops_dict[key] = ast.literal_eval(row['可能的下车站点'])  # 创建可能的下车站点关系字典
    stop_name_dict[key] = row['站点名称']  # 站点编号和站点名称的字典


def infer_alighting_stops(boarding_stop, stops_to_check, stop_name_dict):
    # 强制判断站点关系
    inferred_alighting_stop, inferred_alighting_stop_name = None, None
    stops_to_check = list(set(stops_to_check) - {boarding_stop})  # 排除待定站点自身的等价站点
    for stop_to_check in stops_to_check:
        first_possible_alighting_stops = possible_alighting_stops_dict.get(boarding_stop, [])
        second_boarding_equivalent_stops = equivalence_stops_dict.get(stop_to_check, [])
        possible_alighting_stops = [stop for stop in second_boarding_equivalent_stops
                                    if stop in first_possible_alighting_stops]
        if possible_alighting_stops:
            inferred_alighting_stop = possible_alighting_stops[0]
            inferred_alighting_stop_name = stop_name_dict.get(inferred_alighting_stop)
            break
    return inferred_alighting_stop, inferred_alighting_stop_name


def obtain_records_overdays(smartcard_id, start_date, search_days_delta=timedelta(days=2)):
    # 同一ID多搜索几天的记录数据
    records = pd.DataFrame()
    smartcard_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/OD")
    current_date = start_date
    end_date = start_date + search_days_delta
    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        file_to_open = smartcard_data_folder / file_name
        append_df = pd.read_csv(file_to_open)

        append_df = append_df[append_df['卡号'] == smartcard_id]
        if not append_df.empty:
            records = records.append(append_df)
        current_date += timedelta(days=1)
    return records.reset_index()


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/OD")
    file_name = "2024-06-02.csv"
    df = pd.read_csv(data_folder / file_name)
    df['刷卡时间'] = pd.to_datetime(df['刷卡时间'])
    df = df.sort_values(by=['刷卡时间'])

    # 筛选缺失值
    df = df[df['格式化下车站点编号'].isnull()]

    for smartcard_id in df['卡号'].unique():
        card_df = df[df['卡号'] == smartcard_id]
        records_df = obtain_records_overdays(smartcard_id, start_date=datetime.strptime("2024-06-01", "%Y-%m-%d"))
        if not records_df.empty:
            records_boarding_stops = records_df['格式化上车站点编号'].unique()
            for idx, row in card_df.iterrows():
                boarding_stop = row['格式化上车站点编号']
                inferred_alighting_stop, inferred_alighting_stop_name = \
                    infer_alighting_stops(boarding_stop, records_boarding_stops, stop_name_dict)
                df.loc[(df['卡号'] == smartcard_id) & (df['刷卡时间'] == row['刷卡时间']),
                       '格式化下车站点编号'] = inferred_alighting_stop
                df.loc[(df['卡号'] == smartcard_id) & (df['刷卡时间'] == row['刷卡时间']),
                       '下车站点名称'] = inferred_alighting_stop_name

    save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    df.to_csv(save_folder/'2024-06-02.csv', index=False, encoding='utf-8')
