# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

from __future__ import annotations

import grid

# some of these types are deprecated: https://www.python.org/dev/peps/pep-0585/
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
import collections
import heapq
T = TypeVar('T')

Location = TypeVar('Location')
GridLocation = Tuple[int, int]

#------------------------------
# Graphs
#------------------------------
class Graph(Protocol):
    def neighbors(self, loc: Location) -> list[Location]: pass

class WeightedGraph(Graph):
    def cost(self, from_id: Location, to_id: Location) -> float: pass

#------------------------------
# Queue
#------------------------------
class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]


def reconstruct_path(came_from: dict[Location, Location],
                     start: Location, goal: Location) -> list[Location]:

    current: Location = goal
    path: list[Location] = []
    if goal not in came_from: # no path was found
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    #path.append(start) # optional
    path.reverse() # optional
    return path


#-------------------------------------------------
# Search Mechanisms
#-------------------------------------------------
def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(cost_dict, impassable_list, graph: grid.Grid,  start: Location, goal: Location, max_length=100):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break

        for next_i in graph.neighbors(current):
            tile = graph.get_tile(next_i)
            # optional - don't consider paths in impassable list
            #if tile in impassable_list: continue
            cost = cost_dict.get(tile, 1.0)
            new_cost = cost_so_far[current] + cost
            if new_cost > max_length: continue
            if next_i not in cost_so_far or new_cost < cost_so_far[next_i]:
                cost_so_far[next_i] = new_cost
                priority = new_cost + heuristic(next_i, goal)
                frontier.put(next_i, priority)
                came_from[next_i] = current
    return came_from, cost_so_far


if __name__ == '__main__':
    start, goal = (1, 4), (8, 3)

    G = grid.Grid(12,12, '.')
    G[5,1:11] = '#'

    G[5,0] = 'o'

    cost_dict = { '.' : 1.0, '#' : 999, 'o' : 8 }
    impassable_list = ['#']

    came_from, cost_so_far = a_star_search(cost_dict, impassable_list, G, start, goal)
    
    path = reconstruct_path(came_from, start=start, goal=goal)
    for p in path:
        G[p] = '*'
    print (G)
    
