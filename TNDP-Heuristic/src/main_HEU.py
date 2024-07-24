import sys
import numpy as np
import genInput
import HEU
# import HEU_more_detour
from create_geojson import create_geojson
from eval_routes import eval_routes
import ast
from path import root_dir

min_hop_count = int(sys.argv[1])
max_hop_count = int(sys.argv[2])
num_of_routes = int(sys.argv[3])
best_weight = [float(sys.argv[4])]
start_from_depot = sys.argv[5]
# best_weight = [0.5, 1, 2, 6]

graph, demand_matrix = genInput.graph.copy(), genInput.demand_matrix.copy()

if start_from_depot == 'True':
    with open(f'{root_dir}\\TNDP-Heuristic\\data\\Binzhou_TAZs\\stop_near_depot.txt', 'r') as f:
    # with open(f'{root_dir}\\TNDP-Heuristic\\data\\Mandl\\stop_near_depot.txt', 'r') as f:
        depot_list = np.array(ast.literal_eval(f.readline().strip()))
else:
    depot_list = np.arange(graph.number_of_nodes())


for weight in best_weight:
    # routes, _ = HEU_more_detour.HEU(graph, demand_matrix, weight, min_hop_count, max_hop_count, num_of_routes, depot_list)
    routes, _, _ = HEU.HEU(graph, demand_matrix, weight, min_hop_count, max_hop_count, num_of_routes, depot_list)
    eval_routes(routes, graph, demand_matrix)
    
    # filename = f'{root_dir}\\TNDP-Heuristic\\result\\routes-HEU-more-detour_w={str(weight)}.geojson'
    # filename = f'{root_dir}\\TNDP-Heuristic\\result\\routes-HEU_w={str(weight)}.geojson'
    filename = f'{root_dir}\\TNDP-Heuristic\\result\\routes-from-depots-HEU_w={str(weight)}.geojson'
    # filename = f'{root_dir}\\TNDP-Heuristic\\result\\routes-from-depots-more-detour-HEU_w={str(weight)}.geojson'
    create_geojson(routes, filename)