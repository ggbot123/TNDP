# -*- coding:<UTF-8> -*-

# v0.01 by chalco & ChatGPT
# Created 202407300857

import processing
from qgis.core import QgsPointXY, QgsProject, QgsVectorLayer, QgsGeometry

# 定义输入图层
road_network_layer = QgsProject.instance().mapLayersByName("Output layer")[0]
points_layer = QgsProject.instance().mapLayersByName("line_26")[0]

points = [feat.geometry().asPoint() for feat in points_layer.getFeatures()]

if not points:
    print("顶点图层为空，没有可用的起点。")
    exit()

# 第一个点作为起点
start_point = points[0]
# 剩余的点作为终点
end_points = points[1:]

# 创建用于存储路径的图层
output_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "shortest_paths", "memory")
provider = output_layer.dataProvider()
QgsProject.instance().addMapLayer(output_layer)

for i, end_point in enumerate(end_points):
    # 定义参数
    params = {
        'INPUT': road_network_layer,
        'STRATEGY': 0,
        'DIRECTION_FIELD': '',
        'VALUE_FORWARD': '',
        'VALUE_BACKWARD': '',
        'VALUE_BOTH': '',
        'DEFAULT_DIRECTION': 2,
        'SPEED_FIELD': '',
        'DEFAULT_SPEED': 50,  # 假定默认速度为50
        'TOLERANCE': 0,
        'START_POINT': start_point,
        'END_POINT': end_point,
        'OUTPUT': 'memory:'
    }

    # 运行最短路径算法
    result = processing.run("native:shortestpathpointtopoint", params)

    # 获取生成的路径
    path_layer = result['OUTPUT']
    features = list(path_layer.getFeatures())

    if not features:
        print(f"第{i + 1}个点路径计算失败：没有找到有效路径")
        continue

    path_feature = features[0]

    # 将路径添加到输出图层
    provider.addFeature(path_feature)

    # 更新起点为路径的终点
    path_geom = path_feature.geometry()
    if path_geom.isEmpty():
        print(f"第{i + 1}个点路径计算失败：生成的路径几何为空")
        continue

    # 获取路径的所有顶点
    vertices = path_geom.asPolyline()
    if not vertices:
        print(f"第{i + 1}个点路径计算失败：路径几何没有顶点")
        continue

    # 更新起点为路径的终点
    start_point = vertices[-1]

    print(f"第{i + 1}个点路径计算完成")

print("所有路径计算完成")
