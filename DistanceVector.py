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

def main():
    net = Graph()
    # Read router names until DISTANCEVECTOR
    while True:
        line = sys.stdin.readline().strip()
        if line == "DISTANCEVECTOR":
            break
        net.add_node(line)
    
    # Print network for verification
    for node, neighbors in net.net.items():
        print(f"{node}: {[ (n.neighbor, n.cost) for n in neighbors ]}")

if __name__ == "__main__":
    main()