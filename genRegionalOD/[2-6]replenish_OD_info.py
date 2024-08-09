# -*- coding:<UTF-8> -*-

# v1.20 by chalco
# Created 202407151520

import pathlib
import warnings
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    base_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/OD")
    convert_data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/new_OD")

    file_name = "2024-06-01.csv"
    base_df = pd.read_csv(base_data_folder/file_name)
    more_df = pd.read_csv(convert_data_folder/file_name)

    base_df_null = base_df[base_df['格式化下车站点编号'].isnull()]
    more_df_null = more_df[more_df['格式化下车站点编号'].isnull()]

    print(f'修补前：')
    print(f'base_df的总行数：{len(base_df)}，base_df的空行数：{len(base_df_null)}')
    print(f'more_df的总行数：{len(more_df)}，more_df的空行数：{len(more_df_null)}')
    # print(base_df.head(30))

    # 方法一：combine first(x)
    # df_merged = base_df.combine_first(more_df)
    # df_merged_null = df_merged[df_merged['格式化下车站点编号'].isnull()]
    # print(f'修补后：')
    # print(f'merged_df的总行数：{len(df_merged)}，merged_df的空行数：{len(df_merged_null)}')

    # 方法二：loc
    missing_indices = base_df[base_df['格式化下车站点编号'].isna()].index
    if len(more_df) < len(missing_indices):
        raise ValueError("more_df中的行数不足以填补base_df中的空值")
    # print(f'缺失行数：{len(missing_indices)}')
    # base_df.loc[missing_indices, '格式化下车站点编号'] = more_df['格式化下车站点编号']
    # base_df.loc[missing_indices, '下车站点名称'] = more_df['下车站点名称']
    for i, idx in enumerate(missing_indices):
        base_df.at[idx, '格式化下车站点编号'] = more_df.at[i, '格式化下车站点编号']
        base_df.at[idx, '下车站点名称'] = more_df.at[i, '下车站点名称']

    base_df_null = base_df[base_df['格式化下车站点编号'].isnull()]
    print(f'修补后：')
    print(f'base_df的总行数：{len(base_df)}，base_df的空行数：{len(base_df_null)}')


    # save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    # base_df.to_csv(save_folder /'test.csv', index=False, encoding='utf-8')
    # print(base_df.head(30))


