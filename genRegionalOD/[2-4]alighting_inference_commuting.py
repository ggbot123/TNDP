# -*- coding:<UTF-8> -*-

# v0.51 by chalco
# Created 202407111529

import pathlib
import warnings
import pandas as pd
import ast

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def infer_alighting_stops(df, equivalence_stops_dict, possible_alighting_stops_dict, stop_name_dict):
    for smartcard_id in df['卡号'].unique():
        commuting_rides = df[df['卡号'] == smartcard_id]
        if len(commuting_rides) == 2:
            first_ride = commuting_rides.iloc[0]
            second_ride = commuting_rides.iloc[1]
            first_boarding_stop = first_ride['格式化上车站点编号']
            second_boarding_stop = second_ride['格式化上车站点编号']

            first_boarding_equivalent_stops = equivalence_stops_dict.get(first_boarding_stop, [])
            first_possible_alighting_stops = possible_alighting_stops_dict.get(first_boarding_stop, [])
            second_boarding_equivalent_stops = equivalence_stops_dict.get(second_boarding_stop, [])
            second_possible_alighting_stops = possible_alighting_stops_dict.get(second_boarding_stop, [])

            first_ride_possible_alighting_stops = [stop for stop in second_boarding_equivalent_stops
                                                   if stop in first_possible_alighting_stops]
            if first_ride_possible_alighting_stops:
                first_ride_inferred_alighting_stop = first_ride_possible_alighting_stops[0]  # 随机选择一个合理的站点
                df.loc[(df['卡号'] == smartcard_id) & (df['刷卡时间'] == first_ride['刷卡时间']), '格式化下车站点编号'] = \
                    first_ride_inferred_alighting_stop
                df.loc[(df['卡号'] == smartcard_id) & (df['刷卡时间'] == first_ride['刷卡时间']), '下车站点名称'] = \
                    stop_name_dict.get(first_ride_inferred_alighting_stop)

            second_ride_possible_alighting_stops = [stop for stop in first_boarding_equivalent_stops
                                                   if stop in second_possible_alighting_stops]
            if second_ride_possible_alighting_stops:
                second_ride_inferred_alighting_stop = second_ride_possible_alighting_stops[0]  # 随机选择一个合理的站点
                df.loc[(df['卡号'] == smartcard_id) & (df['刷卡时间'] == second_ride['刷卡时间']), '格式化下车站点编号'] = \
                    second_ride_inferred_alighting_stop
                df.loc[(df['卡号'] == smartcard_id) & (df['刷卡时间'] == second_ride['刷卡时间']), '下车站点名称'] = \
                    stop_name_dict.get(second_ride_inferred_alighting_stop)


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_name = "通勤.csv"
    df = pd.read_csv(data_folder / file_name)
    df['刷卡时间'] = pd.to_datetime(df['刷卡时间'])

    df = df.sort_values(by=['刷卡时间'])
    equivalence_stop = pd.read_csv(data_folder / 'possible_equivalence_stops.csv')

    # 创建站点等价关系字典
    equivalence_stops_dict = {}
    for _, row in equivalence_stop.iterrows():
        key = row['格式化站点编号']
        equivalent_stops = ast.literal_eval(row['等价站点'])
        equivalence_stops_dict[key] = equivalent_stops

    # 创建可能的下车站点关系字典
    possible_alighting_stops_dict = {}
    for _, row in equivalence_stop.iterrows():
        key = row['格式化站点编号']
        possible_alighting_stops = ast.literal_eval(row['可能的下车站点'])
        possible_alighting_stops_dict[key] = possible_alighting_stops

    # 站点编号和站点名称的字典
    stop_name_dict = {}
    for _, row in equivalence_stop.iterrows():
        stop_name_dict[row['格式化站点编号']] = row['站点名称']

    # 初始化下车站点推断列
    df['格式化下车站点编号'] = None
    df['下车站点名称'] = None

    infer_alighting_stops(df, equivalence_stops_dict, possible_alighting_stops_dict, stop_name_dict)
    df.to_csv(data_folder / 'test.csv', index=False, encoding='utf-8')
