import json
import pandas as pd

def dict_to_geojson(route_dict, location_dict):
    features = []
    for route_name, stations in route_dict.items():
        # 创建线路的坐标列表
        route_coords = [(location_dict[station][1], location_dict[station][0]) for station in stations]
        # 创建GeoJSON feature
        feature = {
            "type": "Feature",
            "properties": {
                "name": route_name
            },
            "geometry": {
                "type": "LineString",
                "coordinates": route_coords
            }
        }
        features.append(feature)
    # 创建GeoJSON对象
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson

def create_geojson(routes):
    stop_df = pd.read_csv('D:\\learning\\workspace\\python\\TNDP\\preProcessing\\data\\unique_stop_downtown.csv')
    # print(stop_df.index)
    route_dict = {('route %d' % i): routes[i] for i in range(len(routes))}
    # print(route_dict)
    location_dict = {i: (stop_df.loc[i, '纬度'], stop_df.loc[i, '经度']) for i in stop_df.index}
    # print(location_dict)
    geojson_data = dict_to_geojson(route_dict, location_dict)
    
    geojson_str = json.dumps(geojson_data, indent=2)
    with open('D:\\learning\\workspace\\python\\TNDP\\TNDP-Heuristic\\result\\lines.geojson', 'w') as f:
        f.write(geojson_str)
    print("GeoJSON data has been saved to 'lines.geojson'")