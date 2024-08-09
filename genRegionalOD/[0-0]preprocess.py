# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407050917

import pathlib
import warnings
import pandas as pd
from itertools import chain

lines = list(chain(range(1, 34), range(35, 39), [81], range(101, 104), range(105, 110), range(111, 114)))

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")

if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    file_to_open = data_folder / "消费信息明细报表_20240601.csv"
    df = pd.read_csv(file_to_open)

    df = df.drop(
        ['单位', '路队名称', '交易类型', '流水号', '车号', '交易次数', '消费金额', '余额', '驾驶员编号', '下车站点名称',
         '持卡人姓名', '持卡人证件号', '联系方式', '乘客姓名', '乘客证件号', '乘客性别', '乘客民族', '证件签发机关',
         '证件的有效期', '乘客证件地址', '温度', '原始票价', '里程', '乘客类别', '总人数\总件数', '儿童人数',
         '消费次数'], axis=1)

    datetime_format = '%Y-%m-%d %H:%M:%S'
    date = df.iloc[3, 1]
    df['tmpdatetime'] = df['日期'] + ' ' + df['时间']
    df['刷卡时间'] = pd.to_datetime(df['tmpdatetime'], format=datetime_format)
    df = df.drop(['日期', '时间', '上传日期', '上传时间', 'tmpdatetime'], axis=1)
    df = df.dropna(subset='刷卡时间', inplace=False)

    save_folder = pathlib.Path("/Users/chalcozheng/Desktop/graduate/5. 博士生实践/工作处理/IC刷卡数据")
    save_name = str(date) + ".csv"
    df.to_csv(save_folder / save_name, index=False)