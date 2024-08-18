import Grid
import random
import math
import copy
from typing import List
import logging

from anytree import Node, RenderTree, LevelOrderIter, AnyNode


class Room:
    """Room coordinaes

    Attributes
    ----------
    y1 : int
        Y coordinate of top corners
    y2 : int
        Y coordinate of bottom corners
    x1 : int
        X coordinate of left side
    x2 : int
        X coordinate of right side
    """

    def __init__(self, y1: int, y2: int, x1: int, x2: int):
        self.x1: int = x1
        self.x2: int = x2
        self.y1: int = y1
        self.y2: int = y2
        self.height: int = self.y2 - self.y1
        self.width: int = self.x2 - self.x1
        self.control_points = self.calc_control_points()

    def calc_control_points(self):
        """Calculate the mid-point of each side"""
        pts = {
            "U": [self.y1 - 1, self.x1 + self.width // 2],
            "D": [self.y2, self.x1 + self.width // 2],
            "L": [self.y1 + self.height // 2, self.x1 - 1],
            "R": [self.y1 + self.height // 2, self.x2],
        }
        return pts

    def __repr__(self):
        return f"{self.y1},{self.y2},{self.x1},{self.x2},{self.height},{self.width}"


class DungeonGenerator:
    """Dungeon generatur using BSP Algorithm

    References
    ----------
    https://www.roguebasin.com/index.php/Basic_BSP_Dungeon_generation
    """

    def __init__(self, width:int=120, height:int=30, num_rooms:int=16):
        '''
        Parameters
        ----------
        width : int
            map width
        height : int
            map height
        num_rooms : int
            target num rooms - iterate log2(num_room) times
        '''
        self.width = 120
        self.height = 30
        self.grid = Grid.Grid(self.height, self.width, "#")
        self.num_levels = int(math.log2(num_rooms))

        graph = self.make_rooms()
        self.connect_rooms(graph)

    def make_rooms(self):
        """Construct rooms using BSP algorithm"""
        root = Room(2, self.height - 2, 2, self.width - 2)

        graph = AnyNode(id="root", room=root, split=None)

        # -------------------------------------------------
        # Create a binary tree of divided spaces
        # -------------------------------------------------
        counter = 0
        for i in range(self.num_levels):
            for cur_node in graph.leaves:
                cur_room = cur_node.room
                split_dir = random.choices(
                    ["vertical", "horizontal"],
                    weights=[cur_room.height, cur_room.width],
                )[0]
                # vertical split: pick a row, make two rooms
                if split_dir == "vertical":
                    # weighted choice taller rooms
                    if cur_room.height < 9:
                        new_room = AnyNode(
                            id=str(counter),
                            room=copy.copy(cur_room),
                            split=None,
                            parent=cur_node,
                        )
                        counter += 1
                    else:
                        row = random.randint(cur_room.y1 + 4, cur_room.y2 - 4)
                        new_room = AnyNode(
                            id=str(counter),
                            room=Room(cur_room.y1, row - 1, cur_room.x1, cur_room.x2),
                            split="vertical",
                            parent=cur_node,
                        )
                        counter += 1
                        new_room = AnyNode(
                            id=str(counter),
                            room=Room(row + 1, cur_room.y2, cur_room.x1, cur_room.x2),
                            split="vertical",
                            parent=cur_node,
                        )
                        counter += 1
                # horizontal split: pick a column, make two rooms
                else:
                    # weighted choice wider rooms
                    if cur_room.width < 9:
                        new_room = AnyNode(
                            id=str(counter),
                            room=copy.copy(cur_room),
                            split=None,
                            parent=cur_node,
                        )
                        counter += 1
                    else:
                        col = random.randint(cur_room.x1 + 4, cur_room.x2 - 4)
                        new_room = AnyNode(
                            id=str(counter),
                            room=Room(cur_room.y1, cur_room.y2, cur_room.x1, col - 1),
                            split="horizontal",
                            parent=cur_node,
                        )
                        counter += 1
                        new_room = AnyNode(
                            id=str(counter),
                            room=Room(cur_room.y1, cur_room.y2, col + 1, cur_room.x2),
                            split="horizontal",
                            parent=cur_node,
                        )
                        counter += 1

        # -------------------------------------------
        # For each space, construct a room
        # -------------------------------------------
        for leaf in graph.leaves:
            room = leaf.room
            w = random.randint(2, room.width - 1)
            h = random.randint(2, room.height - 1)
            x1 = random.randint(room.x1 + 1, room.x2 - w)
            x2 = x1 + w
            y1 = random.randint(room.y1 + 1, room.y2 - h)
            y2 = y1 + h
            leaf.room = Room(y1, y2, x1, x2)
            room = leaf.room
            self.grid[room.y1 : room.y2, room.x1 : room.x2] = " "  # leaf.id[0]
        return graph

    def calc_control_points(self, room):
        """Get control points for a room"""
        pts = [
            room.control_points["U"],
            room.control_points["D"],
            room.control_points["L"],
            room.control_points["R"],
        ]
        return pts

    def find_min_distance(
        self, pts1: list[int, int], pts2: list[int, int]
    ) -> [int, int, float]:
        """Find minimum distance between two sets of points

        Returns
        -------
        left : int
            Index of minimum disatnce into pts1
        right : int
            Index of minimum distance into pts2
        min_dist : float
            Calculated distnace
        """
        min_dist = 99999
        left = -1
        right = -1
        for idx1, pt1 in enumerate(pts1):
            for idx2, pt2 in enumerate(pts2):
                dist = math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    left = idx1
                    right = idx2
        return left, right, min_dist

    def calc_intersection(self, room1: Room, room2: Room) -> [List[int], List[int]]:
        """Calculate intersections in x and y of two rectangles

        Returns
        -------
        intseraction_y : List[int]
            intersection of y values
        intersction_x : List[int]
            intsersection of x values
        """
        ys1 = set(range(room1.y1, room1.y2))
        ys2 = set(range(room2.y1, room2.y2))
        intersection_y = list(ys1.intersection(ys2))

        xs1 = set(range(room1.x1 + 1, room1.x2))
        xs2 = set(range(room2.x1 + 1, room2.x2))
        intersection_x = list(xs1.intersection(xs2))
        return intersection_y, intersection_x

    def is_left(self, room1, room2):
        """return true if room1 is left of room2"""
        if room1.x2 < room2.x1:
            return True
        return False

    def is_above(self, room1, room2):
        """return true if room1 is above room2"""
        if room1.y2 < room2.y1:
            return True
        return False

    def connect_rooms(self, graph) -> None:
        """Connect rooms sotred in a sparse binary graph

        Returns
        -------
        None
        """
        ctr = 0

        # ----------------------------------------------
        # Iterate over levels of the graph
        # ----------------------------------------------
        for node in LevelOrderIter(graph):

            # -----------------------------------------------
            # If there is more than one child, connect them
            # -----------------------------------------------
            if len(node.children) == 2:

                # ----------------------------------------------------
                # Find the closest leaves from left set and right set
                # ----------------------------------------------------
                min_dist = 999999
                for idx, leaf1 in enumerate(node.children[0].leaves):
                    for idx2, leaf2 in enumerate(node.children[1].leaves):
                        pts1 = self.calc_control_points(leaf1.room)
                        pts2 = self.calc_control_points(leaf2.room)
                        left, right, dist = self.find_min_distance(pts1, pts2)
                        if dist < min_dist:
                            n1 = leaf1
                            n2 = leaf2
                            min_dist = dist

                # ------------------------------------------------------
                #  if the xs or ys intersect, connect directly
                # ------------------------------------------------------
                intersection_y, intersection_x = self.calc_intersection(
                    n1.room, n2.room
                )
                if len(intersection_y):
                    y1 = y2 = random.choice(intersection_y)
                    if self.is_left(n1.room, n2.room):
                        x1 = n1.room.x2
                        x2 = n2.room.x1 - 1
                        corridor = self.calc_line_segment(x1, x2, y1, y2)
                    else:
                        x1 = n1.room.x1 - 1
                        x2 = n2.room.x2
                        corridor = self.calc_line_segment(x1, x2, y1, y2)
                elif len(intersection_x):
                    x1 = x2 = random.choice(intersection_x)
                    if self.is_above(n1.room, n2.room):
                        y1 = n1.room.y2
                        y2 = n2.room.y1 - 1
                        corridor = self.calc_line_segment(x1, x2, y1, y2)
                    else:
                        y1 = n1.room.y1 - 1
                        y2 = n2.room.y2
                        corridor = self.calc_line_segment(x1, x2, y1, y2)

                else:  # no intersection

                    # -------------------------------------------------
                    # Find shortest path between room control points
                    # -------------------------------------------------
                    pts1 = self.calc_control_points(n1.room)
                    pts2 = self.calc_control_points(n2.room)
                    left, right, _ = self.find_min_distance(pts1, pts2)

                    sides = ["U", "D", "L", "R"]

                    lside = sides[left]
                    rside = sides[right]

                    # ---------------------------------------
                    # Map control point combinations to
                    #  directions
                    #    V = go vertical
                    #    S = go sideways
                    # ---------------------------------------
                    dirmap = {
                        "DD": [],
                        "DR": "VS",
                        "DL": "VS",
                        "DU": "VSV",
                        "RD": "VS",
                        "RR": [],
                        "RL": "SVS",
                        "RU": "SV",
                        "LD": "SV",
                        "LR": "SVS",
                        "LL": [],
                        "LU": "SV",
                        "UD": "VSV",
                        "UR": "VS",
                        "UL": "VS",
                        "UU": [],
                    }
                    dir_sequence = dirmap[f"{lside}{rside}"]

                    y1, x1 = pts1[left]
                    y2, x2 = pts2[right]

                    # ---------------------------------------------
                    # if one room is top/bottom and one is a side,
                    #  make a single turn
                    # ---------------------------------------------
                    if len(dir_sequence) == 2:
                        if dir_sequence[0] == "S":
                            corridor = self.calc_line_segment(x1, x2, y1, y1)
                            corridor.extend(self.calc_line_segment(x2, x2, y1, y2))
                        elif dir_sequence[0] == "V":
                            corridor = self.calc_line_segment(x1, x1, y1, y2)
                            corridor.extend(self.calc_line_segment(x1, x2, y2, y2))
                    # ---------------------------------------------
                    # if both are sides or both are top/bottom,
                    #  make two turns
                    # ---------------------------------------------
                    #  make a single turn
                    elif len(dir_sequence) == 3:
                        if dir_sequence[0] == "S":
                            pt1 = [y1, x1 + (x2 - x1) // 2]
                            pt2 = [y2, x1 + (x2 - x1) // 2]
                        else:
                            pt1 = [y1 + (y2 - y1) // 2, x1]
                            pt2 = [y1 + (y2 - y1) // 2, x2]
                        corridor = self.calc_line_segment(x1, pt1[1], y1, pt1[0])
                        corridor.extend(
                            self.calc_line_segment(pt1[1], pt2[1], pt1[0], pt2[0])
                        )
                        corridor.extend(self.calc_line_segment(pt2[1], x2, pt2[0], y2))
                    else:
                        logging.error(
                            f"ERROR: Unexpected room connection: {lside}{rside}"
                        )

                if len(corridor) > 1:
                    for pt in corridor:
                        if self.grid[pt] not in [" ", "+"]:
                            self.grid[pt] = "."
                    self.grid[corridor[0][0], corridor[0][1]] = "+"
                    self.grid[corridor[-1][0], corridor[-1][1]] = "+"

                ctr += 1

    def calc_line_segment(self, x1: int, x2: int, y1: int, y2: int) -> list[int, int]:
        """Calculate a straight line segment from y1,x1 to y2,x2"""
        pts = [[y1, x1]]
        # Move in Y
        if x1 == x2:
            while pts[-1][0] != y2:
                add = 1
                if y2 - y1 < 0:
                    add = -1
                pts.append([pts[-1][0] + add, pts[-1][1]])
        # Move in X
        elif y1 == y2:
            while pts[-1][1] != x2:
                add = 1
                if x2 - x1 < 0:
                    add = -1
                pts.append([pts[-1][0], pts[-1][1] + add])
        return pts

    def __repr__(self):
        return str(self.grid)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser('')
    parser.add_argument('--width', default=80, type=int)
    parser.add_argument('--height', default=40, type=int)
    parser.add_argument('--num_rooms', default=16, type=int)

    args = parser.parse_args()

    D = DungeonGenerator(width=args.width, 
                         height=args.height, 
                         num_rooms=args.num_rooms)
    print(D)
