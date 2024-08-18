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

        self.colors = [curses.color_pair(0)]
        for i in range(1, 16):
            curses.init_pair(i, i % 8, 0)
            if i < 8:
                self.colors.append(curses.color_pair(i))
            else:
                self.colors.append(curses.color_pair(i) | curses.A_BOLD)

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
        self.dattr = self.colors[0]
        self.chars = [[" "] * self.width for i in range(self.height)]
        self.attrs = [[self.colors[0]] *
                      self.width for i in range(self.height)]
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
        if True or self.chars[y][x] != ch or self.attrs[y][x] != attr:
            self.pad.addstr(y, x, ch, curses.color_pair(attr))

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

def main(stdscr):
    import dungeon_gen
    import random
    UI = GameUI(stdscr)
    MAP = dungeon_gen.DungeonGenerator(UI.pad_width-1, UI.pad_height-1)
    
    for y in range(MAP.grid.height):
        for x in range(MAP.grid.width):
            UI.PutChar(y,x,MAP.grid[y,x], curses.color_pair(1))

    #-------------------------------------
    # Find an open sqare to start on
    #-------------------------------------
    this_y = 0
    this_x = 0
    while True:
        this_y = random.randint(1, MAP.grid.height-1)
        this_x = random.randint(1, MAP.grid.width-1)
        if MAP.grid[this_y, this_x] == ' ':
            break

    UI.center_on(this_y, this_x)

    while True:
        keypress = UI.get_input()
        if keypress in arrow_offsets:
            # calc no position
            new_x =  min(max(0,this_x + arrow_offsets[keypress][0]), UI.pad_width-1)
            new_y = min(max(0,this_y + arrow_offsets[keypress][1]), UI.pad_height-1)

            if MAP.grid[new_y, new_x] not in [' ', '.', '+']:
                continue

            # clear old position
            UI.PutChar(this_y, this_x, MAP.grid[this_y, this_x], curses.color_pair(1))

            this_x, this_y = new_x, new_y

            UI.PutChar(this_y, this_x, '@', curses.color_pair(1))
            UI.center_on(this_y, this_x)

        elif keypress in [ord('q'),ord('Q')]:
            return
        else:
            return


if __name__ == "__main__":
    curses.wrapper(main)
