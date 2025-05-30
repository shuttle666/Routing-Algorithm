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
    neighbors_cost, min_cost, distance_table = initialize_tables(net, routers, router_index)
    
    # Print for verification
    print("Neighbors Cost:", neighbors_cost)

if __name__ == "__main__":
    main()