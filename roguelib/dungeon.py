import Grid
import random
import math

from anytree import Node, RenderTree, LevelOrderIter, AnyNode

class dungeon:
    def __init__(self):
        self.width=120
        self.height=30
        self.grid = Grid.Grid(self.height, self.width, "#")

        graph = self.make_rooms()
        self.connect_rooms(graph)

    def make_rooms(self):
        '''https://www.roguebasin.com/index.php/Basic_BSP_Dungeon_generation'''
        root = [2, self.height-2, 2, self.width-2]

        graph = AnyNode(id='root', room=root, split=None )
        
        counter = 0
        for i in range(3):
            for cur_node in graph.leaves:
                room = cur_node.room
                split_dir = random.choices(['vertical', 'horizontal'],
                                           weights=[room[1]-room[0], room[3]-room[2]])[0]
                # vertical split: pick a row, make two rooms
                if split_dir == 'vertical':
                    # weighted choice taller rooms
                    if room[1] - room[0] < 9: 
                        new_room = AnyNode(id=str(counter), room=room, split=None, parent=cur_node)
                        counter+=1
                    else:
                        row = random.randint(room[0]+4, room[1]-4)
                        new_room = AnyNode(id=str(counter), room=[room[0], row-1, room[2], room[3]], split='vertical', parent=cur_node)
                        counter+=1
                        new_room = AnyNode(id=str(counter), room=[row+1, room[1], room[2], room[3]], split='vertical', parent=cur_node)
                        counter+=1
                # horizontal split: pick a column, make two rooms
                else:
                    # weighted choice wider rooms
                    if room[3] - room[2] < 9:
                        new_room = AnyNode(id=str(counter), room=room, split=None, parent=cur_node)
                        counter +=1
                    else:
                        col = random.randint(room[2]+4, room[3]-4)
                        new_room = AnyNode(id=str(counter), room=[room[0], room[1], room[2], col-1 ], split='horizontal', parent=cur_node)
                        counter += 1
                        new_room = AnyNode(id=str(counter), room=[room[0], room[1], col+1, room[3] ], split='horizontal',  parent=cur_node)
                        counter += 1

        for leaf in graph.leaves:
            room  = leaf.room
            w = random.randint(2, room[3] - room[2])
            h = random.randint(2, room[1] - room[0])
            x1 = random.randint(room[2], room[3]-w)
            x2 = x1 + w
            y1 = random.randint(room[0], room[1]-h)
            y2 = y1 + h
            leaf.room = [y1,y2,x1,x2]
            room = leaf.room
            self.grid[room[0]:room[1], room[2]:room[3]] = ' ' #leaf.id[0]
        return graph

    def connect_vertical(self, room1, room2, pt1, pt2):
        ''' room1 above (smaller y) '''
        #xs1 = set(range(room1[2]+1, room1[3]))
        #xs2 = set(range(room2[2]+1, room2[3]))
        #intersection = list(xs1.intersection(xs2))
        y1 = pt1[0] #room1[1]
        y2 = pt2[0] #room2[0]-1
        #if 0 and len(intersection):
        #    x1 = random.choice(intersection)
        #    x2 = x1
        #else:
        if 1:
            x1 = pt1[1]
            x2 = pt2[1]
        corridor = self.calc_corridor(x1, x2, y1, y2, 'vertical')
        for pt in corridor:
            self.grid[pt] = '-'
        self.grid[corridor[0][0], corridor[0][1]] = '+'
        self.grid[corridor[-1][0], corridor[-1][1]] = '+'

    def connect_horizontal(self, room1, room2, pt1, pt2):
        ys1 = set(range(room1[0]+1, room1[1]))
        ys2 = set(range(room2[0]+1, room2[1]))
        intersection = list(ys1.intersection(ys2))
        x1 = pt1[1] #room1[3]
        x2 = pt2[1] #room2[2]-1
        if 0 and len(intersection):
            y1 = random.choice(intersection)
            y2 = y1
        else:
            y1 = pt1[0]
            y2 = pt2[0]
        corridor = self.calc_corridor(x1, x2, y1, y2, 'horizontal')
        for pt in corridor:
            self.grid[pt] = '-'
        self.grid[corridor[0][0], corridor[0][1]] = '+'
        self.grid[corridor[-1][0], corridor[-1][1]] = '+'

    def calc_control_points(self, room):
        pts = [ [room[0]-1, room[2] + (room[3]-room[2])//2],  # U
                [room[1], room[2] + (room[3]-room[2])//2],    # D
                [room[0] + (room[1]-room[0])//2, room[2]-1 ], # L
                [room[0] + (room[1]-room[0])//2, room[3] ]    # R
              ]
        return pts

    def find_min_distance(self, pts1, pts2):
        min_dist = 99999
        left = -1
        right = -1
        for idx1, pt1 in enumerate(pts1):
            for idx2, pt2 in enumerate(pts2):
                dist = math.sqrt( (pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    left = idx1
                    right = idx2
        return left, right

    def calc_intersection(self, room1, room2):
        ys1 = set(range(room1[0]+1, room1[1]))
        ys2 = set(range(room2[0]+1, room2[1]))
        intersection_y = list(ys1.intersection(ys2))

        xs1 = set(range(room1[2]+1, room1[3]))
        xs2 = set(range(room2[2]+1, room2[3]))
        intersection_x = list(xs1.intersection(xs2))
        return intersection_y, intersection_x

    def is_left(self, room1, room2):
        if room1[3] < room2[2]: 
            return True
        return False

    def is_above(self, room1, room2):
        if room1[1] < room2[0]:
            return True
        return False

    def connect_rooms(self, graph):
        ctr = 0
        for node in LevelOrderIter(graph):
            if len(node.children) == 2:
                #if not node.children[0].is_leaf: continue
                
                n1 = node.children[0].leaves[0]
                n2 = node.children[1].leaves[0]

                # side <-> top/bottom
                #   - lr, ud
                # top/bottom <-> top/bottom
                #   - test intersection
                #   - ud, lr, ud
                # side <-> side
                #   - test intersection
                #   - lr, ud, lr

                # 1. get intersections in x and y
                #  if possible, connect largest intersection
                intersection_y, intersection_x = self.calc_intersection(n1.room, n2.room)
                if len(intersection_y):
                    y1 = y2 = random.choice(intersection_y)
                    if self.is_left(n1.room, n2.room):
                        x1 = n1.room[3]
                        x2 = n2.room[2]-1
                        corridor = self.calc_corridor(x1, x2, y1, y2, 'horizontal')
                        for pt in corridor:
                            self.grid[pt] = '-'
                        self.grid[corridor[0][0], corridor[0][1]] = '+'
                        self.grid[corridor[-1][0], corridor[-1][1]] = '+'
                    else:
                        x1 = n1.room[2]-1
                        x2 = n2.room[3]
                        corridor = self.calc_corridor(x1, x2, y1, y2, 'horizontal')
                        for pt in corridor:
                            self.grid[pt] = '-'
                        self.grid[corridor[0][0], corridor[0][1]] = '+'
                        self.grid[corridor[-1][0], corridor[-1][1]] = '+'
                elif len(intersection_x):
                    x1 = x2 = random.choice(intersection_x)
                    if self.is_above(n1.room, n2.room):
                        y1 = n1.room[1]
                        y2 = n2.room[0]-1
                        corridor = self.calc_corridor(x1, x2, y1, y2, 'horizontal')
                        for pt in corridor:
                            self.grid[pt] = '-'
                        self.grid[corridor[0][0], corridor[0][1]] = '+'
                        self.grid[corridor[-1][0], corridor[-1][1]] = '+'
                    else:
                        y1 = n1.room[0]-1
                        y2 = n2.room[1]
                        corridor = self.calc_corridor(x1, x2, y1, y2, 'horizontal')
                        for pt in corridor:
                            self.grid[pt] = '-'
                        self.grid[corridor[0][0], corridor[0][1]] = '+'
                        self.grid[corridor[-1][0], corridor[-1][1]] = '+'

                elif len(intersection_y) == 0 and len(intersection_x) == 0:
                    # 2. if not, do a zig/zag

                    pts1 = self.calc_control_points(n1.room)
                    pts2 = self.calc_control_points(n2.room)
                    left, right = self.find_min_distance(pts1, pts2)

                    sides = [ 'U', 'D', 'L', 'R' ]

                    lside = sides[left]
                    rside = sides[right]

                    dirmap = { 
                               'DD' : [],
                               'DR' : 'VS',
                               'DL' : 'VS',
                               'DU' : 'VSV',
                               'RD' : 'VS',
                               'RR' : [],
                               'RL' : 'SVS',
                               'RU' : 'SV',
                               'LD' :  'SV',
                              'LR' :   'SVS',
                              'LL' : [],
                              'LU' :  'SV',
                              'UD' :  'VSV',
                              'UR' :  'VS',
                              'UL' :  'VS',
                              'UU' : [],
                              }
                    dir_sequence = dirmap[ f'{lside}{rside}' ]

                    if len(dir_sequence) == 2:
                        y1, x1 = pts1[left]
                        y2, x2 = pts2[right]
                        print ("HERE")

                        if dir_sequence[0] == 'S':
                            corridor = self.calc_corridor(x1, x2, y1, y2, 'horizontal')
                            corridor.extend(self.calc_corridor(x2, x2, y1, y2, 'vertical'))
                        else:
                            corridor = self.calc_corridor(x1, x1, y1, y2, 'vertical')
                            corridor.extend(self.calc_corridor(x1, x2, y2, y2, 'horizontal'))
                        for pt in corridor:
                            self.grid[pt] = '-'
                        self.grid[corridor[0][0], corridor[0][1]] = '+'
                        self.grid[corridor[-1][0], corridor[-1][1]] = '+'

                    elif len(dir_sequence) == 3:
                        if dir_sequence[0] == 'S':
                            self.connect_horizontal(n1.room, n2.room, pts1[left], pts2[right])
                        else:
                            self.connect_vertical(n1.room, n2.room, pts1[left], pts2[right])

                    ctr += 1


    def calc_corridor(self, x1, x2, y1, y2, axis='vertical'):
        ''' 3 pt corridor'''
        pts = [[y1,x1]]

        # straight corridor
        if x1 == x2: 
            while pts[-1][0] != y2:
                add = 1
                if y2  - y1 < 0: add = -1
                pts.append( [pts[-1][0] + add, pts[-1][1]] )
        elif y1 == y2:
            while pts[-1][1] != x2:
                add = 1
                if x2  - x1 < 0: add = -1
                pts.append( [pts[-1][0] , pts[-1][1] + add] )

        else:
            # segment 1
            dx = x2 - x1
            dy = y2 - y1
            if axis == 'horizontal':
                pt1 = [ y1, x1 + dx//2 ]
                pt2 = [ y2, x1 + dx//2 ]
            else:
                pt1 = [ y1 + dy//2, x1 ]
                pt2 = [ y1 + dy//2, x2 ]
            pts.extend(self.calc_corridor(x1, pt1[1], y1, pt1[0]))
            pts.extend(self.calc_corridor(pt1[1], pt2[1], pt1[0], pt2[0]))
            pts.extend(self.calc_corridor(pt2[1], x2, pt2[0], y2))

        return pts
        


    def __repr__(self):
        return str(self.grid)

if __name__ == "__main__":
    D = dungeon()
    print (D)
