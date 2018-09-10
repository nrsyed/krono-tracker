from collections import OrderedDict
import curses

class InteractiveParams:
    """
    Class to present a curses window of session parameters that can be
    modified by the user and returned to the caller.
    """

    def __init__(self, start="0000-01-01 00:00:00", end="9999-12-31 23:59:59",
                 project="", tags="", notes="", header_text=""):
        self.params = OrderedDict([
            ("start", list(start)),
            ("end", list(end)),
            ("project", list(project)),
            ("tags", list(tags)),
            ("notes", list(notes))
            ])

        self.dict_keys = list(self.params.keys())
        self.num_dict_keys = len(self.dict_keys)

        self.header_text = header_text
        self.base = None
        self.scr = None

    def start(self):
        try:
            self.base = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(2)
            self._interactive_params()
            self.base = None
        finally:
            curses.flushinp()
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
        for dict_key in self.params:
            self.params[dict_key] = "".join(self.params[dict_key])
        return dict(self.params)

    def _interactive_params(self):
        base_height, base_width = self.base.getmaxyx()
        self.base.addstr(0, 1, self.header_text)
        y_offset = 2
        instructions = "Navigation [Up/Down/Left/Right/Tab], Select [Enter], Quit [q]"
        self.base.addstr(self.num_dict_keys + y_offset + 2, 1, instructions)
        self.base.refresh()

        scr = curses.newwin(self.num_dict_keys, base_width, y_offset, 1)
        scr_height, scr_width = scr.getmaxyx()
        scr.refresh()
        scr.keypad(True)


        min_x = 10
        date_separator_idx = [min_x + i for i, c in enumerate(self.params["start"])
                              if c in ("-", " ", ":")]
        date_len = len(self.params["start"])

        def print_line(line_idx):
            dict_key = self.dict_keys[line_idx]
            text = "{:<8}| {}".format(dict_key, "".join(self.params[dict_key]))
            scr.move(line_idx, 0)
            scr.clrtoeol()
            scr.addstr(line_idx, 0, text)
            scr.move(line, x)

        def date_move_right():
            if x + 1 in date_separator_idx:
                scr.move(line, x + 2)
            elif x == min_x + date_len - 1:
                scr.move(line, min_x)
            else:
                scr.move(line, x + 1)
        
        def date_move_left():
            if x - 1 in date_separator_idx:
                scr.move(line, x - 2)
            elif x == min_x:
                scr.move(line, min_x + date_len - 1)
            else:
                scr.move(line, x - 1)

        def move_right():
            dict_key = self.dict_keys[line]
            if x < min_x + len(self.params[dict_key]):
                scr.move(line, x + 1)

        def move_left():
            dict_key = self.dict_keys[line]
            if x > min_x:
                scr.move(line, x - 1)

        line = 0
        x = min_x
        for i in range(self.num_dict_keys):
            print_line(i)

        while True:
            key = scr.getch()
            y, x = scr.getyx()

            if key == curses.KEY_UP and line > 0:
                line -= 1
                scr.move(line, min_x)
            elif key == curses.KEY_DOWN or key == ord("\t"):
                if line == self.num_dict_keys - 1:
                    line = 0
                else:
                    line += 1
                scr.move(line, min_x)
            elif key == curses.KEY_RIGHT:
                if line <= 1:
                    date_move_right()
                else:
                    move_right()
            elif key == curses.KEY_LEFT:
                if line <= 1:
                    date_move_left()
                else:
                    move_left()
            elif key == curses.KEY_BACKSPACE:
                if line > 1 and x > min_x:
                    dict_key = self.dict_keys[line]
                    del self.params[dict_key][x - min_x - 1]
                    print_line(line)
                    move_left()
                else:
                    date_move_left()
            elif line <= 1 and ord("0") <= key <= ord("9"):
                dict_key = self.dict_keys[line]
                self.params[dict_key][x - min_x] = chr(key)
                print_line(line)
                date_move_right()
            elif line > 1 and 32 <= key <= 126:
                dict_key = self.dict_keys[line]
                if x - min_x < len(self.params[dict_key]):
                    self.params[dict_key][x - min_x] = chr(key)
                else:
                    self.params[dict_key].append(chr(key))
                print_line(line)
                move_right()
            elif key == ord("\n"):
                break

        scr.erase()

if __name__ == "__main__":
    f = InteractiveParams(header_text="Modify").start()
