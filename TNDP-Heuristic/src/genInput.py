import json
import networkx as nx
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from path import root_dir

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

# dist_file = Path(f'{root_dir}\\TNDP-Heuristic\\data\\Mandl\\MandlDistances.json')
# demand_file = Path(f'{root_dir}\\TNDP-Heuristic\\data\\Mandl\\MandlOriginDestination.txt')
# dist_file = Path(f'{root_dir}\\TNDP-Heuristic\\data\\Mumford\\M3Distances.json')
# demand_file = Path(f'{root_dir}\\TNDP-Heuristic\\data\\Mumford\\M3OriginDestination.txt')
# dist_file = Path(f'{root_dir}\\preProcessing\\data\\manhattan_distance_matrix.csv')
# demand_file = Path(f'{root_dir}\\preProcessing\\data\\Binzhou_route_OD.csv')
dist_file = Path(f'{root_dir}\\preProcessing\\data\\manhattan_distance_matrix_downtown.csv')
demand_file = Path(f'{root_dir}\\preProcessing\\data\\Binzhou_route_OD_downtown.csv')

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

# nx.draw(graph, with_labels=True)
# plt.show()

if demand_file.suffix == '.csv':
    demand_matrix = read_csv(demand_file)
else:
    demand_matrix = read_matrix(demand_file)
total_demand = demand_matrix.sum()

mean = lambda l: sum(l) / len(l)
print('Average demand: {}'.format(demand_matrix[np.nonzero(demand_matrix)].mean()))
print('Total demand: {}'.format(total_demand))
print('Average distance: {}'.format(mean(list(map(lambda d:d[2], graph.edges.data(data='weight'))))))