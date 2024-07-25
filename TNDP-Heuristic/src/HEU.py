import networkx as nx
import numpy as np
import pandas as pd
from geographiclib.geodesic import Geodesic
import genInput
from path import root_dir

# stop_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\unique_stop_downtown.csv')
stop_df = pd.read_csv(f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\TAZ_revised_centroids.csv')
max_demand = np.max(genInput.demand_matrix)
max_dis = max(data['weight'] for u,v,data in genInput.graph.edges(data=True))

def get_highest_demand_pair(demand_matrix):
    return np.unravel_index(np.argmax(demand_matrix), demand_matrix.shape)

def get_highest_demand_destination_from(source, demand_matrix, route, detour_list, graph, weight):
    ind = np.argsort(demand_matrix[source])[::-1]
    for dest in ind:
        if (source, dest) not in detour_list and not_detour(source, dest, route):
            try:
                route_chunk = get_best_route_between(source, dest, graph, demand_matrix, weight)
            except nx.NetworkXNoPath as e:
                return -1, []
            if not_detour(route[-1], route_chunk[1], route):
                return dest, route_chunk
            else:
                detour_list.append((source, dest))
    return -1, []

def not_detour(source, dest, route):
    return 1
    old_route_direction = [Geodesic.WGS84.Inverse(stop_df.loc[route[-(i+1)], '纬度'], stop_df.loc[route[-(i+1)], '经度'],
                                                  stop_df.loc[route[-i], '纬度'], stop_df.loc[route[-i], '经度'])['azi1'] for i in range(1,3) if i < len(route)]
    new_route_direction = Geodesic.WGS84.Inverse(stop_df.loc[source, '纬度'], stop_df.loc[source, '经度'], stop_df.loc[dest, '纬度'], stop_df.loc[dest, '经度'])['azi1']
    angle = abs(np.array(old_route_direction) - new_route_direction)
    return (np.all(angle > 0) and np.all(angle < 100)) or (np.all(angle > 260) and np.all(angle < 360))

def get_highest_demand_destination_from_depot(demand_matrix, depot_list):
    demand_matrix_from_depot = demand_matrix[depot_list]
    ind = np.unravel_index(np.argmax(demand_matrix_from_depot), demand_matrix_from_depot.shape)
    return depot_list[ind[0]], ind[1]

def set_demand_satisfied_in_route(cover_matrix, demand_matrix, route):
    demand_matrix = demand_matrix.copy()
    cover_matrix = cover_matrix.copy()
    for i in route:
        for j in route:
            cover_matrix[i][j] += 1
    demand_matrix = demand_matrix*np.maximum((1 - cover_matrix), 0)
    return demand_matrix, cover_matrix


def disconnect_nodes_in_route_from_graph(graph, route):
    for i in route:
        edges_to_remove = list((i, j) for j in graph[i])
        graph.remove_edges_from(edges_to_remove)


# def importance_of_node_in_between(source, dest, demand_matrix):
#     demand_from_source = demand_matrix[source, :]
#     demand_to_dest = demand_matrix[:, dest]
#     return (demand_from_source + demand_to_dest)/max_demand


# def get_best_route_between(source, dest, graph, demand_matrix, weight):
#     node_importance = importance_of_node_in_between(source, dest, demand_matrix)
#     node_cost = 1 / (1.0 + weight*node_importance)
#     # node_cost = 1 / (1.0 + node_importance)
#     w = weight
#     best_route = nx.algorithms.shortest_paths.weighted.dijkstra_path(graph, source, dest, 
#                                                                      weight=lambda u,v,d: 0.5*(node_cost[u] + node_cost[v])*d['weight']/max_dis)
#                                                                     #  weight=lambda u,v,d: 0.5*w*(node_cost[u] + node_cost[v]) + (1-w)*d['weight']/max_dis)
    
#     return best_route

def importance_of_node_in_between(source, dest, demand_matrix):
    demand_from_source = demand_matrix[source, :]
    demand_to_dest = demand_matrix[:, dest]
    return demand_from_source + demand_to_dest


def node_cost_from_importance(node_importance, weight):
    return weight / (1.0 + node_importance)

def get_best_route_between(source, dest, graph, demand_matrix, weight):
    node_importance = importance_of_node_in_between(source, dest, demand_matrix)
    node_cost = node_cost_from_importance(node_importance, weight)
    best_route = nx.algorithms.shortest_paths.weighted.dijkstra_path(graph, source, dest, weight=lambda u,v,d: node_cost[u] + node_cost[v] + d['weight'])
    return best_route


def get_route_satisfying_constraint(graph, cover_matrix, demand_matrix, weight, min_hop_count, max_hop_count, depot_list, source=None, dest=None, taboo_list=[]):
    graph = graph.copy()
    demand_matrix = demand_matrix.copy()
    cover_matrix = cover_matrix.copy()
    detour_list = []
    if source is None or dest is None:
        source, dest = get_highest_demand_destination_from_depot(demand_matrix, depot_list[~np.isin(depot_list, taboo_list)])
    route = [source]
    route_chunk = get_best_route_between(source, dest, graph, demand_matrix, weight)
    while True:
        route_chunk = route_chunk[1:]
        if len(route) + len(route_chunk) <= max_hop_count:
            route.extend(route_chunk)
        else:
            break
        disconnect_nodes_in_route_from_graph(graph, route[:-1])
        demand_matrix, cover_matrix = set_demand_satisfied_in_route(cover_matrix, demand_matrix, route)
        source = dest
        dest, route_chunk = get_highest_demand_destination_from(dest, demand_matrix, route, detour_list, graph, weight)
        if demand_matrix[source][dest] == 0 or dest == -1:
            break
    # print(route)
    return route


def get_routes(graph, demand_matrix, weight, min_hop_count, max_hop_count, num_of_routes, depot_list):
    demand_matrix = demand_matrix.copy()
    cover_matrix = np.zeros_like(demand_matrix)
    taboo_list = []
    cnt = 0
    while cnt < num_of_routes:
        route = get_route_satisfying_constraint(graph, cover_matrix, demand_matrix, weight, min_hop_count, max_hop_count, depot_list, taboo_list=taboo_list)
        if len(route) == 1:
            taboo_list.append(route[0])
            continue
        demand_matrix, cover_matrix = set_demand_satisfied_in_route(cover_matrix, demand_matrix, route)
        cnt += 1
        yield route
    yield demand_matrix
    yield cover_matrix


def HEU(graph, demand_matrix, weight, min_hop_count, max_hop_count, num_of_routes, depot_list):
    solu = list(get_routes(graph, demand_matrix, weight, min_hop_count, max_hop_count, num_of_routes, depot_list))
    routes, demand_matrix, cover_matrix = solu[:-2], solu[-2], solu[-1]
    return routes, demand_matrix, cover_matrix
