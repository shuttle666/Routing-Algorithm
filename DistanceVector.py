import sys

# Neighbor class to store neighbor router and link cost
class Neighbor:
    def __init__(self, neighbor, cost):
        self.neighbor = neighbor
        self.cost = cost

# Graph class to store network topology as adjacency list
class Graph:
    def __init__(self):
        self.net = {}  # Dictionary: {router: [(neighbor, cost), ...]}

    def add_node(self, node):
        """Add a router to the network if not already present."""
        if node not in self.net:
            self.net[node] = []

    def add_edge(self, source, neighbor, weight):
        """Add a bidirectional edge with given weight."""
        if weight != -1:
            self.add_node(source)
            self.add_node(neighbor)
            self.net[source].append(Neighbor(neighbor, weight))
            self.net[neighbor].append(Neighbor(source, weight))

# DistanceTable class to store distance table for a router
class DistanceTable:
    def __init__(self):
        self.table = {}  # {dest: {via: cost}}

    def set_cost(self, dest, via, cost):
        """Set cost to dest via neighbor."""
        if dest not in self.table:
            self.table[dest] = {}
        self.table[dest][via] = cost

    def get_cost(self, dest, via):
        """Get cost to dest via neighbor, return 'INF' if not set."""
        return self.table.get(dest, {}).get(via, 'INF')

def get_router_index(net):
    """Create a sorted router name to index mapping."""
    routers = sorted(net.net.keys())
    return {router: idx for idx, router in enumerate(routers)}

def initialize_tables(net, routers, router_index):
    """Initialize neighbors_cost and min_cost tables."""
    n = len(routers)
    neighbors_cost = [[-1] * n for _ in range(n)]
    min_cost = [[None] * n for _ in range(n)]
    distance_table = [[DistanceTable() for _ in range(n)] for _ in range(n)]

    # Initialize min_cost (cost to self is 0) and neighbors_cost
    for router in routers:
        idx = router_index[router]
        min_cost[idx][idx] = Neighbor(router, 0)
        for neighbor in net.net[router]:
            neighbors_cost[idx][router_index[neighbor.neighbor]] = neighbor.cost

    return neighbors_cost, min_cost, distance_table

def get_min_cost(distance_table, router, dest, router_index, routers):
    """Get minimum cost path from router to dest, choosing lowest via by name."""
    table = distance_table[router_index[router]][router_index[dest]].table.get(dest, {})
    min_cost = float('inf')
    min_via = None
    for via in routers:
        if via != router:
            cost = table.get(via, 'INF')
            if cost != 'INF' and int(cost) < min_cost:
                min_cost = int(cost)
                min_via = via
            elif cost != 'INF' and int(cost) == min_cost and via < min_via:
                min_via = via
    return Neighbor(min_via, min_cost) if min_via else None

def print_distance_table(routers, distance_table, router_index, t):
    """Print distance table for each router at time t."""
    for router in routers:
        print(f"Distance Table of router {router} at t={t}:")
        print("    ", end="")
        for dest in routers:
            if dest != router:
                print(f"{dest:5}", end="")
        print()
        for dest in routers:
            if dest != router:
                print(f"{dest:5}", end="")
                for via in routers:
                    if via != router:
                        cost = distance_table[router_index[router]][router_index[dest]].get_cost(dest, via)
                        print(f"{cost:5}", end="")
                print()
        print()

def distance_vector(net, routers, router_index):
    """Implement Distance Vector algorithm."""
    n = len(routers)
    neighbors_cost, min_cost, distance_table = initialize_tables(net, routers, router_index)
    global t
    t = 0

    while True:
        changed = False
        min_cost_new = [[None] * n for _ in range(n)]
        for i, router in enumerate(routers):
            for j, dest in enumerate(routers):
                if router != dest:
                    for k, via in enumerate(routers):
                        if router != via:
                            nc = neighbors_cost[i][k]
                            mc = min_cost[k][j].cost if min_cost[k][j] else -1
                            cost = 'INF' if nc == -1 or mc == -1 else nc + mc
                            old_cost = distance_table[i][j].get_cost(dest, via)
                            if old_cost != cost:
                                distance_table[i][j].set_cost(dest, via, cost)
                                changed = True
                    min_cost_new[i][j] = get_min_cost(distance_table, router, dest, router_index, routers)
        print_distance_table(routers, distance_table, router_index, t)
        if not changed:
            break
        min_cost = min_cost_new
        t += 1

    return distance_table, min_cost

def main():
    net = Graph()
    # Read router names until DISTANCEVECTOR
    while True:
        line = sys.stdin.readline().strip()
        if line == "DISTANCEVECTOR":
            break
        net.add_node(line)
    
    # Read initial topology until UPDATE
    while True:
        line = sys.stdin.readline().strip()
        if line == "UPDATE":
            break
        source, neighbor, weight = line.split()
        weight = int(weight)
        net.add_edge(source, neighbor, weight)
    
    router_index = get_router_index(net)
    routers = sorted(net.net.keys())
    distance_table, min_cost = distance_vector(net, routers, router_index)

if __name__ == "__main__":
    main()