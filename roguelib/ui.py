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
        self.game_win.box()
        self.game_win.refresh()

        self.status_win = curses.newwin(
            self.status_height, self.status_width, self.msg_height, 0)
        self.status_win.box()
        self.status_win.refresh()

        self.pad_height = 80
        self.pad_width = 180
        self.pad = curses.newpad(self.pad_height, self.pad_width)
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

    def fill_pad(self):
        chars = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h' ]
        for y in range(self.pad_height):
            for x in range(self.game_width):
                c = chars[((y*self.game_width)+x) % len(chars)]
                self.pad.addstr(y,x,c, curses.color_pair(1))


def main(stdscr):
    UI = GameUI(stdscr)
    chars = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h' ]
    for y in range(UI.game_height):
        for x in range(UI.game_width):
            c = chars[((y*UI.game_width)+x) % len(chars)]
            UI.chars[y][x] = c
    UI.PutChar(20,20, 'Q', curses.color_pair(2))

    ul_x = 0;
    ul_y = 0;

    UI.pad.refresh(ul_y, ul_x,
               UI.game_start_y, UI.game_start_x,
               UI.game_start_y + UI.game_height-2,
               UI.game_start_x + UI.game_width-2)
    curses.doupdate()
    UI.pad.touchwin()

    while True:
        keypress = UI.get_input()
        if keypress in arrow_offsets:
            ul_x = min(max(0,ul_x + arrow_offsets[keypress][0]), UI.pad_width-1)
            ul_y = min(max(0,ul_y + arrow_offsets[keypress][1]), UI.pad_height-1)
            #print (ul_x, ul_y, UI.pad_width, UI.pad_height)
            UI.pad.refresh(ul_y, ul_x,
               UI.game_start_y, UI.game_start_x,
               UI.game_start_y + UI.game_height-2,
               UI.game_start_x + UI.game_width-2)
            curses.doupdate()
            UI.pad.touchwin()
        elif keypress in [ord('q'),ord('Q')]:
            return
        else:
            return


if __name__ == "__main__":
    curses.wrapper(main)
