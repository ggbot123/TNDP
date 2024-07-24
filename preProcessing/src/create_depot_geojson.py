import pandas as pd
import json
from path import root_dir

filename = f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\depot.geojson'
def dict_to_geojson(location_dict):
    features = []
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

if __name__ == '__main__':
    future_depot_df = pd.read_csv(f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\future_depots.csv')
    depot_df = pd.read_csv(f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\depot.csv')
    location_dict = {i: (depot_df.loc[i, '中心点坐标-中国纬度'], depot_df.loc[i, '中心点坐标-中国经度']) for i in depot_df.index}
    # print(location_dict)
    location_dict.update({i+len(depot_df): (future_depot_df.loc[i, 'Latitute'], future_depot_df.loc[i, '经度']) for i in future_depot_df.index})
    print(location_dict)
    geojson_data = dict_to_geojson(location_dict)
    geojson_str = json.dumps(geojson_data, indent=2)
    with open(filename, 'w') as f:
        f.write(geojson_str)
    print("GeoJSON data has been saved to %s" % filename)