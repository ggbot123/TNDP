import sys
import numpy as np
import genInput
from SBS import SBS
import logging
from datetime import datetime
from create_geojson import create_geojson
import networkx as nx

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(filename=f"E:\\workspace\\python\\TNDP\\TNDP\\TNDP-Heuristic\\log\\log_{current_time}.log", level=logging.INFO)

transfer_time = 5
wait_time_at_O = 5
velocity = 4    # min/km

def generate_transit_graph(routes, graph):
    transit_graph = nx.Graph()
    for i in range(len(routes)):
        route = routes[i]
        route = [str(j) + '_' + str(i) for j in route]
        for j in range(len(route)-1):
            length = graph.get_edge_data(routes[i][j], routes[i][j+1])['weight']
            transit_graph.add_edge(route[j], route[j+1], weight=length)
    nodes = list(transit_graph.nodes())
    for i in range(graph.number_of_nodes()):
        selected_nodes = [node for node in nodes if node.startswith(str(i) + '_')]
        for j in selected_nodes:
            transit_graph.add_edge(i, j, weight=wait_time_at_O/(2*velocity))  # 起始等待时间，主要是便于对多条线路的同名节点去中心化
            for k in selected_nodes:
                if j != k:
                    transit_graph.add_edge(j, k, weight=transfer_time/velocity)
    return transit_graph

def evaluate(routes, graph, demand_matrix):
    transit_graph = generate_transit_graph(routes, graph)
    node_num = graph.number_of_nodes()
    travel_time_matrix = np.zeros_like(demand_matrix)
    transfer_matrix = np.zeros_like(demand_matrix)
    for i in range(node_num):
        transit_graph.add_node(i)
        cost_dict, path_dict = nx.single_source_dijkstra(transit_graph, i, weight='weight')
        for j in range(node_num):
            if j in cost_dict:
                travel_time_matrix[i][j] = cost_dict[j]
                transfer_matrix[i][j] = len(np.unique(np.array([s.split('_')[1] for s in path_dict[j] if '_' in str(s)]))) - 1
            else:
                travel_time_matrix[i][j] = -1
                transfer_matrix[i][j] = -1
    return travel_time_matrix, transfer_matrix

def set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, max_transfer):
    demand_matrix = demand_matrix.copy()
    satisfied_demand = 0.
    for i in route:
        for j in route:
            if transfer_matrix[i][j] >= 0 and transfer_matrix[i][j] <= max_transfer:
                satisfied_demand += demand_matrix[i][j]
                demand_matrix[i][j] = 0.
    return demand_matrix, satisfied_demand

graph, demand_matrix = genInput.graph.copy(), genInput.demand_matrix.copy() 

max_hop_count = int(sys.argv[2])
min_hop_count = int(sys.argv[1])
num_of_routes = int(sys.argv[3])
best_weight = float(sys.argv[4])
depot_list = np.arange(graph.number_of_nodes())

routes = SBS(graph, demand_matrix, min_hop_count, max_hop_count, num_of_routes, best_weight, depot_list).routes

print(len(routes))
travel_time_matrix, transfer_matrix = evaluate(routes, graph, demand_matrix)
np.savetxt('E:\\workspace\\python\\TNDP\\TNDP\\TNDP-Heuristic\\result\\travel_time.csv', travel_time_matrix, delimiter=',', fmt="%.2f")
np.savetxt('E:\\workspace\\python\\TNDP\\TNDP\\TNDP-Heuristic\\result\\transfer.csv', transfer_matrix, delimiter=',', fmt="%d")
ATT = travel_time_matrix[np.where(travel_time_matrix != -1)].mean()
ATrans = transfer_matrix[np.where(transfer_matrix != -1)].mean()
print('Average Travel Time: %f min\n' % ATT)
print('Average Transfer: %f\n' % ATrans)

demand_matrix = genInput.demand_matrix
total_demand = demand_matrix.sum()
for route in routes:
    assert(len(route) == len(set(route)))
    demand_matrix, satisfied_demand = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 1000)
    print(route, satisfied_demand)
print('Unfulfilled demand: {}%'.format(demand_matrix.sum()/total_demand))

demand_matrix = genInput.demand_matrix
for route in routes:
    demand_matrix, _ = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 0)
print('Directly unfulfilled demand: {}%'.format(demand_matrix.sum()/total_demand))

demand_matrix = genInput.demand_matrix
for route in routes:
    demand_matrix, _ = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 1)
print('One-transfer unfulfilled demand: {}%'.format(demand_matrix.sum()/total_demand))

demand_matrix = genInput.demand_matrix
for route in routes:
    demand_matrix, _ = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 2)
print('Two-transfer unfulfilled demand: {}%'.format(demand_matrix.sum()/total_demand))

filename = 'E:\\workspace\\python\\TNDP\\TNDP\\TNDP-Heuristic\\result\\lines-SBS.geojson'
create_geojson(routes, filename)
