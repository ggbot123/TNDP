# -*- coding:<UTF-8> -*-

# v0.01 by chalco
# Created 202407221440

import pathlib
import warnings
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_folder = pathlib.Path("/Users/chalcozheng/PycharmProjects/pythonProject/IC_Smartcard")
    df = pd.read_csv(data_folder/'final_OD.csv')


