import random


class Space:
    def _init_(self, height, width, maxh):
        self.height = height
        self.width = width
        self.maxh = maxh
        self.objs1 = set()
        self.objs2 = set()

    def add_obj1(self, row, col):
        """Add obj1 at a particular location in state space"""
        self.objs1.add((row, col))

    def available_spaces(self):
        """
        Returns all cells not currently used by obj1 or obj2"""

        # Consiser all posssible cells
        candidates = set(
            (row, col) for row in range(self.height) for col in range(self.width)
        )

        # Remove all obj1 and obj2
        for obj1 in self.objs1:
            candidates.remove(obj1)
        for obj2 in self.objs2:
            candidates.remove(obj2)
        return candidates

    def hill_climb(self, maximum=None, image_prefix=None, log=False):
        """
        Performs hill-climbing to find a solution"""
        count = 0

        # Start by initializing objs2 randomly
        self.objs2 = set()
        for i in range(self.maxh):
            self.objs2.add(random.choice(list(self.available_spaces())))
        if log:
            print("initial state: cost", self.get_cost(self.objs2))
        if image_prefix:
            self.output_image(f"{image_prefix}{str(count).zfill(3)}.png")

        # KEY-IDEA
        # COntinue til reach maximum number of iterations
        while maximum is None or count < maximum:
            count += 1
            best_neighbors = []
            best_neighbor_cost = None

            # consider all objs2 to move
            for obj2 in self.objs2:
                # consider all neighbors for obj2
                for replacement in self.get_neighbors(*obj2):
                    # generate a neighboring set of hospitals
                    neighbor = self.objs2.copy()
                    neighbor.remove(obj2)
                    neighbor.add(replacement)

                    # check if neighbor is best so far
                    cost = self.get_cost(neighbor)
                    if best_neighbor_cost is None or cost < best_neighbor_cost:
                        best_neighbor_cost = cost
                        best_neighbors = [
                            neighbor
                        ]  # if best neighbor is better, update and keep track
                    elif best_neighbor_cost == cost:
                        best_neighbors.append(neighbor)

            # None of the neighbors are better than the current state
            if best_neighbor_cost >= self.get_cost(self.objs2):
                return self.objs2

            # Move to a highest-valued neighbor
            else:
                if log:
                    print(f"Found better neighbor: cost {best_neighbor_cost}")
                self.objs2 = random.choice(best_neighbors)

            # Generate image
            if image_prefix:
                self.output_image(f"{image_prefix}{str(count).zfill(3)}.png")

    def random_restart(self, maximum, image_prefix=None, log=False):
        """Repeats hill-climbing multiple times"""
        best_objs2 = None
        best_cost = None

        # Repeat hill-climbing a fixed number of times
        for i in range(maximum):
            objs2 = self.hill_climb()
            cost = self.get_cost(objs2)
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_objs2 = objs2
                if log:
                    print(f"{i}: Found new best state: cost {cost}")
            else:
                if log:
                    print(f"{i}: Found state: cost {cost}")
