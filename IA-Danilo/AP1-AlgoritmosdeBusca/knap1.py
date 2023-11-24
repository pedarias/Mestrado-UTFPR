"""
Given a set of items, each with a weight and a value,
and you must select a subset of the items to maximize the total value 
while keeping the total weight within a given capacity.
"""
import random


class KnapsackSolver:
    def __init__(self, weights, values, capacity):  # args we want to accept
        self.weights = weights
        self.values = values
        self.capacity = capacity
        self.n = len(weights)

        # Initialize state with a given binary representation
        self.state = [1, 0, 1, 1, 1, 0, 1, 1]  # Provided initial state

    def get_cost(self, state):
        # Calculate the total value of the selected items
        total_value = sum(state[i] * self.values[i] for i in range(self.n))
        # If the total weight exceeds the capacity, return a negative cost
        total_weight = sum(state[i] * self.weights[i] for i in range(self.n))
        if total_weight > self.capacity:
            return -total_value
        return total_value

    def get_neighbors(self, state):
        # Generate neighboring states by flipping the value (0 to 1 or 1 to 0) of a randomly selected item
        neighbors = []
        for i in range(self.n):
            neighbor = state.copy()
            neighbor[i] = 1 - neighbor[i]  # Flip the value
            neighbors.append(neighbor)
        return neighbors

    def hill_climb(self, maximum=None, log=False):
        count = 0

        while maximum is None or count < maximum:
            count += 1
            best_neighbors = []
            best_neighbor_cost = None

            for neighbor in self.get_neighbors(self.state):
                cost = self.get_cost(neighbor)
                if best_neighbor_cost is None or cost > best_neighbor_cost:
                    best_neighbor_cost = cost
                    best_neighbors = [neighbor]
                elif best_neighbor_cost == cost:
                    best_neighbors.append(neighbor)

            if best_neighbor_cost <= self.get_cost(self.state):
                # If no better neighbor is found, terminate
                return self.state

            # Move to a highest-valued neighbor
            self.state = random.choice(best_neighbors)

            if log:
                print(f"Iteration {count}: Cost {best_neighbor_cost}")

        return self.state


# Example usage with provided parameters
weights = [25, 35, 45, 5, 25, 3, 2, 2]
values = [350, 400, 50, 20, 70, 8, 5, 5]
max_weight = 104
initial_state = [1, 0, 1, 1, 1, 0, 1, 1]

solver = KnapsackSolver(weights, values, max_weight)
best_solution = solver.hill_climb(log=True)

print("Best Solution:", best_solution)
print("Best Value:", solver.get_cost(best_solution))
