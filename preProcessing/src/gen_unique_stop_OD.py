import pandas as pd
import pathlib

# 读文件
data_folder = pathlib.Path("D:\learning\workspace\python\TNDP\preProcessing\data")
stop_name_file = 'possible_equivalence_stops.csv'
stop_name_df = pd.read_csv(data_folder/stop_name_file)
stop_name_list = stop_name_df['站点名称'].unique()

# 站点名称和同名站点的字典
stop_name_dict = {}
for stop_name in stop_name_list:
    sdf = stop_name_df[stop_name_df['站点名称'] == stop_name]
    stop_id_list = sdf['格式化站点编号'].tolist()
    stop_name_dict[stop_name] = stop_id_list

# 站点编号和站点名称的字典
stop_id_dict = {}
for _, row in stop_name_df.iterrows():
    stop_id_dict[row['格式化站点编号']] = row['站点名称']

OD_name_file = 'OD_groupby.csv'
OD_name_df = pd.read_csv(data_folder/OD_name_file)

OD_name_df['格式化上车站点编号'] = OD_name_df.apply(
    lambda row: stop_name_dict[stop_id_dict[row['格式化上车站点编号']]][0], axis=1)
OD_name_df['格式化下车站点编号'] = OD_name_df.apply(
    lambda row: stop_name_dict[stop_id_dict[row['格式化下车站点编号']]][0], axis=1)

OD_name_df = OD_name_df.groupby(['格式化上车站点编号', '格式化下车站点编号'])['一天内刷卡数'].sum()
print(OD_name_df)
OD_name_df.to_csv(data_folder/'OD_unique.csv')