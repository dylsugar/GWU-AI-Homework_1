import numpy as np

import util
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
        self.lower = np.inf
        self.total_explored = 99

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

    def get_h(self, state) -> int:
        target = self.env.goal - self.env.volumes[-1]
        # print(target)
        # print(self.env.pitchers)
        # print(self.env.volumes)
        estimate = 0

        # if the infinite goal pitcher is overfilled
        if target < 0:
            # will likely need additional logic here to estimate how many steps to goal (how much to pour out)
            # maybe something like: if excess amount != any pitcher, estimate = 2. 1 to pour out, 1 to pour in
            # ideal case: pour excess into a cup to reach goal state exactly
            estimate = 1
            return estimate

        # check all pitchers except last infinite
        for volume in self.env.volumes[:-1]:
            # if the cup has water
            if volume != 0:
                # print('cup has water: ', volume)
                if abs(target - volume) > target:
                    break
                target -= volume
                estimate += 1       # add a step for transferring between cup and solution

        # get the pitcher closest to the goal
        closest, closest_index = util.find_closest(self.env.pitchers, target)
        multiple: int = util.closest_multiple(closest, target)

        # add 2 steps for each multiple (1 to fill, 1 to transfer)
        estimate += multiple*2

        # remove a step if the cup is already full
        if self.env.volumes[closest_index] > 0:
            estimate -= 1

        # if the target quantity isn't reached exactly, add (ideally) only 1 step to
        # transfer in/out the remaining amount
        if abs(target - closest*multiple) != 0:
            estimate += 1

        # goal = self.env.goal
        # total = np.sum(state)
        # diffs = abs(state - goal)
        # return min(diffs) + (0.2 * total)
        return estimate

    def step(self, naive=True) -> bool:
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

        # print(f'low index: {low_index}, low_f: {low_f}')
        q = self.open.pop(low_index)
        # print("q: ", q)
        # Generate Q's successors
        successors = self.env.propagate(q.state[:-1], q.state[-1])
        # Add to open
        for state in successors:
            if self.check_finished(state):
                n = Node(state, q, self.get_h(state))

                val = self.clear_up(n)

                if naive:
                    self.success = val
                    return True
                # print(val, self.lower, val < self.lower)
                if val.g < self.lower:
                    self.success = val
                    self.lower = val.g

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
        self.close_stale()
        if len(self.closed) % 100 == 0:
            print(f"Explored {len(self.closed)}")
        return len(self.open) <= 0

    def close_stale(self):
        if self.lower == np.inf:
            return

        new_open = []
        for node in self.open:
            if node.g <= self.lower:
                new_open.append(node)
            else:
                self.closed.append(node)

        self.open = new_open.copy()
        # print(len(self.open), len(self.closed), self.lower)

    def check_finished(self, state) -> bool:
        for elem in state[:-1]:
            if elem == self.env.goal:
                return True
        return False

    def run(self, naive=True):
        while not self.empty:
            self.empty = self.step(naive)

    def clear_up(self, poss):

        node = poss
        self.closed.append(node)
        success_index = np.where(node.state[:-1] == self.env.goal)[0]

        # print(node.state[:-1][-1], self.env.goal)
        if not node.state[:-1][-1] == self.env.goal:
            new_state = np.copy(node.state)
            if not node.state[:-1][-1] == 0:
                new_state[-2] = 0
                new_state[-1] += 1
                node = Node(new_state, node)
                self.closed.append(node)

            new_state[-2] = self.env.goal
            new_state[-1] += 1
            new_state[success_index] = 0
            node = Node(new_state, node)
            self.closed.append(node)

        return node
