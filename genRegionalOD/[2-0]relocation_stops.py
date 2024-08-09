# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407101444

import pathlib
import warnings
import pandas as pd
from itertools import chain, product

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    # 读文件
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/stops")
    lines = list(chain(range(1, 34), range(35, 39), [81], range(101, 104), range(105, 110), range(111, 114)))
    ud = ['_up', '_down']

    file_name_list = list(product(lines, ud))
    for file_names in file_name_list:
        file_name = str(file_names[0])+str(file_names[1])+'.csv'
        file_path = data_folder/file_name
        df = pd.read_csv(file_path)
        condition = (df['站点名称'] == '沪滨医院') & (df['线路方向'] == '下行')
        if not df[condition].empty:
            df.iloc[condition, 3] = 118.024177
            df.to_csv(file_path, index=False)
            # print(df[condition])
