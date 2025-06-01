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

    def update_edge(self, source, neighbor, weight):
        """Update or remove a bidirectional edge."""
        if weight == -1:
            # Remove edge if exists
            if source in self.net:
                self.net[source] = [n for n in self.net[source] if n.neighbor != neighbor]
            if neighbor in self.net:
                self.net[neighbor] = [n for n in self.net[neighbor] if n.neighbor != source]
        else:
            # Remove existing edge and add new one
            self.update_edge(source, neighbor, -1)
            self.add_edge(source, neighbor, weight)

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

def print_routing_table(routers, min_cost, router_index):
    """Print routing table for each router after convergence."""
    for router in routers:
        print(f"Routing Table of router {router}:")
        for dest in routers:
            if dest != router:
                via_obj = min_cost[router_index[router]][router_index[dest]]
                via = via_obj.neighbor if via_obj else "INF"
                cost = via_obj.cost if via_obj else "INF"
                print(f"{dest},{via},{cost}")
        print()

def merge_tables(old_min_cost, old_distance_table, old_router_index, new_routers, new_router_index):
    """Merge old tables into new tables for updated topology."""
    n = len(new_routers)
    new_min_cost = [[None] * n for _ in range(n)]
    new_distance_table = [[DistanceTable() for _ in range(n)] for _ in range(n)]
    for router in new_routers:
        i = new_router_index[router]
        new_min_cost[i][i] = Neighbor(router, 0)
        if router in old_router_index:
            old_i = old_router_index[router]
            for dest in new_routers:
                if dest in old_router_index:
                    old_j = old_router_index[dest]
                    new_min_cost[i][new_router_index[dest]] = old_min_cost[old_i][old_j]
                    new_distance_table[i][new_router_index[dest]] = old_distance_table[old_i][old_j]
    return new_min_cost, new_distance_table

def distance_vector(net, routers, router_index, old_min_cost=None, old_distance_table=None, old_router_index=None):
    """Implement Distance Vector algorithm."""
    n = len(routers)
    neighbors_cost, min_cost, distance_table = initialize_tables(net, routers, router_index)
    if old_min_cost and old_distance_table and old_router_index:
        min_cost, distance_table = merge_tables(old_min_cost, old_distance_table, old_router_index, routers, router_index)
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

    print_routing_table(routers, min_cost, router_index)
    return distance_table, min_cost

def main():
    net = Graph()
    # Read router names until DISTANCEVECTOR
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            return
        if line == "DISTANCEVECTOR":
            break
        if not line.isalpha():
            print("Error: Invalid router name")
            return
        net.add_node(line)
    
    # Read initial topology until UPDATE
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            return
        if line == "UPDATE":
            break
        try:
            source, neighbor, weight = line.split()
            weight = int(weight)
            net.add_edge(source, neighbor, weight)
        except (ValueError, TypeError):
            print("Error: Invalid topology input")
            return
    
    router_index = get_router_index(net)
    routers = sorted(net.net.keys())
    distance_table, min_cost = distance_vector(net, routers, router_index)
    
    # Read updates until END
    updates = []
    while True:
        line = sys.stdin.readline().strip()
        if not line or line == "END":
            break
        try:
            source, neighbor, weight = line.split()
            weight = int(weight)
            updates.append((source, neighbor, weight))
        except (ValueError, TypeError):
            print("Error: Invalid update input")
            return
    
    if updates:
        for source, neighbor, weight in updates:
            net.update_edge(source, neighbor, weight)
        new_router_index = get_router_index(net)
        new_routers = sorted(net.net.keys())
        distance_vector(net, new_routers, new_router_index, min_cost, distance_table, router_index)

if __name__ == "__main__":
    main()