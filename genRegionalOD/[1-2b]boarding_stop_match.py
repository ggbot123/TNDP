# -*- coding:<UTF-8> -*-

# v0.20 by chalco
# Created 202407091511

import pathlib
import warnings
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


def parse_boarding_stop_info(stop_name):
    if '的前' in stop_name:
        base_stop, offset = stop_name.split('的前')
        direction = '前'
    elif '的后' in stop_name:
        base_stop, offset = stop_name.split('的后')
        direction = '后'
    else:
        return None, None, None
    offset = int(offset.replace('站',''))
    return base_stop, direction, offset


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/boarding_inference")
    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        file_to_open = data_folder / file_name
        df = pd.read_csv(file_to_open)

        update_df = df[df['更新提醒'] == '是'].copy()
        for idx, row in update_df.iterrows():
            line = str(int(row['线路']))
            direction = 'up' if row['上下行'] == '上行' else 'down'
            stop_name = row['上车站点名称']

            base_stop, dir, offset = parse_boarding_stop_info(stop_name)
            if base_stop is None:
                continue

            stop_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")
            stop_file = f'{line}_{direction}.csv'

            stops_data = pd.read_csv(stop_data_folder/stop_file)
            stop_list = stops_data['站点名称'].tolist()

            if base_stop in stop_list:
                base_index = stop_list.index(base_stop)
                if dir == '前':
                    new_index = max(0, base_index - offset)
                else:
                    new_index = min(len(stop_list) - 1, base_index + offset)
                new_stop_name = stop_list[new_index]
                df.at[row.name, '上车站点名称'] = new_stop_name

        save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/boarding_stop_inference")
        save_name = file_name
        df.to_csv(save_folder/save_name, index=False, encoding='utf-8')

        current_date += timedelta(days=1)
