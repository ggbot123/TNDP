# -*- coding:<UTF-8> -*-

# v0.01 by chalco & ChatGPT
# Created 202407221538

import csv
from qgis.core import QgsProject, QgsGeometry


if __name__ == '__main__':
    # 获取当前活动图层
    layer = iface.activeLayer()

    # 获取图层中的所有多边形
    features = list(layer.getFeatures())

    # 创建邻接矩阵
    adjacency_matrix = []
    group_field_name = '分组'

    for feat1 in features:
        row = []
        geom1 = feat1.geometry()
        for feat2 in features:
            geom2 = feat2.geometry()
            # 检查两个多边形是否相邻
            if geom1.touches(geom2):
                row.append(1)
            else:
                row.append(0)
        adjacency_matrix.append(row)

    output_csv_path = 'D:\\Downloads\\adjacency_matrix.csv'
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([feat[group_field_name] for feat in features])
        for row in adjacency_matrix:
            writer.writerow(row)
