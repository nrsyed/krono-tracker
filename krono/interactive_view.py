import curses

class InteractiveView:
    def __init__(self, strings):
        self.strings = ["[ ] " + string for string in strings]
        self.instructions = "Up: [Up/k], Down [Down/j], Select: [Space], Quit: [q]"
        self.selection = []

    def start(self):
        self._curses_wrapper()
        return self.selection
        
    def _interactive_log(self, base):
        base_height, base_width = base.getmaxyx()
        base.addstr(base_height - 1, 1, self.instructions)
        base.refresh()

        scr = curses.newwin(base_height - 2, base_width, 0, 0)
        scr.keypad(True)
        scr.scrollok(True)

        height, width = scr.getmaxyx()
        self._reprint(scr, 0, height)

        line = 0
        while True:
            key = scr.getch()
            y, _ = scr.getyx()
            if (key == curses.KEY_UP or key == ord("k")) and line > 0:
                if y > 0:
                    scr.addstr(y, 0, self.strings[line])
                    line -= 1
                    scr.move(y-1, 0)
                    scr.addstr(y-1, 0, self.strings[line], curses.A_REVERSE)
                else:
                    line -= 1
                    self._reprint(scr, line, height)
            elif (key == curses.KEY_DOWN or key == ord("j")) and line < len(self.strings) - 1:
                if y < height - 1:
                    scr.addstr(y, 0, self.strings[line])
                    line += 1
                    scr.move(y+1, 0)
                    scr.addstr(y+1, 0, self.strings[line], curses.A_REVERSE)
                else:
                    scr.addstr(y, 0, self.strings[line])
                    scr.addstr("\n")
                    line += 1
                    scr.addstr(self.strings[line], curses.A_REVERSE)
            elif key == ord(" "):
                # Toggle line selection.
                if line not in self.selection:
                    self.selection.append(line)
                    self.strings[line] = "[*] " + self.strings[line][4:]
                else:
                    self.selection.remove(line)
                    self.strings[line] = "[ ] " + self.strings[line][4:]
                scr.addstr(y, 0, self.strings[line], curses.A_REVERSE)
            elif key == ord("q"):
                break

        base.erase()
        scr.erase()
        del scr

    def _reprint(self, scr, line, height):
        """
        Erase and reprint the entire curses window, beginning with "line"
        (the index in "strings" corresponding to the first line of the window).
        """
        scr.clrtoeol()
        scr.addstr(0, 0, self.strings[line], curses.A_REVERSE)
        i = line + 1
        y = 1
        while i < len(self.strings) and y < height:
            scr.clrtoeol()
            scr.addstr(y, 0, self.strings[i])
            i += 1
            y += 1
        scr.move(0, 0)

    def _curses_wrapper(self):
        try:
            base = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            self._interactive_log(base)
            del base
        finally:
            curses.flushinp()
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
