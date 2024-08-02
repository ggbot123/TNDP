import numpy as np
import genInput
import ast
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import clear_output
from path import root_dir

def set_demand_satisfied_in_route(cover_matrix, demand_matrix, route):
    demand_matrix = demand_matrix.copy()
    cover_matrix = cover_matrix.copy()
    for i in route:
        for j in route:
            cover_matrix[i][j] += 1
    demand_matrix = demand_matrix*np.maximum((1 - cover_matrix), 0)
    return demand_matrix, cover_matrix

class Individual:
    def __init__(self, routes, demand_matrix, cover_matrix):
        self.routes = routes.copy()
        self.demand_matrix = demand_matrix.copy()
        self.cover_matrix = cover_matrix
    def del_route(self, route, demand_matrix):
        self.routes.remove(route)
        for i in route:
            for j in route:
                self.cover_matrix[i][j] -= 1
        tmp = self.demand_matrix.copy()
        self.demand_matrix = demand_matrix*np.maximum(1 - self.cover_matrix, 0)
        demand_change = self.demand_matrix - tmp
        return np.array(np.where(demand_change != 0)).T, demand_change
    def add_route(self, route, demand_matrix):
        self.routes.append(route)
        for i in route:
            for j in route:
                self.cover_matrix[i][j] += 1
        tmp = self.demand_matrix.copy()
        self.demand_matrix = demand_matrix*np.maximum(1 - self.cover_matrix, 0)
        demand_change = tmp - self.demand_matrix
        return np.array(np.where(demand_change != 0)).T, demand_change.copy()

def get_leaked_OD(i, demand_without, leaked_OD, num_of_return):
    route_imp_rank = np.argsort(demand_without)[::-1]
    print(f'route {i}: {demand_without[i]} OD amount unfulfilled if deleted, importance rank {np.where(route_imp_rank == i)[0][0] + 1}')
    return leaked_OD[i][0:num_of_return:2]

if __name__ == '__main__':
    graph, demand_matrix = genInput.graph.copy(), genInput.demand_matrix.copy()
    total_demand = demand_matrix.sum()
    routes = []
    filename = f'{root_dir}\\TNDP-Heuristic\\result\\txt\\routes_0727.txt'
    with open(filename, 'r') as f:
        for line in f:
            routes.append(ast.literal_eval(line.strip()))
    cover_matrix = np.zeros_like(demand_matrix)
    ind = Individual(routes, demand_matrix, cover_matrix)
    for route in routes:
        ind.demand_matrix, ind.cover_matrix = set_demand_satisfied_in_route(ind.cover_matrix, ind.demand_matrix, route)
    flatten_indices = indices = np.argsort(ind.demand_matrix, axis=None)[::-1]
    flatten_values = ind.demand_matrix.flatten()[flatten_indices]
    indices = np.unravel_index(flatten_indices, ind.demand_matrix.shape)
    unfulfilled_OD = [(indices[0][j], indices[1][j], flatten_values[j]) for j in range(len(flatten_values))]

    demand_without = np.zeros(len(routes))
    leaked_OD = []
    unfulfilled_demand = ind.demand_matrix.copy()
    for i in range(len(routes)):
        route = routes[i]
        changes, demand_change = ind.del_route(route, demand_matrix)
        flatten_indices = indices = np.argsort(demand_change, axis=None)[::-1]
        flatten_values = demand_change.flatten()[flatten_indices]
        indices = np.unravel_index(flatten_indices, demand_change.shape)
        leaked_OD.append([(indices[0][j], indices[1][j], flatten_values[j]) for j in range(len(flatten_values))])
        demand_without[i] = ind.demand_matrix.sum() - unfulfilled_demand.sum()
        ind.add_route(route, demand_matrix)
    

    plt.ion()
    fig, ax = plt.subplots()
    cbar_ax = fig.add_axes([0.91, 0.3, 0.03, 0.4])
    changes = None
    while True:
        ax.clear()
        sns.heatmap(ind.demand_matrix, cmap="viridis", ax=ax, cbar_ax=cbar_ax)
        if changes is not None:
            for (row, col) in changes:
                rect = plt.Rectangle((col, row), 1, 1, linewidth=2, edgecolor='red', facecolor='none')
                ax.add_patch(rect)
            # 设置坐标轴标签
            ax.set_xticks(np.unique(changes[:, 1]))
            ax.set_yticks(np.unique(changes[:, 0]))
            ax.set_xticklabels([f'{i}*' for i in ax.get_xticks()], rotation=45)
            ax.set_yticklabels([f'{i}*' for i in ax.get_yticks()], rotation=0)
        ax.set_title(f'Unfulfilled demand: {ind.demand_matrix.sum()}, {100*ind.demand_matrix.sum()/total_demand}%')
        plt.draw()
        plt.pause(0.001)
        
        user_input = input(">>>")
        if user_input == 'exit':
            break
        else:
            command, *args = user_input.split()
            if command == "add":
                index = int(args[0])
                changes, _ = ind.add_route(routes[index], demand_matrix)
                print(ind.demand_matrix.sum())
            elif command == "del":
                index = int(args[0])
                changes, _ = ind.del_route(routes[index], demand_matrix)
                print(ind.demand_matrix.sum())
            elif command == "check":
                if args[0] == 'all':
                    args[0] = range(0, 49)
                else:
                    args[0] = [int(args[0])]
                for rid in args[0]:
                    OD_pairs = get_leaked_OD(rid, demand_without, leaked_OD, 2*5)
                    with open(f'{root_dir}\\TNDP-Heuristic\\result\\txt\\OD_pairs\\{rid}.txt', 'w') as f:
                        for O, D, demand in OD_pairs[::-1]:
                            # f.write(f'{O+1} {D+1} {demand}\n')
                            f.write(f'{O+1} {D+1}\n')
                            print(f'O: {O+1}, D: {D+1}, leaked demand: {demand}')
                        # f.write(f'{demand_without[rid]}')
                # get_ATT_increase(int(args[1]), graph, demand_matrix)
            elif command == "demand-at":
                O, D = int(args[0]), int(args[1])
                print(f'demand between {O+1} and {D+1}:\noriginal: {demand_matrix[O][D]}\ncurrent: {ind.demand_matrix[O][D]}')
                print(f'most unfulfilled OD:')
            elif command == "demand-un":
                with open(f'{root_dir}\\TNDP-Heuristic\\result\\txt\\OD_pairs\\un.txt', 'w') as f:
                    for O, D, demand in unfulfilled_OD[0:20:2]:
                        f.write(f'{O+1} {D+1}\n')
                        print(f'O: {O+1}, D: {D+1}, unfulfilled demand: {demand}')
            else:
                print("invalid input")
    plt.ioff()
    plt.show()
