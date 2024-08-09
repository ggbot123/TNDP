from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsMarkerSymbol,
    QgsTextFormat,
    QgsTextBufferSettings,
    QgsVectorLayer,
    QgsField,
    QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes
)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

reverse = 1
# 获取活动图层
layer = iface.activeLayer()

# 假设你有一个 CSV 文件或其他表格文件，路径为 csv_file_path
csv_file_path = r'D:\learning\workspace\python\TNDP\postProcessing\result\properties.csv'

# 读取 CSV 文件
csv_layer = QgsProject.instance().mapLayersByName('properties')[0]
if not csv_layer.isValid():
    print("CSV layer failed to load!")
else:
    print("CSV layer loaded successfully!")

# 检查图层的字段
fields = csv_layer.fields()
print("Fields:", fields.names())
csv_provider = csv_layer.dataProvider()

# 从 CSV 表中读取数据
layer_name = layer.name()  # 获取当前图层的名称
# 使用正则表达式提取数字部分
match = re.search(r'\d+', layer_name)
if match:
    numbers = match.group()  # 提取第一个匹配的数字部分
    print(f"Extracted numbers: {numbers}")
else:
    print("No numbers found in the layer name.")
labels_start = {}
labels_end = {}
route_id = numbers
for feature in csv_layer.getFeatures():
    feature_layer_name = feature['线路编号']  # 假设 CSV 表格中有一个 'layer_name' 字段
    start = feature['首站']  # 假设 CSV 表格中有一个 'label' 字段
    end = feature['末站']
    if str(feature_layer_name) == route_id:
        labels_start[route_id] = start  # 使用 feature.id() 作为键，label_text 作为值
        labels_end[route_id] = end

# 创建一个临时图层用于端点标注
temp_layer = QgsVectorLayer('Point?crs=EPSG:4326', f'Endpoints{route_id}', 'memory')
temp_provider = temp_layer.dataProvider()
temp_provider.addAttributes([QgsField("label", QVariant.String)])
temp_layer.updateFields()

# 创建一个空的几何对象用于存储合并后的线
combined_geometry = QgsGeometry()

# 遍历线要素，将它们合并为一个几何对象
for feature in layer.getFeatures():
    geometry = feature.geometry()
    if geometry and geometry.type() == QgsWkbTypes.LineGeometry:
        if not geometry.isEmpty() and geometry.asPolyline():
            #print(f"Adding geometry: {geometry.asWkt()}")
            combined_geometry = QgsGeometry.unaryUnion([combined_geometry, geometry])
        else:
            print(f"Empty or invalid geometry: {geometry.asWkt()}")

# 打印合并后的几何体
#print(f"Combined geometry: {combined_geometry.asWkt()}")

# 确保合并后的几何体是线类型并提取其端点
if combined_geometry.type() == QgsWkbTypes.LineGeometry:
    if combined_geometry.isMultipart():
        lines = combined_geometry.asMultiPolyline()
    else:
        lines = [combined_geometry.asPolyline()]

    if lines and lines[0]:
        start_point = lines[0][0]  # 第一个线段的起点
        end_point = lines[-1][-1]  # 最后一个线段的终点

        # 添加起点
        start_feat = QgsFeature(temp_layer.fields())
        start_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(start_point)))
        print(labels_start[route_id])
        if reverse == 1:
            start_feat.setAttribute("label", labels_start.get(route_id, "End"))
        else:
            start_feat.setAttribute("label", labels_end.get(route_id, "End"))
        temp_provider.addFeatures([start_feat])

        # 添加终点
        end_feat = QgsFeature(temp_layer.fields())
        end_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(end_point)))
        print(labels_end[route_id])
        if reverse == 1:
            end_feat.setAttribute("label", labels_end.get(route_id, "End"))
        else:
            end_feat.setAttribute("label", labels_start.get(route_id, "End"))
        temp_provider.addFeatures([end_feat])

# 添加临时图层到项目中
QgsProject.instance().addMapLayer(temp_layer)

# 为临时图层设置样式
symbol = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': 'red', 'size': '6'})
temp_layer.renderer().setSymbol(symbol)

# 设置标注样式
label_layer_settings = QgsPalLayerSettings()
label_layer_settings.fieldName = 'label'
label_layer_settings.placement = QgsPalLayerSettings.Placement.OrderedPositionsAroundPoint  # 选择标注位置

# 省略placement设置，改为使用默认标注设置
label_format = QgsTextFormat()
label_format.setSize(15)
font = QFont('Arial', 15)  # 创建 QFont 对象，设置字体类型和大小
font.setBold(True)  # 设置字体加粗
label_format.setFont(font)  # 设置字体
label_format.setColor(QColor('blue'))

buffer_settings = QgsTextBufferSettings()
buffer_settings.setEnabled(False)
label_format.setBuffer(buffer_settings)
label_layer_settings.setFormat(label_format)

labeling = QgsVectorLayerSimpleLabeling(label_layer_settings)
temp_layer.setLabelsEnabled(True)
temp_layer.setLabeling(labeling)

iface.mapCanvas().refresh()
