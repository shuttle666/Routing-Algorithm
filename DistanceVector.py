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
            # Remove empty nodes
            if source in self.net and not self.net[source]:
                del self.net[source]
            if neighbor in self.net and not self.net[neighbor]:
                del self.net[neighbor]
        else:
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
        """Get cost to dest via neighbor, return float('inf') if not set."""
        return self.table.get(dest, {}).get(via, float('inf'))

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
            cost = table.get(via, float('inf'))
            if cost < min_cost:
                min_cost = cost
                min_via = via
            elif cost == min_cost and cost != float('inf') and min_via is not None and via < min_via:
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
                        print(f"{cost if cost != float('inf') else 'INF':5}", end="")
                print()
        print()

def print_routing_table(routers, min_cost, router_index, neighbors_cost):
    """Print routing table for each router after convergence."""
    for router in routers:
        print(f"Routing Table of router {router}:")
        i = router_index[router]
        for dest in routers:
            if dest != router:
                j = router_index[dest]
                via_obj = min_cost[i][j]
                if via_obj and via_obj.cost != float('inf'):
                    via = via_obj.neighbor
                    cost = via_obj.cost
                    # Verify via is a direct neighbor
                    if neighbors_cost[i][router_index[via]] != -1:
                        print(f"{dest},{via},{cost}")
                    else:
                        print(f"{dest},INF,INF")
                else:
                    print(f"{dest},INF,INF")
        print()

def distance_vector(net, routers, router_index):
    """Implement Distance Vector algorithm with proper convergence."""
    n = len(routers)
    neighbors_cost, min_cost, distance_table = initialize_tables(net, routers, router_index)
    
    t = 0
    max_iterations = 1000  # 防止无限循环
    
    while t < max_iterations:
        changed = False
        min_cost_changed = False
        
        # 创建新的min_cost表来检测变化
        min_cost_new = [[None] * n for _ in range(n)]
        
        # 初始化对角线（到自己的距离为0）
        for i, router in enumerate(routers):
            min_cost_new[i][i] = Neighbor(router, 0)
        
        for i, router in enumerate(routers):
            for j, dest in enumerate(routers):
                if router != dest:
                    for k, via in enumerate(routers):
                        if router != via:
                            nc = neighbors_cost[i][k]
                            if nc != -1:  # 只有当存在直接连接时才计算
                                mc = min_cost[k][j].cost if min_cost[k][j] and min_cost[k][j].cost != float('inf') else float('inf')
                                cost = nc + mc if mc != float('inf') else float('inf')
                            else:
                                cost = float('inf')
                            
                            old_cost = distance_table[i][j].get_cost(dest, via)
                            if old_cost != cost:
                                distance_table[i][j].set_cost(dest, via, cost)
                                changed = True
                    
                    # 计算新的最小成本路径
                    new_min = get_min_cost(distance_table, router, dest, router_index, routers)
                    min_cost_new[i][j] = new_min
                    
                    # 检查最小成本是否发生变化
                    old_min = min_cost[i][j]
                    if ((old_min is None and new_min is not None) or 
                        (old_min is not None and new_min is None) or
                        (old_min is not None and new_min is not None and 
                         (old_min.cost != new_min.cost or old_min.neighbor != new_min.neighbor))):
                        min_cost_changed = True
        
        print_distance_table(routers, distance_table, router_index, t)
        
        # 只有当最小成本路径不再变化时才收敛
        if not min_cost_changed:
            break
            
        min_cost = min_cost_new
        t += 1

    if t >= max_iterations:
        print(f"Warning: Algorithm did not converge after {max_iterations} iterations")
    
    print_routing_table(routers, min_cost, router_index, neighbors_cost)
    return distance_table, min_cost

def main():
    net = Graph()
    # Read router names until START
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            return
        if line == "START":
            break
        if any(c.isdigit() for c in line) or ' ' in line:
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
    if routers:  # Run DV only if there are routers
        distance_table, min_cost = distance_vector(net, routers, router_index)
    else:
        return
    
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
        if new_routers:  # 重新运行完整的DV算法，不保留旧状态
            distance_vector(net, new_routers, new_router_index)

if __name__ == "__main__":
    main()