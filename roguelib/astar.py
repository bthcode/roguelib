"""
A* pathfinding module for Pyro.

This module assumes movement on a grid, rather than an arbitrary graph.
"""
from heapq import heappush, heappop
from typing import Callable, Iterable, List
from numbers import Number

class NodeList(object):
    def __init__(self, name="nodelist"):
        self.nodes = []
        self.idx = {}
        self.name = name

    def add(self, x:int, y:int, cost:Number, h:Number, parent_x:int, parent_y:int)->None:
        '''
        Params
        ------
        x : int : grid x
        y : int : grid y
        cost : float : cost of moving to grid point x,y
        h : int : heuristic cost (how close does it get you to the goal?)
        parent_x : grid x of previous point
        parent_y : grid y of previous point
        '''
        if self.has(x, y):
            raise ValueError
        node = [cost+h, cost, h, x, y, (parent_x, parent_y)]
        heappush(self.nodes, node)
        self.idx[(x, y)] = node

    def best_path_so_far(self) -> List:
        '''
        Return the path to the closest node we found (lowest heuristic)
        '''
        lowest = 99999
        for n in self.nodes:
            if n[2] < lowest:
                lowest = n[2]
                x, y = n[3], n[4]
        return self.path_from(x, y)

    def has(self, x:int, y:int) -> bool:
        return (x, y) in self.idx  # self.idx.has_key((x, y))

    def node(self, x:int, y:int):
        return self.idx[(x, y)]

    def path_from(self, x:int, y:int):
        '''
        Return a path from the given node back to the start:
        '''
        node = self.node(x, y)
        path = []
        while node[5] != (None, None):
            path.insert(0, (x, y))
            x, y = node[5]
            node = self.node(x, y)
        return path

    def pop(self)->List:
        node = heappop(self.nodes)
        del self.idx[(node[3], node[4])]
        return node

    def remove(self, x:int, y:int) -> None:
        self.nodes = [n for n in self.nodes if (n[3], n[4]) != (x, y)]
        del self.idx[(x, y)]


def path(start_x:int, start_y:int, dest_x:int, dest_y:int, 
         passable:Callable[[int,int],bool], max_length:int=99999) -> Iterable:
    '''
    Use A-star to fine a bath from start x,y to dest x,y

    Params
    ------
    start_x : int : starting grid x
    start_y : int : starting grid y
    start_x : int : ending grid x
    start_y : int : ending grid y
    passable : Func : Reference to function that determines if a given x,y is passable
    max_length : int : max length of acceptable path

    Returns
    -------
    List( [x,y], [x1,y1], ... )  : Best Path
    '''
    open_squares = NodeList("Open")
    h = max(abs(dest_x - start_x), abs(dest_y - start_y))
    open_squares.add(start_x, start_y, 0, h, None, None)
    closed = NodeList("Closed")
    while len(open_squares.nodes) > 0:
        node = open_squares.pop()
        node_cost_h, node_cost, node_h, node_x, node_y, node_parent = node
        if node_cost > max_length:
            # We've failed to find a short enough path; return the best we've got:
            break
        # Put the parent node in the closed set:
        closed.add(node_x, node_y, node_cost, node_h,
                   node_parent[0], node_parent[1])
        # See if we're at the destination:
        if (node_x, node_y) == (dest_x, dest_y):
            # We found the path; return it:
            p = closed.path_from(node_x, node_y)
            return p
        # Check adjacent nodes:
        for i in range(node_x - 1, node_x + 2):
            for j in range(node_y - 1, node_y + 2):
                dx, dy = i - node_x, j - node_y
                # Skip the current node:
                if (i, j) == (node_x, node_y):
                    continue
                # If this node is impassable, disregard it:
                if not passable(i, j):
                    continue
                # Calculate the heuristic:
                h = max(abs(dest_x - i), abs(dest_y - j))
                # Calculate the move cost; assign slightly more to diagonal moves
                # to discourage superfluous wandering:
                if dx == 0 or dy == 0:
                    move_cost = 1
                else:
                    move_cost = 1.001
                cost = node_cost + move_cost
                # See if it's already in the closed set:
                if closed.has(i, j):
                    c = closed.node(i, j)
                    if cost < c[1]:
                        open_square.add(i, j, cost, h, node_x, node_y)
                        closed.remove(i, j)
                else:
                    # It's not in the closed list, put it in the open list if it's not already:
                    if not open_squares.has(i, j):
                        open_squares.add(i, j, cost, h, node_x, node_y)
    # We ran out of open nodes; pathfinding failed:
    # Do the best we can:
    p = closed.best_path_so_far()
    return p

def get_test_grid():
    Grid = [ [ 0, 1, 0, 0, 0 ],
             [ 0, 1, 0, 1, 0 ],
             [ 0, 0, 1, 1, 0 ],
             [ 0, 0, 1, 1, 0 ],
             [ 0, 0, 1, 1, 0 ] ]
    return Grid



def test_passable(x:int,y:int)->bool:
    Grid = get_test_grid()

    if x < 0 or x >= len(Grid[0]):
        return False
    if y < 0 or y >= len(Grid):
        return False

    if (Grid[y][x]): 
        return False
    else:
        return True 


if __name__ == "__main__":
    import pprint
    g = get_test_grid()
    start_x = 0
    start_y = 0
    end_x = 4
    end_y = 4
    p = path(start_x, start_y, end_x, end_y, test_passable) 

    # For printing out path
    l = []
    for i in range(len(g)):
        l.append( [0] * len(g[0]))
    l[start_y][start_x] = 8

    print ("GRID: (1 is blocked)")
    print (pprint.pformat(g))

    for point in p:
        l[point[1]][point[0]] = 1
    l[end_y][end_x] = 9

    print ("PATH: (8->9)")
    print (pprint.pformat((l)))
