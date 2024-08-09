# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407220939

import os.path
import pathlib
import warnings
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard/output")

    df = pd.DataFrame(columns=['original_TAZ','destination_TAZ','volume'])

    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")
    current_date = start_date

    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".csv"
        file_to_open = data_folder / file_name
        if os.path.exists(file_to_open):
            data = pd.read_csv(file_to_open)
            df = pd.concat([df, data], ignore_index=True)
            print(data.head())
        else:
            print(f'file {file_name} not found')

        current_date += timedelta(days=1)

    aggregated_df = df.groupby(['original_TAZ','destination_TAZ']).sum().reset_index()

    save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    aggregated_df.to_csv(save_folder/'TAZ_OD.csv', index=False, encoding='utf-8')
