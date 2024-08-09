# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407220939

import pathlib
import warnings
import numpy as np
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    df = pd.read_csv(data_folder/'TAZ_OD.csv')

    min_taz = int(df['original_TAZ'].min())
    max_taz = int(df['original_TAZ'].max())

    taz_range = [i for i in range(min_taz, max_taz+1) if i != 0]

    matrix_df = pd.DataFrame(0, index=taz_range, columns=taz_range)

    for _, row in df.iterrows():
        original = row['original_TAZ']
        destination = row['destination_TAZ']
        volume = row['volume']
        matrix_df.at[original, destination] = volume

    save_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    matrix_df.to_csv(save_folder/'final_OD.csv', index=True, encoding='utf-8')
