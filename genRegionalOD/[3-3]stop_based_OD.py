# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407151736

import pathlib
import warnings
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/OD")
    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        file_to_open = data_folder / file_name
        df = pd.read_csv(file_to_open)
        df = df.dropna(subset='格式化下车站点编号', inplace=False)
        df = df.sort_values(by=['格式化上车站点编号', '格式化下车站点编号'])

        tdf = df.groupby(['格式化上车站点编号', '格式化下车站点编号']).count()
        bdf = pd.DataFrame(tdf)
        bdf.reset_index(inplace=True)
        bdf = bdf.drop(columns=['卡别', '卡号', '线路', '车牌号', '驾驶员姓名', '上下行', '上车站点名称', '刷卡时间', '下车站点名称'])

        save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stop_OD")
        bdf.to_csv(save_folder/file_name, index=False, encoding='utf-8')

        current_date += timedelta(days=1)