import numpy as np
from math import gcd
from functools import reduce
from typing import Tuple
import numba as nb


def is_valid_problem(pitchers: np.array, target: int) -> bool:
    """Returns true if there is a valid solution, false if there is not.

    The logic behind this stems from Bezout's identity, which relates an integer
    in terms of the gcd of other integers. More specifically, if d is the greatest
    common divisor of integers (a, b), then integers of the form ax + by are multiples
    of d. This idea can be generalized to more than 2 integers, which proves
    useful for this problem: a valid solution exists iff the target quantity is a 
    multiple of the gcd of all the pitcher values.
    
    More information: https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity#Generalizations
    """
    # get the gcd of all the pitchers
    x: int = reduce(gcd, pitchers)
    # problem is valid if the target is a multiple of the gcd
    return target % x == 0


@nb.njit(nogil=True)
def find_closest(pitchers: np.array, target: int) -> Tuple[int, int]:
    """Returns the pitcher that is closest to the target value, and the index of that pitcher in the array"""
    closest = pitchers[0]
    index = 0
    smallest_diff = abs(target - pitchers[0])

    for (i, pitcher) in enumerate(pitchers):
        diff = abs(target - pitcher)
        if diff < smallest_diff:
            closest = pitcher
            smallest_diff = diff
            index = i

    return closest, index


@nb.njit(nogil=True)
def closest_multiple(pitcher: int, target: int) -> int:
    """Returns the closest multiple of the pitcher to the target"""
    if pitcher == 0:
        return 0
    return round(target / pitcher)
