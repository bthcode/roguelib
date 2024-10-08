import curses
import grid

arrow_offsets = {
    curses.KEY_DOWN: (0, 1),
    curses.KEY_RIGHT: (1, 0),
    curses.KEY_LEFT: (-1, 0),
    curses.KEY_UP: (0, -1),
}


class Subwin:
    def __init__(self, start_x, start_y, width, height):
        pass

class GameUI():
    def __init__(self, scr):
        self.init_ui(scr)

    def init_ui(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.clear()
        self.screen = stdscr  # FIXME
        self.screen.refresh()

        curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.stdscr.keypad(1)
        #self.stdscr.nodelay(1)
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Layout
        self.height, self.width = self.stdscr.getmaxyx()
        self.msg_height = 3
        self.status_width = 20
        self.game_height = self.height - self.msg_height
        self.status_height = self.game_height
        self.game_width = self.width - self.status_width
        self.game_start_y = self.msg_height
        self.game_start_x = self.status_width
        
        # Windows
        self.msg_win = curses.newwin(self.msg_height, self.width, 0, 0)
        self.msg_win.box()
        self.msg_win.refresh()

        self.game_win = curses.newwin(
            self.game_height, self.game_width, self.msg_height, self.status_width)
        #self.game_win.box()
        self.game_win.refresh()

        self.status_win = curses.newwin(
            self.status_height, self.status_width, self.msg_height, 0)
        self.status_win.box()
        self.status_win.refresh()

        self.pad_height = self.game_height + 10
        self.pad_width = self.game_width + 10
        self.pad_ul_x = 0
        self.pad_ul_y = 0
        self.pad = curses.newpad(self.pad_height+1, self.pad_width+1)
        curses.doupdate()
        self.pad.touchwin()
        self.clear()

    def clear(self):
        self.chars = [[" "] * self.width for i in range(self.height)]
        self.cursor = [0, 0]
        self.pad.clear()
        self.pad.refresh(0, 0,
                         self.game_start_y, self.game_start_x,
                         self.game_height, self.game_width)
        for win in [self.msg_win, self.status_win]:  # , self.stats_win ]:
            win.refresh()
        self.screen.refresh()

    def clearline(self, lines, win):
        "Clear one or more lines."
        try:
            for line in lines:
                self.addstr(line, 0, ' ' * self.width, win, c_white)
        except TypeError:
            self.addstr(lines, 0, ' ' * self.width, win, c_white)

    def PutChar(self, loc:grid.GridLocation, ch, attr):
        y, x = loc
        if 1 and attr == 'BOLD':
            self.pad.addstr(y, x, ch, curses.color_pair(3))
        else:
            self.pad.addstr(y, x, ch, curses.color_pair(1))

    def refresh(self):
        self.msg_win.touchwin()
        self.msg_win.refresh()
        self.status_win.touchwin()
        self.status_win.refresh()
        self.move(0, 0)
        self.pad.touchwin()
        self.stdscr.refresh()

    def get_input(self):
        return self.screen.getch()

    def center_on(self, loc:grid.GridLocation):
        y, x = loc
        # does the screen need to move?
        screen_min_x = self.pad_ul_x
        screen_max_x = self.pad_ul_x + self.game_width-1
        screen_min_y = self.pad_ul_y 
        screen_max_y = self.pad_ul_y + self.game_height-1

        if x < screen_min_x + 10:
            self.pad_ul_x = max(self.pad_ul_x - self.game_width//2, 0)
        if x > screen_max_x - 10:
            self.pad_ul_x = min(self.pad_width-self.game_width+1, self.pad_ul_x + self.game_width//2)
        if y < screen_min_y + 10:
            self.pad_ul_y = max(self.pad_ul_y - self.game_height//2, 0)
        if y > screen_max_y - 10:
            self.pad_ul_y = min(self.pad_height-self.game_height+1, self.pad_ul_y + self.game_height//2)

        self.pad.refresh(self.pad_ul_y, self.pad_ul_x,
           self.game_start_y, self.game_start_x,
           self.game_start_y + self.game_height-1,
           self.game_start_x + self.game_width-1)
        curses.doupdate()
        self.pad.touchwin()

#----------------------------------------------------------------
# NOTES:
#   1. BUG - can't write to last pos in pad
#   2. need to differentiate between background and foreground
#       - restore the background on move
#       - GameEngine::get_tile()
#   3. where does the game engine live?
#       - UI Has a game engine
#---------------------------------------------------------------- 

import dungeon_gen
import fov
import random
import astar
import grid

class PlayerCharacter:
    def __init__(self):
        self.loc:grid.Location = (0,0)

class Monster:
    def __init__(self):
        self.loc:grid.Location = (0,0)
        self.symbol = 'A'
        self.cost_dict = { '.' : 1.0, '#' : 99, '+' : 0 }
        self.impassable_list = ['#', '+']

    def get_path(self, G: grid.Grid, goal: grid.Location):
        
        came_from, path_so_far = astar.a_star_search( self.cost_dict,
                                                      self.impassable_list,
                                                      G,
                                                      self.loc,
                                                      goal, max_length=999)
        path = astar.reconstruct_path(came_from, start=self.loc, goal=goal)

        return path


class GameEngine:
    def __init__(self, width, height):
        self.MAP = dungeon_gen.DungeonGenerator(width-1, height-1)
        self.PC  = PlayerCharacter()
        pc_loc = self.find_empty_square()
        self.PC.loc = pc_loc
        self.FOV = fov.FOVMap(self.MAP.grid.width,
                              self.MAP.grid.height,
                              self.BlocksVision)
        
        # TEST
        sample_monster = Monster()
        while True:
            x = random.randint(max(0,self.PC.loc[1] - 30), min(self.PC.loc[1] + 30, self.MAP.grid.width-2))
            y = random.randint(max(0,self.PC.loc[0] - 30), min(self.PC.loc[0] + 30, self.MAP.grid.height-2))
            if self.MAP.grid[y,x] in ['.', ' ']:
                break
        sample_monster.loc = (y,x)
        
        self.monsters = [sample_monster]

    def BlocksVision(self, x, y):
        return self.MAP.grid[y,x] in ['+', '#']

    def PathfindPass(self, x, y):
        return self.MAP.grid[y,x] in ['.', ' ', '+']

    def find_empty_square(self):
        while True:
            x = random.randint(1, self.MAP.grid.width-1)
            y = random.randint(1, self.MAP.grid.height-1)
            if self.MAP.grid[y,x] in ['.', ' ']:
                return y,x

    def get_tile(self, y, x):
        return self.MAP.grid[y,x]

    def move_monster(self, monster_idx):
        monster = self.monsters[monster_idx]
        path = monster.get_path( self.MAP.grid, self.PC.loc) #self.PC.y, self.PC.x, self.PathfindPass)
        old_pos = monster.loc
        if path:
            dx, dy = path[0][1] - monster.loc[1], path[0][0] - monster.loc[0]
            new_pos = ( monster.loc[0] + dy, monster.loc[1] + dx )
            tile = self.MAP.grid[new_pos]
            if tile in monster.impassable_list: 
                return old_pos, old_pos
            elif new_pos[0] == self.PC.loc[0] and new_pos[1] == self.PC.loc[1]:
                return old_pos, old_pos
            else: 
                monster.loc = new_pos
                return old_pos, new_pos 
        else:
            return old_pos, old_pos

    def move_pc(self, direction):
        new_x =  min(max(0,self.PC.loc[1] + direction[0]), self.MAP.grid.width-1)
        new_y = min(max(0,self.PC.loc[0] + direction[1]), self.MAP.grid.height-1)

        old_y, old_x = self.PC.loc

        moved = False
        if self.MAP.grid[(new_y, new_x)] not in [' ', '.', '+']:
            pass
        else:
            self.PC.loc = (new_y, new_x)
            moved = True
        return self.PC.loc[0], self.PC.loc[1], old_y, old_x, moved

    def calc_fov(self, loc):
        new_fov = set()
        y, x = loc
        for i, j in self.FOV.Ball(x, y, 2):
            distance_squared = (i - x) ** 2 + (j - y) ** 2
            if distance_squared <= 3**2:
                new_fov.add((i, j))
            new_fov.add((i,j))
        return new_fov

#@profile
def main(stdscr):
    import random
    UI = GameUI(stdscr)
    Engine = GameEngine(UI.pad_width, UI.pad_height)
    
    for y in range(Engine.MAP.height):
        for x in range(Engine.MAP.width):
            UI.PutChar((y,x),Engine.MAP.grid[y,x], curses.color_pair(1))


    fov = Engine.calc_fov(Engine.PC.loc)
    for pt in fov:
        UI.PutChar((pt[1], pt[0]), Engine.MAP.grid[pt[1], pt[0]], 'BOLD')

    UI.PutChar(Engine.PC.loc, '@', 'BOLD')
    UI.center_on(Engine.PC.loc)

    for idx, monster in enumerate(Engine.monsters):
        UI.PutChar(monster.loc, monster.symbol, 'BOLD')

    while True:
        keypress = UI.get_input()
        if keypress in arrow_offsets:

            new_y, new_x, old_y, old_x, moved = Engine.move_pc(arrow_offsets[keypress])

            if moved:
                # clear old position
                UI.PutChar((old_y, old_x), Engine.MAP.grid[old_y, old_x], 'X')


                #---------------------------------------------------
                # FOV Example
                #---------------------------------------------------
                new_fov = Engine.calc_fov(Engine.PC.loc)

                for pt in fov ^ new_fov:
                    UI.PutChar((pt[1], pt[0]), Engine.MAP.grid[pt[1], pt[0]], '')

                for pt in new_fov:
                    UI.PutChar((pt[1], pt[0]), Engine.MAP.grid[pt[1], pt[0]], 'BOLD')

                UI.PutChar((new_y, new_x), '@', 'BOLD')

                fov = new_fov

                #-------------------------------------------------
                # Move Monsters
                #-------------------------------------------------
                for idx, monster in enumerate(Engine.monsters):
                    old_pos, new_pos = Engine.move_monster(0) 
                    UI.PutChar(old_pos, Engine.MAP.grid[old_pos[0], old_pos[1]], 'BOLD')
                    UI.PutChar(monster.loc, monster.symbol, 'BOLD')
                        

                # Does the update
                UI.center_on((new_y, new_x))

        elif keypress in [ord('q'),ord('Q')]:
            return
        else:
            return


if __name__ == "__main__":
    curses.wrapper(main)
