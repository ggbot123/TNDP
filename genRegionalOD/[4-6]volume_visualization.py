# -*- coding:<UTF-8> -*-

# v0.01 by chalco & ChatGPT
# Created 202407221619

import csv
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsLineString,
    QgsField,
    QgsSymbol,
    QgsRendererRange,
    QgsGraduatedSymbolRenderer,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface
from PyQt5.QtGui import QColor


if __name__ == '__main__':
    od_matrix_path = 'D:\\Downloads\\final_OD[downtown].csv'
    od_data = {}

    with open(od_matrix_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)[1:]  # 获取分组名称
        for row in reader:
            od_data[row[0]] = {headers[i]: float(row[i + 1]) for i in range(len(headers))}

    layer = iface.activeLayer()

    output_layer = QgsVectorLayer('LineString?crs=EPSG:4326', 'Traffic Flow', 'memory')
    output_layer_provider = output_layer.dataProvider()

    # 添加必要的字段
    output_layer_provider.addAttributes([
        QgsField('from_group', QVariant.String),
        QgsField('to_group', QVariant.String),
        QgsField('volume', QVariant.Double)
    ])
    output_layer.updateFields()

    centroids = {}
    for feat in layer.getFeatures():
        geom = feat.geometry()
        centroid = geom.centroid().asPoint()
        group = feat['分组']
        centroids[group] = centroid

    features = []
    for from_group, destinations in od_data.items():
        if from_group not in centroids:
            continue
        from_centroid = centroids[from_group]
        for to_group, volume in destinations.items():
            if to_group not in centroids or volume == 0:
                continue
            to_centroid = centroids[to_group]
            line_geom = QgsGeometry.fromPolylineXY([from_centroid, to_centroid])
            feat = QgsFeature()
            feat.setGeometry(line_geom)
            feat.setAttributes([from_group, to_group, volume])
            features.append(feat)

    output_layer_provider.addFeatures(features)
    output_layer.updateExtents()
    QgsProject.instance().addMapLayer(output_layer)

    ranges = []
    for volume in range(0, 1000, 200):  # 修改范围以适应你的数据
        symbol = QgsSymbol.defaultSymbol(output_layer.geometryType())
        symbol.setWidth(volume / 100.0)  # 调整箭头的宽度
        symbol.setColor(QColor(255, 0, 0, min(255, int(volume / 4))))  # 调整颜色
        renderer_range = QgsRendererRange(volume, volume + 200, symbol, '{} - {}'.format(volume, volume + 200))
        ranges.append(renderer_range)

    renderer = QgsGraduatedSymbolRenderer('volume', ranges)
    output_layer.setRenderer(renderer)

    print("流量线已创建并添加到地图中。")
