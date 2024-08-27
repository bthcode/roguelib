import curses

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

    def PutChar(self, y, x, ch, attr):
        if 1 and attr == 'BOLD':
            self.pad.addstr(y, x, ch, curses.color_pair(2))
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

    def center_on(self, y, x):
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
class PlayerCharacter:
    def __init__(self):
        self.x = 0
        self.y = 0

class GameEngine:
    def __init__(self, width, height):
        self.MAP = dungeon_gen.DungeonGenerator(width-1, height-1)
        self.PC  = PlayerCharacter()
        pc_loc = self.find_empty_square()
        self.PC.y = pc_loc[0]
        self.PC.x = pc_loc[1]
        self.FOV = fov.FOVMap(self.MAP.grid.width,
                              self.MAP.grid.height,
                              self.BlocksVision)

    def BlocksVision(self, x, y):
        return self.MAP.grid[y,x] in ['+', '#']

    def find_empty_square(self):
        while True:
            x = random.randint(1, self.MAP.grid.width-1)
            y = random.randint(1, self.MAP.grid.height-1)
            if self.MAP.grid[y,x] in ['.', ' ']:
                return y,x

    def get_tile(self, y, x):
        return self.MAP.grid[y,x]

    def move_pc(self, direction):
        new_x =  min(max(0,self.PC.x + direction[0]), self.MAP.grid.width-1)
        new_y = min(max(0,self.PC.y + direction[1]), self.MAP.grid.height-1)

        old_y = self.PC.y 
        old_x = self.PC.x

        moved = False
        if self.MAP.grid[new_y, new_x] not in [' ', '.', '+']:
            pass
        else:
            self.PC.y = new_y
            self.PC.x = new_x
            moved = True
        return self.PC.y, self.PC.x, old_y, old_x, moved

    def calc_fov(self, y, x):
        new_fov = set()
        for i, j in self.FOV.Ball(x, y, 2):
            distance_squared = (i - x) ** 2 + (j - y) ** 2
            if distance_squared <= 3**2:
                new_fov.add((i, j))
            new_fov.add((i,j))
        return new_fov

def main(stdscr):
    import random
    UI = GameUI(stdscr)
    Engine = GameEngine(UI.pad_width, UI.pad_height)
    
    for y in range(Engine.MAP.height):
        for x in range(Engine.MAP.width):
            UI.PutChar(y,x,Engine.MAP.grid[y,x], curses.color_pair(1))


    fov = Engine.calc_fov(Engine.PC.y, Engine.PC.x)
    for pt in fov:
        UI.PutChar(pt[1], pt[0], Engine.MAP.grid[pt[1], pt[0]], 'BOLD')

    UI.PutChar(Engine.PC.y, Engine.PC.x, '@', 'BOLD')
    UI.center_on(Engine.PC.y, Engine.PC.x)

    while True:
        keypress = UI.get_input()
        if keypress in arrow_offsets:

            new_y, new_x, old_y, old_x, moved = Engine.move_pc(arrow_offsets[keypress])

            if moved:
                # clear old position
                UI.PutChar(old_y, old_x, Engine.MAP.grid[old_y, old_x], 'X')


                #---------------------------------------------------
                # FOV Example
                #---------------------------------------------------
                new_fov = Engine.calc_fov(Engine.PC.y, Engine.PC.x)

                for pt in fov ^ new_fov:
                    UI.PutChar(pt[1], pt[0], Engine.MAP.grid[pt[1], pt[0]], '')

                for pt in new_fov:
                    UI.PutChar(pt[1], pt[0], Engine.MAP.grid[pt[1], pt[0]], 'BOLD')

                UI.PutChar(new_y, new_x, '@', 'BOLD')

                fov = new_fov

                # Does the update
                UI.center_on(new_y, new_x)

        elif keypress in [ord('q'),ord('Q')]:
            return
        else:
            return


if __name__ == "__main__":
    curses.wrapper(main)
