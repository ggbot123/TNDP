import json
import pandas as pd
import ast
from path import root_dir

def dict_to_geojson(route_dict, location_dict):
    features = []
    for route_name, stops in route_dict.items():
        # 创建线路的坐标列表
        route_coords = [(location_dict[stop][1], location_dict[stop][0]) for stop in stops]
        # 创建GeoJSON feature
        route_feature = {
            "type": "Feature",
            "properties": {
                "name": route_name
            },
            "geometry": {
                "type": "LineString",
                "coordinates": route_coords
            }
        }
        features.append(route_feature)
    # 添加站点的GeoJSON Feature
    for stop_id, (lat, lon) in location_dict.items():
        stop_feature = {
            "type": "Feature",
            "properties": {
                "stop_id": stop_id
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        }
        features.append(stop_feature)
    # 创建GeoJSON对象
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson

def create_geojson(routes, filename):
    stop_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\unique_stop_downtown.csv')
    # print(stop_df.index)
    route_dict = {('route %d' % i): routes[i] for i in range(len(routes))}
    # print(route_dict)
    location_dict = {i: (stop_df.loc[i, '纬度'], stop_df.loc[i, '经度']) for i in stop_df.index}
    # print(location_dict)
    geojson_data = dict_to_geojson(route_dict, location_dict)
    geojson_str = json.dumps(geojson_data, indent=2)
    with open(filename, 'w') as f:
        f.write(geojson_str)
    print("GeoJSON data has been saved to %s" % filename)

if __name__ == '__main__':
    routes = []
    with open('../result/routes_0718.txt', 'r') as f:
        for line in f:
            routes.append(ast.literal_eval(line.strip()))
        print(routes)
    create_geojson(routes, filename=f'{root_dir}\\TNDP-Heuristic\\result\\routes-SBS-0718.geojson')