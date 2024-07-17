import pandas as pd
import numpy as np

df = pd.read_csv('../data/unique_equivalence_stios.csv')
OD_df = pd.read_csv('../data/OD_unique_downtown.csv')

df = df[df['在主城区']==True]
print(df)
df.to_csv('../data/unique_stop_downtown.csv', index=False)
OD_matrix = pd.DataFrame(np.zeros([len(df), len(df)]), columns = df['格式化站点编号'], index=df['格式化站点编号'])
for i in OD_df.index:
    O_name = OD_df.loc[i, '格式化上车站点编号']
    D_name = OD_df.loc[i, '格式化下车站点编号']
    OD_matrix.loc[O_name, D_name] = OD_df.loc[i, '一天内刷卡数']
print(OD_matrix)
OD_matrix.to_csv('../data/Binzhou_route_OD_downtown.csv')
# OD_matrix.to_csv('../data/manhattan_distance_matrix.csv')