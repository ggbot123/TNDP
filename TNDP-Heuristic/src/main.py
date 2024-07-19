import sys
import numpy as np
import genInput
from SBS import SBS
import logging
from datetime import datetime
from create_geojson import create_geojson
from eval_routes import eval_routes
from path import root_dir

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(filename=f"{root_dir}\\TNDP-Heuristic\\log\\log_{current_time}.log", level=logging.INFO)

graph, demand_matrix = genInput.graph.copy(), genInput.demand_matrix.copy() 

max_hop_count = int(sys.argv[2])
min_hop_count = int(sys.argv[1])
num_of_routes = int(sys.argv[3])
best_weight = float(sys.argv[4])
depot_list = np.arange(graph.number_of_nodes())

routes = SBS(graph, demand_matrix, min_hop_count, max_hop_count, num_of_routes, best_weight, depot_list).routes
eval_routes(routes, graph, demand_matrix)

filename = f'{root_dir}\\TNDP-Heuristic\\result\\lines-SBS.geojson'
create_geojson(routes, filename)
