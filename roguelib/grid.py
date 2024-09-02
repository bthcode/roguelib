from typing import Protocol, Iterator, Tuple, TypeVar, Optional, Iterable
T = TypeVar('T')

Location = TypeVar('Location')
GridLocation = Tuple[int, int]

class Grid:
    def __init__(self, height: int, width: int, val : str = '#' ):
        self.height : int = height
        self.width : int = width
        self.data = []
        for i in range(height):
            self.data.append([val] * width)
    def __setitem__(self, row_col, val : str):
        row, col = row_col
        if isinstance(row, slice):
            for r in range(row.start, row.stop):
                if isinstance(col, slice):
                    for c in range(col.start, col.stop):
                        self.data[r][c] = val
                else:
                    self.data[r][col] = val
        else:
            if isinstance(col, slice):
                for c in range(col.start, col.stop):
                    self.data[row][c] = val
            else:
                self.data[row][col] = val
    def __getitem__(self, row_col):
        ''' NOTE: Base interface to allow slices, etc '''
        row, col = row_col

        # Double Slice
        if isinstance(row, slice) and isinstance(col, slice):
            rows = self.data[row]
            arr = [ x[col] for x in rows ]
            G = Grid(len(arr), len(arr[0]))
            G.data = arr
            return G
        # Row Slice
        elif isinstance(row, slice):
            rows = self.data[row]
            arr = [ x[col] for x in rows ]
            G = Grid(len(arr), len(arr[0]))
            G.data = [arr]
            return G
        # Col Slice
        elif isinstance(col, slice):
            arr = self.data[row][col]
            G = Grid(1, len(arr))
            G.data = [arr]
            return G
        # Single tile accessor
        else:
            return self.data[row][col]

    def __str__(self):
        return "\n".join(["".join(row) for row in self.data])

    def get_tile(self, loc:GridLocation):
        ''' Primary means of fetching a tile '''
        row, col = loc
        if not self.in_bounds(loc):
            raise ValueError("Loc out of bounds")
        return self.data[row][col]

    def contains(self, vals: Iterable[str]) -> bool:
        ''' Does this grid contain anything in vals?  '''
        found = False
        for v in vals:
            for row in self.data:
                if v in row:
                    return True
        return False

    def in_bounds(self, loc: GridLocation) -> bool:
        ''' Is this loc in the grid? '''
        (y, x) = loc
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, loc: GridLocation, passable_list) -> bool:
        ''' Is this loc passable? '''
        return self.get_tile(loc) in passable_list

    def cost(self, loc: GridLocation) -> [bool, float]:
        return 1.0
    
    def neighbors(self, loc: GridLocation) -> Iterator[GridLocation]:
        ''' What are the in-bounds neighbords of this loc? '''
        (y, x) = loc
        neighbors = [(y, x+1), (y-1, x+1), (y-1, x), (y-1, x-1),
                     (y, x-1), (y+1, x-1), (y+1, x), (y+1, x+1) ]
        # see "Ugly paths" section for an explanation:
        if (x + y) % 2 == 0: neighbors.reverse() # S N W E
        results = filter(self.in_bounds, neighbors)
        #results = filter(self.passable, results, passable_list)
        return results


if __name__ == "__main__":
    G = Grid(5,6, '#')
    print ('Orig:')
    print (G)
    print ('Set val')
    G[(0,0)] = 'b'
    print (G)
    print ('\nSingle row, col slice')
    G[1,2:5] = 'c'
    print (G)
    print ('\nSet val for Row slice, col slice')
    G[2:4,2:4] = 'a'
    print (G)
    print ('\nFetch rectangular slice')
    print (G[2:4,3:5])

    print ('\nFetch col slice')
    print (G[2,2:4])

    print ('\nFetch row slice')
    print (G[0:4,0])

    print (f"G contains b: {G.contains(['b'])}")
    print (f"G contains x: {G.contains(['x'])}")

    print (f"G[2:4,2:4].contains['a']: {G[2:4,2:4].contains(['a'])}")
    print (f"G[2:4,2:4].contains['#']: {G[2:4,2:4].contains(['#'])}")

    print (f'G.in_bound((3,3)) = {G.in_bounds((3,3))}')
    print (f'G.in_bound((10,3)) = {G.in_bounds((10,3))}')

    print (f'G.neighbors((2,2)) = {list(G.neighbors((2,2)))}')
    
    print (f'G.get_tile((3,3)) = {G.get_tile((3,3))}')
