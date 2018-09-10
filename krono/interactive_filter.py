from collections import OrderedDict
import curses

class InteractiveFilter:
    def __init__(self):
        self.filters = OrderedDict([
            ("start", list("0000-01-01 00:00:00")),
            ("end", list("9999-12-31 23:59:59")),
            ("project", list("placeholder")),
            ("tags", list("")),
            ("notes", list(""))
            ])

        self.dict_keys = list(self.filters.keys())
        self.num_dict_keys = len(self.dict_keys)

        self.scr = None

    def _interactive_filter(self):
        scr = self.scr
        scr_height, scr_width = scr.getmaxyx()
        scr.refresh()
        scr.keypad(True)

        min_x = 10
        date_separator_idx = [min_x + i for i, c in enumerate(self.filters["start"])
                              if c in ("-", " ", ":")]
        date_len = len(self.filters["start"])

        def refresh_line(line_idx):
            dict_key = self.dict_keys[line_idx]
            text = "{:<8}| {}".format(dict_key, "".join(self.filters[dict_key]))
            scr.move(line_idx, 0)
            scr.clrtoeol()
            scr.addstr(line_idx, 0, text)
            scr.move(line, x)

        def date_move_right():
            if x + 1 in date_separator_idx:
                scr.move(line, x + 2)
            elif x < min_x + date_len - 1:
                scr.move(line, x + 1)
        
        def date_move_left():
            if x - 1 in date_separator_idx:
                scr.move(line, x - 2)
            elif x > min_x:
                scr.move(line, x - 1)

        def move_right():
            dict_key = self.dict_keys[line]
            if x < min_x + len(self.filters[dict_key]):
                scr.move(line, x + 1)

        def move_left():
            dict_key = self.dict_keys[line]
            if x > min_x:
                scr.move(line, x - 1)

        line = 0
        x = min_x
        for i in range(self.num_dict_keys):
            refresh_line(i)

        while True:
            key = scr.getch()
            y, x = scr.getyx()

            if key == curses.KEY_UP and line > 0:
                line -= 1
                scr.move(line, min_x)
            elif key == curses.KEY_DOWN and line < self.num_dict_keys - 1:
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
                    del self.filters[dict_key][x - min_x - 1]
                    refresh_line(line)
                    move_left()
                else:
                    date_move_left()
            elif line <= 1 and ord("0") <= key <= ord("9"):
                dict_key = self.dict_keys[line]
                self.filters[dict_key][x - min_x] = chr(key)
                refresh_line(line)
                date_move_right()
            elif line > 1 and 32 <= key <= 126:
                dict_key = self.dict_keys[line]
                if x - min_x < len(self.filters[dict_key]):
                    self.filters[dict_key][x - min_x] = chr(key)
                else:
                    self.filters[dict_key].append(chr(key))
                refresh_line(line)
                move_right()
            elif key == ord("\n"):
                break

        scr.erase()

    def start(self):
        try:
            self.scr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(2)
            self._interactive_filter()
            self.scr = None
        finally:
            curses.flushinp()
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
        for dict_key in self.filters:
            self.filters[dict_key] = "".join(self.filters[dict_key])
        return dict(self.filters)
