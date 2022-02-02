import numpy as np

from Environment import Environment as Env


class Node:
    def __init__(self, state, parent, h=0):
        self.state = np.copy(state)
        self.parent = parent
        self.g = state[-1]
        self.h = h
        self.f = self.g + self.h

    def __str__(self) -> str:
        return f"{self.state}, {self.f}"

    def __eq__(self, __o: object) -> bool:

        if isinstance(__o, Node):
            return (__o.state[:-1] == self.state[:-1]).all()

        return False


class AStar:
    def __init__(self, env: Env):
        self.env = env
        self.open = []
        self.closed = []

        self.open.append(Node(self.env.get_state(), None))
        # self.open.append(Node([0,8,0,1], self.open[0]))
        self.empty = False
        self.success = None

    def print_path(self):
        path = []

        n = self.success

        while n is not None:
            path.insert(0, n.state[:-1])
            n = n.parent

        print(path)

    def get_steps(self) -> int:
        if self.success is None:
            return -1
        return self.success.g

    def list_open(self):
        for node in self.open:
            print(node)

    def list_closed(self):
        for node in self.closed:
            print(node)

    def get_h(self, state) -> float:
        goal = self.env.goal
        total = np.sum(state)
        diffs = abs(state - goal)
        return min(diffs) + (0.2 * total)

    def step(self) -> bool:
        if len(self.open) <= 0:
            return True

        # Get lowest f
        low_index, low_f = 0, self.open[0].f

        if len(self.open) > 1:
            for i in range(1, len(self.open)):
                new_f = self.open[i].f
                if new_f < low_f:
                    low_f = new_f
                    low_index = i

        q = self.open.pop(low_index)
        # Generate Q's successors
        successors = self.env.proporgate(q.state[:-1], q.state[-1])
        # Add to open
        for state in successors:
            if self.check_finished(state):
                self.success = Node(state, q, self.get_h(state))
                self.clear_up()
                return True

            to_add = Node(state, q, self.get_h(state[:-1]))
            skip = False
            for i in range(len(self.open)):
                if self.open[i] == to_add and self.open[i].f <= to_add.f:
                    skip = True
                    break
            if skip:
                continue

            for i in range(len(self.closed)):
                if self.closed[i] == to_add and self.closed[i].f <= to_add.f:
                    skip = True
                    break
            if skip:
                continue
            self.open.append(to_add)
            self.closed.append(q)
        return len(self.open) <= 0

    def check_finished(self, state) -> bool:
        for elem in state[:-1]:
            if elem == self.env.goal:
                return True
        return False

    def run(self):
        while not self.empty:
            self.empty = self.step()

    def clear_up(self):
        if self.success is None:
            return

        node = self.success
        success_index = np.where(node.state[:-1] == self.env.goal)[0]

        if not node.state[:-1][-1] == self.env.goal:
            new_state = np.copy(node.state)
            if not node.state[:-1][-1] == 0:
                new_state[-2] = 0
                new_state[-1] += 1
                node = Node(new_state, node)

            new_state[-2] = self.env.goal
            new_state[-1] += 1
            new_state[success_index] = 0
            node = Node(new_state, node)

            self.success = node
