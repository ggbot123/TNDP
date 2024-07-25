import numpy as np
import networkx as nx
from HEU import HEU, get_route_satisfying_constraint, set_demand_satisfied_in_route
from operator import attrgetter
import random
import logging
import copy
import time
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import ast
from path import root_dir

MAX_ITER = 200
# sp_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\Binzhou_downtown_shortest_path_map.csv')
sp_df = pd.read_csv(f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\revised_region_shortest_path_map.csv')
# sp_df = pd.read_csv(f'{root_dir}\\TNDP-Heuristic\\data\\Mandl\\shortest_path_map.csv')
BEST_WEIGHT = 0.5
transfer_time = 15
wait_time_at_O = 5
velocity = 4    # min/km

class Individual:
    def __init__(self, routes, demand_matrix, cover_matrix):
        self.routes = routes
        self.demand_matrix = demand_matrix
        self.cover_matrix = cover_matrix
    def cal_fitness(self, graph, demand_matrix):
        transit_graph = generate_transit_graph(self.routes, graph)
        node_num = graph.number_of_nodes()
        cost_matrix = np.zeros_like(demand_matrix)
        # start_0 = time.perf_counter()
        for i in range(node_num):
            transit_graph.add_node(i)
            # start_0 = time.perf_counter()
            cost_dict = nx.single_source_dijkstra_path_length(transit_graph, i, weight='weight')
            # start_1 = time.perf_counter()
            # print('[CAL_TIME] Running time for single-source-dijkstra: %s s\n' %(start_1 - start_0))
            # start_0 = time.perf_counter()
            for j in range(node_num):
                if j in cost_dict:
                    cost_matrix[i][j] = cost_dict[j] * demand_matrix[i][j]
                else:
                    cost_matrix[i][j] = demand_matrix[i][j] * (50 + optimal_travel_time_between(graph, i, j))
            # start_1 = time.perf_counter()
            # print('[CAL_TIME] Running time for calculate optimal travel time: %s s\n' %(start_1 - start_0))
        # start_1 = time.perf_counter()
        # print('[CAL_TIME] Running time for cal_fitness: %s s\n' %(start_1 - start_0))
        self.detour_coeff = np.zeros(len(self.routes))
        # for i in range(len(self.routes)):
        #     route = self.routes[i]
        #     route_len_straight = nx.dijkstra_path_length(graph, route[0], route[-1], weight='weight')
        #     route_len = sum([graph[route[j]][route[j+1]]['weight'] for j in range(len(route)-1)])
        #     self.detour_coeff[i] = route_len/route_len_straight
        # self.fitness = - (cost_matrix.sum() + sum([(coeff-1)*1000 if coeff < 2 else 1000000000 for coeff in self.detour_coeff]))
        self.fitness = - cost_matrix.sum()
        return self
    def del_route(self, route, demand_matrix):
        self.routes.remove(route)
        for i in route:
            for j in route:
                self.cover_matrix[i][j] -= 1
        self.demand_matrix = demand_matrix*np.maximum(1 - self.cover_matrix, 0)
    def add_route(self, route, demand_matrix):
        self.routes.append(route)
        for i in route:
            for j in route:
                self.cover_matrix[i][j] += 1
        self.demand_matrix = demand_matrix*np.maximum(1 - self.cover_matrix, 0)
    def __str__(self):
        route_str = '\n    '.join(str(route) for route in self.routes)
        return "routes: %s\nfitness: %s\nmean detour coeff: %s\n" % (route_str, str(self.fitness), str(self.detour_coeff.mean()))

def optimal_travel_time_between(graph, source, dest):
    # return nx.dijkstra_path_length(graph, source, dest, weight='weight')
    return sp_df.loc[source, str(dest)]

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
        
def generate_weight():
    return max(np.random.normal(loc=1, scale=0.5) * BEST_WEIGHT, 0)
    # return np.random.rand()

def get_initial_solution(pop_size, graph, demand_matrix, min_hop_count, max_hop_count, num_of_routes, depot_list, specified_routes_list):
    for routes in specified_routes_list:
        demand_matrix_rest = demand_matrix.copy()
        cover_matrix_rest = np.zeros_like(demand_matrix)
        for route in routes:
            demand_matrix_rest, cover_matrix_rest = set_demand_satisfied_in_route(cover_matrix_rest, demand_matrix_rest, route)
        yield Individual(routes, demand_matrix_rest, cover_matrix_rest).cal_fitness(graph, demand_matrix)
    for _ in range(pop_size - len(specified_routes_list)):
        weight = generate_weight()
        routes, demand_matrix_rest, cover_matrix_rest = HEU(graph, demand_matrix, weight, min_hop_count, max_hop_count, num_of_routes, depot_list)
        yield Individual(routes, demand_matrix_rest, cover_matrix_rest).cal_fitness(graph, demand_matrix)

def add_node(graph, route, side):
    candidate_nodes = [node for node in graph[side] if node not in route]
    if candidate_nodes:
        new_node = random.choice(candidate_nodes)
        if side == route[-1]:
            route.append(new_node)
        else:
            route.insert(0, new_node)
    return route

def del_node(route, side):
    route.remove(side)
    return route

def get_trivial_successor(ind, graph, demand_matrix, min_hop_count, max_hop_count, p_del):
    route = random.choice(ind.routes)
    count = np.random.randint(0, len(route)/2 + 1) # 目前：包括1/2路线长度的下界
    # side = random.choice([0, -1])
    side = -1
    rand = np.random.rand()
    ind.del_route(route, demand_matrix)
    for _ in range(count):
        if rand < p_del:
            if len(route) <= min_hop_count:
                route = add_node(graph, route, route[side])
            else:
                route = del_node(route, route[side])
        else:
            if len(route) >= max_hop_count:
                route = del_node(route, route[side])
            else:
                route = add_node(graph, route, route[side])
    ind.add_route(route, demand_matrix)
    ind.cal_fitness(graph, demand_matrix)
    return ind

def get_heuristic_successor(ind, graph, demand_matrix, min_hop_count, max_hop_count):
    route = random.choice(ind.routes)
    source, dest = route[0], route[-1]
    ind.del_route(route, demand_matrix)
    weight = generate_weight()
    new_route = get_route_satisfying_constraint(graph, ind.cover_matrix, ind.demand_matrix, weight, min_hop_count, max_hop_count, depot_list=None, source=source, dest=dest)
    ind.add_route(new_route, demand_matrix)
    ind.cal_fitness(graph, demand_matrix)
    return ind

def tournament_select(successors, pop_size, tourn_size):
    selected = []
    for _ in range(pop_size):
        group = random.choices(successors, k=tourn_size)
        group_best_ind = max(group, key=attrgetter('fitness'))
        selected.append(group_best_ind)
    return selected

def SBS(graph, demand_matrix, min_hop_count, max_hop_count, num_of_routes, depot_list, ini_routes_path):
    pop_size = 10
    neib_size = 20
    tourn_size = 180
    p_del = 0.4
    p_heu = 0.9
    best_fitness = []
    
    # start_0 = time.perf_counter()
    logging.info("[INIT-POP] Initialize population...\n")
    specified_routes_list = []
    for filename in ini_routes_path:
        specified_routes = []
        with open(filename, 'r') as f:
            for line in f:
                specified_routes.append(ast.literal_eval(line.strip()))
        specified_routes_list.append(specified_routes)
    population = list(get_initial_solution(pop_size, graph, demand_matrix, min_hop_count, max_hop_count, num_of_routes, depot_list, specified_routes_list))
    for i in range(len(population)):
        logging.info("[INIT-POP] Ind %d:\n%s\n" % (i, population[i]))
    # start_1 = time.perf_counter()
    # print('[get_initial_solution] Running time: %s s\n' %(start_1 - start_0))
    best_ind = max(population, key=attrgetter('fitness'))
    logging.info("[INIT-POP] Best Ind in Iter 0:\n%s\n" % best_ind)
    best_fitness.append(best_ind.fitness)
    
    for iter_cnt in tqdm(range(MAX_ITER)):
        logging.info("[Iter %d] Start evolutioning...\n" % iter_cnt)
        successors = []
        # start_0 = time.perf_counter()
        ind_cnt = 0
        for ind in population:
            logging.info("[GEN-SUCC] Generating Successors for Ind %d in Iter %d...\n" % (ind_cnt, iter_cnt))
            for _ in range(neib_size):
                rand = np.random.rand()
                if rand < p_heu:
                    successor = get_heuristic_successor(copy.deepcopy(ind), graph, demand_matrix, min_hop_count, max_hop_count)
                else:
                    successor = get_trivial_successor(copy.deepcopy(ind), graph, demand_matrix, min_hop_count, max_hop_count, p_del)
                successors.append(successor)
            # for i in range(len(successors)):
            #     logging.info("[GEN-SUCC] Successor %d of Ind %d in Iter %d:\n%s\n" % (i, ind_cnt, iter_cnt, successors[i]))
            ind_cnt += 1
        # start_1 = time.perf_counter()
        # print('[get_successor] Running time: %s s\n' %(start_1 - start_0))

        # start_0 = time.perf_counter()
        logging.info("[GEN-CAND] Generating Best Candidates in Iter %d...\n" % (iter_cnt))
        population = tournament_select(successors, pop_size, tourn_size)
        for i in range(len(population)):
            logging.info("[GEN-CAND] Ind %d:\n%s\n" % (i, population[i]))
        # start_1 = time.perf_counter()
        # print('[tournament_select] Running time: %s s\n' %(start_1 - start_0))

        candidate_best_ind = max(population, key=attrgetter('fitness'))
        logging.info("[SELECT-CAND] Candidate Best Ind in Iter %d:\n%s\n" %(iter_cnt, candidate_best_ind))
        best_ind = max([candidate_best_ind, best_ind], key=attrgetter('fitness'))
        logging.info("[SELECT-BEST] Best Ind in Iter %d:\n%s\n" %(iter_cnt, best_ind))
        best_fitness.append(best_ind.fitness)
    plt.plot(np.arange(MAX_ITER+1), best_fitness)
    plt.xlabel('iter')
    plt.ylabel('fitness')
    plt.title('fitness variation')
    plt.grid(True)
    plt.savefig(f'{root_dir}\\TNDP-Heuristic\\result\\fitness_variation.png')
    return best_ind
