import pandas as pd
from cal_adj_matrix import manhattan
from path import root_dir

routes_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\possible_equivalence_stops.csv')
unique_stop_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\unique_stop_downtown.csv')
# 补全adj_matrix
adj_matrix_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\manhattan_distance_matrix_downtown copy.csv')

def gen_dict():
    stop_name_list = routes_df['站点名称'].unique()
    # 站点名称和同名站点的字典
    stop_name_dict = {}
    for stop_name in stop_name_list:
        sdf = routes_df[routes_df['站点名称'] == stop_name]
        stop_id_list = sdf['格式化站点编号'].tolist()
        stop_name_dict[stop_name] = stop_id_list
    # 站点编号和站点名称的字典
    stop_id_dict = {}
    for _, row in routes_df.iterrows():
        stop_id_dict[row['格式化站点编号']] = row['站点名称']
    return stop_id_dict, stop_name_dict


routes_df['route_id'] = routes_df['格式化站点编号'].str.extract(r'(\w+_\w+_)')[0]
routes_U_downtown_df = routes_df[routes_df['route_id'].str.contains('U') & routes_df['在主城区'] == True]
grouped_routes = routes_U_downtown_df.groupby('route_id')

stop_id_dict, stop_name_dict = gen_dict()
routes = []
for route_id, route in grouped_routes:
    stop_list = []
    prev_stop_id = None
    for stop_id in route['格式化站点编号']:
        stop_name = stop_id_dict[stop_id]
        try:
            unique_stop_id = unique_stop_df[unique_stop_df['格式化站点编号'].isin(stop_name_dict[stop_name])].index.to_list()[0]
        except IndexError:
            continue
        stop_list.append(unique_stop_id)
        # 补全adj_matrix
        if prev_stop_id and adj_matrix_df.loc[prev_stop_id, unique_stop_df.loc[unique_stop_id, '格式化站点编号']] == -1:
            dis = manhattan(unique_stop_df.loc[unique_stop_id, '纬度'], unique_stop_df.loc[unique_stop_id, '经度'],
                                               unique_stop_df.loc[prev_stop_id, '纬度'], unique_stop_df.loc[prev_stop_id, '经度'])
            adj_matrix_df.loc[unique_stop_id, unique_stop_df.loc[prev_stop_id, '格式化站点编号']] = dis
            adj_matrix_df.loc[prev_stop_id, unique_stop_df.loc[unique_stop_id, '格式化站点编号']] = dis
        prev_stop_id = unique_stop_id
    routes.append(stop_list)

for route_id in range(len(routes)):
    print(f'route {route_id}:\n{routes[route_id]}')
with open(f'{root_dir}\\TNDP-Heuristic\\result\\routes-Origin.txt', 'w') as f:
    for route in routes:
        f.write(str(route) + '\n')
adj_matrix_df.to_csv(f'{root_dir}\\preProcessing\\data\\manhattan_distance_matrix_downtown.csv', index=False)
