# Neighbor class to store neighbor router and link cost
class Neighbor:
    def __init__(self, neighbor, cost):
        self.neighbor = neighbor
        self.cost = cost

def main():
    # Temporary test for Neighbor class
    neighbor = Neighbor("Y", 3)
    print(f"Neighbor: {neighbor.neighbor}, Cost: {neighbor.cost}")

if __name__ == "__main__":
    main()