import networkx as nx
from pathlib import Path
import numpy as np
import json
import pandas as pd

def read_matrix(path):
    text = path.read_text()
    numbers = list(map(int, text.split()))
    size = numbers[0]
    matrix = np.array(numbers[1:]).reshape(size, size)
    return matrix
def read_csv(path):
    return pd.read_csv(path, index_col=0).values
def save_graph_as_json(distance_matrix, file_path):
    distance_matrix = distance_matrix.copy()
    distance_matrix[distance_matrix == -1] = 0
    graph = nx.convert_matrix.from_numpy_matrix(distance_matrix)
    dest_path = file_path.parent/(file_path.stem + '.json')
    data = nx.readwrite.json_graph.node_link_data(graph)
    with open(dest_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return graph

dist_file = Path('D:\\learning\\workspace\\python\\TNDP\\preProcessing\\data\\manhattan_distance_matrix_downtown.csv')
if dist_file.suffix == '.json':
    with open(dist_file) as f:
        data = json.load(f)
    graph = nx.readwrite.json_graph.node_link_graph(data)
    distance_matrix = nx.convert_matrix.to_numpy_matrix(graph)
elif dist_file.suffix == '.csv':
    distance_matrix = read_csv(dist_file)
    graph = save_graph_as_json(distance_matrix, dist_file)
else:
    distance_matrix = read_matrix(dist_file)
    graph = save_graph_as_json(distance_matrix, dist_file)

node_num = graph.number_of_nodes()
cost_dict = dict(nx.all_pairs_dijkstra_path_length(graph), weight='weight')
shortest_path_matrix = np.array([[cost_dict[i][j] for j in range(node_num)] for i in range(node_num)])
shortest_path = pd.DataFrame(shortest_path_matrix)
shortest_path.to_csv('D:\\learning\\workspace\\python\\TNDP\\preProcessing\\data\\Binzhou_downtown_shortest_path_map.csv', index=False)