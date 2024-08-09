# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407081538

import pathlib
import warnings
import pandas as pd
from itertools import chain
from datetime import timedelta
import re

lines = list(chain(range(1, 34), range(35, 39), [81], range(101, 104), range(105, 110), range(111, 114)))

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def filter_bus_card_data(df):
    # 同一卡号，在两分钟之内，在同一驾驶员姓名下，出现多次刷卡记录的，仅保留第一次刷卡的记录，删去其他的刷卡记录。
    df = df.sort_values(by=['卡号', '驾驶员姓名', '上下行', '上车站点名称', '刷卡时间'])
    df['时间差_2分钟'] = df.groupby(['卡号', '驾驶员姓名'])['刷卡时间'].diff().dt.total_seconds().div(60)
    # 同一卡号，同一驾驶员，同一上下行，同一上车站点的，在60分钟之内的重复刷卡，只保留第一次刷卡的记录，其他的删去。
    df['时间差_60分钟'] = df.groupby(['卡号', '驾驶员姓名', '上下行', '上车站点名称'])[
        '刷卡时间'].diff().dt.total_seconds().div(60)
    filtered_df = df[
        (df['时间差_2分钟'].isna() | (df['时间差_2分钟'] > 2)) &
        (df['时间差_60分钟'].isna() | (df['时间差_60分钟'] > 60))
        ]
    filtered_df = filtered_df.drop(columns=['时间差_2分钟', '时间差_60分钟'])
    return filtered_df.sort_values('刷卡时间')


def fill_missing_stops(df):
    # 上行推断
    df.sort_values(by=['上下行', '刷卡时间'], inplace=True)  # 先按照“上下行”字段和时间划分不同的班次
    df['班次'] = (df['上下行'] != df['上下行'].shift()) | (df['刷卡时间'] - df['刷卡时间'].shift() > timedelta(hours=1))
    df['班次'] = df['班次'].cumsum()

    def fill_stops(group):
        group['更新提醒'] = ''
        if group['上车站点名称'].isnull().all():
            return pd.DataFrame()  # 如果整个班次上车站点名称全部为空，删除该班次
        elif group['上车站点名称'].isnull().any():
            for i in range(len(group)):
                if pd.isnull(group.iloc[i]['上车站点名称']):
                    prev_stop_name = None
                    prev_stop_time = None
                    j = i - 1
                    while j >= 0:
                        if pd.notnull(group.iloc[j]['上车站点名称']):
                            prev_stop_name = group.iloc[j]['上车站点名称']
                            prev_stop_time = group.iloc[j]['刷卡时间']
                            break
                        j -= 1
                    next_stop_name = None
                    next_stop_time = None
                    k = i + 1
                    while k < len(group):
                        if pd.notnull(group.iloc[k]['上车站点名称']):
                            next_stop_name = group.iloc[k]['上车站点名称']
                            next_stop_time = group.iloc[k]['刷卡时间']
                            break
                        k += 1

                    # 记录站间次数，简化描述
                    def simplify_description(description):
                        parts = description.split('的')
                        final_count = 0
                        base_station = parts[0]
                        for part in parts[1:]:
                            pattern = r'\d+'
                            if '前' in part:
                                # 这里有个bug，比如算出来是前几十站就很抽象
                                count = int(re.findall(pattern, part)[0])
                                final_count -= count
                            elif '后' in part:
                                count = int(re.findall(pattern, part)[0])
                                final_count += count
                        if final_count > 0:
                            return f"{base_station}的后{final_count}站"
                        elif final_count < 0:
                            return f"{base_station}的前{-final_count}站"
                        else:
                            return base_station

                    if prev_stop_name and next_stop_name:
                        # 既有前一个非空站点也有后一个非空站点
                        prev_time_diff = group.iloc[i]['刷卡时间'] - prev_stop_time
                        prev_stops_diff = int(prev_time_diff.total_seconds() / 120)
                        next_time_diff = next_stop_time - group.iloc[i]['刷卡时间']
                        next_stops_diff = int(next_time_diff.total_seconds() / 120)
                        if prev_stops_diff <= next_stops_diff:
                            new_description = f"{prev_stop_name}的后{prev_stops_diff}站"
                        else:
                            new_description = f"{next_stop_name}的前{next_stops_diff}站"
                        group.at[group.index[i], '上车站点名称'] = simplify_description(new_description)
                        group.at[group.index[i], '更新提醒'] = '是'
                    elif prev_stop_name:
                        # 只有前一个非空站点
                        time_diff = group.iloc[i]['刷卡时间'] - prev_stop_time
                        stops_diff = int(time_diff.total_seconds() / 120)
                        new_description = f"{prev_stop_name}的后{stops_diff}站"
                        group.at[group.index[i], '上车站点名称'] = simplify_description(new_description)
                        group.at[group.index[i], '更新提醒'] = '是'
                    elif next_stop_name:
                        time_diff = next_stop_time - group.iloc[i]['刷卡时间']
                        stops_diff = int(time_diff.total_seconds() / 120)
                        new_description = f"{next_stop_name}的前{stops_diff}站"
                        group.at[group.index[i], '上车站点名称'] = simplify_description(new_description)
                        group.at[group.index[i], '更新提醒'] = '是'
        return group

    # 对每个班次进行处理
    df = df.groupby('班次').apply(fill_stops).reset_index(drop=True)
    # return df.sort_values('刷卡时间')
    return df


if __name__ == '__main__':
    # 读文件
    ic_data_folder = pathlib.Path("/Users/chalcozheng/Desktop/graduate/5. 博士生实践/工作处理/IC刷卡数据")
    file_name = "2024-06-01.csv"
    ic_file_to_open = ic_data_folder/file_name
    df = pd.read_csv(ic_file_to_open)
    df = df[df['线路'].isin(lines)]
    df['刷卡时间'] = pd.to_datetime(df['刷卡时间'])
    # 去重
    df = filter_bus_card_data(df)

    updated_df = pd.DataFrame()
    buses = df['驾驶员姓名'].unique()
    for bus in buses:
        bdf = df[df['驾驶员姓名'] == bus]
        if bdf['上车站点名称'].isnull().sum():  # 这个是刚好判断如果没有上车站点信息是空，就不用管了；有上车站点是空的情况才处理。
            bdf = fill_missing_stops(bdf)
        updated_df = pd.concat([updated_df, bdf])

    save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    updated_df.to_csv(save_folder/file_name, index=False, encoding='utf-8')

    # bdf = df[df['驾驶员姓名'] == '张海滨']
    # sbdf = fill_missing_stops(bdf)