import numpy as np
import networkx as nx
import ast
import pandas as pd
import genInput
import sys
from path import root_dir

transfer_time = 5
wait_time_at_O = 5
velocity = 4    # min/km
sp_np = pd.read_csv(f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\revised_region_shortest_path_map.csv').to_numpy()

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
                travel_time_matrix[i][j] = cost_dict[j]*velocity
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

def eval_routes(routes, graph, demand_matrix):
    graph = graph.copy()
    demand_matrix = demand_matrix.copy()
    total_demand = demand_matrix.sum()
    travel_time_matrix, transfer_matrix = evaluate(routes, graph, demand_matrix)
    travel_time_ratio = travel_time_matrix/(sp_np*velocity)
    np.savetxt(f'{root_dir}\\TNDP-Heuristic\\result\\travel_time.csv', travel_time_matrix, delimiter=',', fmt="%.2f")
    np.savetxt(f'{root_dir}\\TNDP-Heuristic\\result\\transfer.csv', transfer_matrix, delimiter=',', fmt="%d")
    np.savetxt(f'{root_dir}\\TNDP-Heuristic\\result\\travel_time_ratio.csv', travel_time_ratio, delimiter=',', fmt="%.2f")
    travel_time_matrix_weighted = travel_time_matrix * demand_matrix
    transfer_matrix_weighted = transfer_matrix * demand_matrix
    travel_time_ratio_weighted = travel_time_ratio * demand_matrix
    # ATT = travel_time_matrix[np.where(travel_time_matrix != -1)].mean()
    # ATrans = transfer_matrix[np.where(transfer_matrix != -1)].mean()
    ATT = travel_time_matrix_weighted[np.where(travel_time_matrix_weighted >= 0)].sum()/total_demand
    ATrans = transfer_matrix_weighted[np.where(transfer_matrix_weighted >= 0)].sum()/total_demand
    ATTR = travel_time_ratio_weighted[np.where(travel_time_ratio_weighted >= 0)].sum()/total_demand
    print('\nAverage Travel Time: %f min' % ATT)
    print('Average Transfer: %f' % ATrans)
    print('Average Travel Time Ratio: %f' % ATTR)

    demand_matrix_all = demand_matrix
    total_demand = demand_matrix_all.sum()

    demand_matrix = demand_matrix_all.copy()
    route_id = 0
    for route in routes:
        assert(len(route) == len(set(route)))
        demand_matrix, satisfied_demand = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 1000)
        # print(('route %d' % route_id), route, satisfied_demand)
        print([i+1 for i in route])
        route_id += 1
    print('Unfulfilled demand: {}%'.format(100*demand_matrix.sum()/total_demand))

    demand_matrix = demand_matrix_all.copy()
    for route in routes:
        demand_matrix, _ = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 0)
    print('Directly unfulfilled demand: {}%'.format(100*demand_matrix.sum()/total_demand))

    demand_matrix = demand_matrix_all.copy()
    for route in routes:
        demand_matrix, _ = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 1)
    print('One-transfer unfulfilled demand: {}%'.format(100*demand_matrix.sum()/total_demand))

    demand_matrix = demand_matrix_all.copy()
    for route in routes:
        demand_matrix, _ = set_demand_satisfied_in_route(route, demand_matrix, transfer_matrix, 2)
    print('Two-transfer unfulfilled demand: {}%'.format(100*demand_matrix.sum()/total_demand))

if __name__ == '__main__':
    graph, demand_matrix = genInput.graph.copy(), genInput.demand_matrix.copy()
    routes = []
    filename = f'{root_dir}\\TNDP-Heuristic\\result\\txt\\routes_0727.txt'
    # filename = f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\routes-Origin-region.txt'
    exclude = ast.literal_eval(str(sys.argv[1]))
    with open(filename, 'r') as f:
        for line in f:
            routes.append(ast.literal_eval(line.strip()))
        # print(routes)
        print(max([len(route) for route in routes]))
    
    for i in exclude:
        del routes[i]
    eval_routes(routes, graph, demand_matrix)
    