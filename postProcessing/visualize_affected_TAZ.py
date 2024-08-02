import os
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsExpression,
    QgsFillSymbol,
    QgsRuleBasedRenderer
)
from PyQt5.QtGui import QColor

# 读取文件中的编号对
def read_id_pairs_from_file(file_path):
    id_pairs = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 2:
                id_pairs.append((int(parts[0]), int(parts[1])))
    return id_pairs

# 高亮显示指定编号对的多边形
def highlight_polygon_pairs(layer_name, id_pairs):
    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    # 创建新的符号和渲染器
    default_symbol = QgsFillSymbol.createSimple({
        'color': 'transparent',        # 填充颜色透明
        'outline_color': 'transparent', # 边框颜色透明
        'outline_width': '0'           # 边框宽度为0
    })
    root_rule = QgsRuleBasedRenderer.Rule(default_symbol)
    renderer = QgsRuleBasedRenderer(root_rule)

    # 为每对编号创建新的规则
    for i, (id1, id2) in enumerate(id_pairs):
        expression = '\"分组\" IN ({}, {})'.format(id1, id2)
        
        # 创建新符号并设置样式
        symbol = QgsFillSymbol.createSimple({'color': 'yellow', 'outline_color':'transparent', 'outline_width':'0'})
        color = QColor.fromHsv((i * 60) % 360, 255, 255)  # 生成不同的颜色，最大支持6种颜色
        symbol.setColor(color)
        #symbol.symbolLayer(0).setStrokeColor(QColor('black'))
        #symbol.symbolLayer(0).setStrokeWidth(1.5)

        # 创建规则并设置过滤表达式
        rule = QgsRuleBasedRenderer.Rule(symbol)
        rule.setFilterExpression(expression)
        root_rule.appendChild(rule)

    # 设置新的渲染器
    layer.setRenderer(renderer)

    # 刷新图层以应用更改
    layer.triggerRepaint()

# 文件路径和图层名称
file_path = 'D:\\learning\\workspace\\python\\TNDP\\TNDP-Heuristic\\result\\txt\\OD_pairs\\25.txt'  # 替换为实际文件路径
layer_name = 'TAZ_revised'  # 替换为你的图层名称

# 读取文件中的编号对
polygon_id_pairs_to_highlight = read_id_pairs_from_file(file_path)
print(polygon_id_pairs_to_highlight)

# 高亮显示这些编号对对应的多边形
highlight_polygon_pairs(layer_name, polygon_id_pairs_to_highlight)