import pandas as pd
import json
from preProcessing.src.cal_adj_matrix import manhattan
from preProcessing.src.create_depot_geojson import dict_to_geojson
from path import root_dir

depot_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\depot.csv')
stop_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\unique_stop_downtown.csv')
location_dict = {i: (depot_df.loc[i, '中心点坐标-中国纬度'], depot_df.loc[i, '中心点坐标-中国经度']) for i in depot_df.index}
# 五四广场附近加个场站
location_dict['五四广场'] = (37.37271, 118.02948)
stop_df['最近depot'] = stop_df.apply(
    lambda row: min(manhattan(lat1, lon1, row['纬度'], row['经度']) for _, (lat1, lon1) in location_dict.items()), axis=1)
depot_list = stop_df[stop_df['最近depot'] < 2].index.to_list()
print(depot_list)
filename = f'{root_dir}\\preProcessing\\data\\stop_near_depot.txt'
with open(filename, 'w') as f:
    f.write(str(depot_list))

filename = f'{root_dir}\\preProcessing\\data\\stop_near_depot.geojson'
location_dict = {i: (stop_df.loc[i, '纬度'], stop_df.loc[i, '经度']) for i in depot_list}
# print(location_dict)
geojson_data = dict_to_geojson(location_dict)
geojson_str = json.dumps(geojson_data, indent=2)
with open(filename, 'w') as f:
    f.write(geojson_str)
print("GeoJSON data has been saved to %s" % filename)