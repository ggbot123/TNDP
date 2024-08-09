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

    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        base_df = pd.read_csv(base_data_folder/file_name)
        more_df = pd.read_csv(convert_data_folder / file_name)

        base_df_null = base_df[base_df['格式化下车站点编号'].isnull()]
        more_df_null = more_df[more_df['格式化下车站点编号'].isnull()]

        missing_indices = base_df[base_df['格式化下车站点编号'].isna()].index
        if len(more_df) < len(missing_indices):
            raise ValueError("more_df中的行数不足以填补base_df中的空值")

        for i, idx in enumerate(missing_indices):
            base_df.at[idx, '格式化下车站点编号'] = more_df.at[i, '格式化下车站点编号']
            base_df.at[idx, '下车站点名称'] = more_df.at[i, '下车站点名称']

        base_df_null = base_df[base_df['格式化下车站点编号'].isnull()]

        save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/replenish_OD")
        base_df.to_csv(save_folder /file_name, index=False, encoding='utf-8')

        current_date += timedelta(days=1)
