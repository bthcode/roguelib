class Grid:
    def __init__(self, height: int, width: int, val : str = '#' ):
        self.height : int = height
        self.width : int = width
        self.data = []
        for i in range(height):
            self.data.append([val] * width)
    def __setitem__(self, row_col, val):
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
        row, col = row_col
        if isinstance(row, slice) and isinstance(col, slice):
            rows = self.data[row]
            arr = [ x[col] for x in rows ]
            G = Grid(len(arr), len(arr[0]))
            G.data = arr
            return G
        elif isinstance(row, slice):
            rows = self.data[row]
            arr = [ x[col] for x in rows ]
            G = Grid(len(arr), len(arr[0]))
            G.data = [arr]
            return G
        elif isinstance(col, slice):
            arr = self.data[row][col]
            G = Grid(1, len(arr))
            G.data = [arr]
            return G
        else:
            return self.data[row][col]
    def __str__(self):
        return "\n".join(["".join(row) for row in self.data])
    def contains(self, vals):
        found = False
        for v in vals:
            for row in self.data:
                if v in row:
                    return True
        return False

if __name__ == "__main__":
    G = Grid(5,6, '#')
    print ('Orig:')
    print (G)
    print ('Set val')
    G[0,0] = 'b'
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

