import curses

class InteractiveList:
    """
    Class to present a list of items that the user can scroll through and
    potentially select, with the selection(s) being returned to the caller.
    """

    def __init__(self, strings, select_mode="off"):
        """
        @param strings List of strings (items) to display--one per row.
        @param select_mode String indicating whether items can be selected:
            "multi": select any number of items using select boxes, with an
                empty box ("[ ]") next to unselected items and a starred
                box ("[*]") next to selected items.
            "single_box": same as "multi" but only a single item can be selected
                (marked by "[*]" instead of "[ ]") at a time.
            "single": select a single box by navigating to it and pressing Enter.
            "off": functionally same as "single"--different instructions shown.
        """

        self.select_mode = select_mode.lower()

        if self.select_mode == "off":
            self.instructions = "Up [Up/k], Down [Down/j], Done [Enter/q]"
            self.strings = list(strings)
        elif self.select_mode == "single":
            self.instructions = "Up [Up/k], Down [Down/j], Select [Enter], Quit [q]"
            self.strings = list(strings)
        else:
            self.instructions = "Up [Up/k], Down [Down/j], Select [Space]"\
                ", Done [Enter], Quit [q]"
            self.strings = ["[ ] " + string for string in strings]
        
        if self.select_mode == "multi":
            self.selected = []
        else:
            self.selected = None

        self.base = None
        self.height = None
        self.width = None

    def start(self):
        try:
            self.base = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            self._interactive_list()
            self.base = None
        finally:
            curses.flushinp()
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
        return self.selected

    def _interactive_list(self):
        base_height, base_width = self.base.getmaxyx()
        self.base.addstr(base_height - 1, 1, self.instructions)
        self.base.refresh()

        scr = curses.newwin(base_height - 2, base_width, 0, 0)
        scr.keypad(True)
        scr.scrollok(True)

        self.height, self.width = scr.getmaxyx()
        self._reprint(scr, 0)
        scr.addstr(0, 0, self.strings[0], curses.A_REVERSE)

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
                    self._reprint(scr, line)
                    scr.addstr(0, 0, self.strings[line], curses.A_REVERSE)
            elif (key == curses.KEY_DOWN or key == ord("j")) and line < len(self.strings) - 1:
                if y < self.height - 1:
                    scr.addstr(y, 0, self.strings[line])
                    line += 1
                    scr.move(y+1, 0)
                    scr.addstr(y+1, 0, self.strings[line], curses.A_REVERSE)
                else:
                    scr.addstr(y, 0, self.strings[line])
                    scr.addstr("\n")
                    line += 1
                    scr.addstr(self.strings[line], curses.A_REVERSE)
            elif key == ord(" ") and self.select_mode in ("multi", "single_box"):
                # If multiselect enabled, toggle selection and add or remove
                # entry from self.selected list as necessary. If single_box
                # select enabled, toggle selection and update selected index.
                if self.select_mode == "multi":
                    if line not in self.selected:
                        self.selected.append(line)
                        self._toggle_string(line, True)
                    else:
                        self.selected.remove(line)
                        self._toggle_string(line, False)
                else:
                    # If single_box select enabled.
                    if self.selected is None:
                        self._toggle_string(line, True)
                        self.selected = line
                    elif self.selected == line:
                        self._toggle_string(line, False)
                        self.selected = None
                    else:
                        self._toggle_string(self.selected, False)
                        self._toggle_string(line, True)

                        # Determine the distance of the previously selected
                        # item from the currently selected item (i.e., index
                        # of previously selected item minus the index of the
                        # current line). A negative distance means the previous
                        # item precedes the current line. A positive distance
                        # means the previously selected item comes later in the
                        # list than the current line.
                        distance = self.selected - line

                        # If distance is outside the bounds of the window, do
                        # nothing. Else, reprint the previously selected item
                        # to reflect that it is no longer selected.
                        if 0 <= y + distance < self.height:
                            scr.addstr(y + distance, 0, self.strings[self.selected])

                        # Update self.selected to reflect new selection.
                        self.selected = line

                # Reprint the current line with the select-box marked.
                scr.addstr(y, 0, self.strings[line], curses.A_REVERSE)
            elif key == ord("q"):
                self.selected = None
                break
            elif key == ord("\n"):
                break

        self.base.erase()
        scr.erase()
        del scr

    def _reprint(self, scr, first_line):
        """
        Erase and reprint the entire curses window, beginning with "first_line"
        (the index in "strings" corresponding to the first line of the window).
        """

        i = first_line
        y = 0
        while i < len(self.strings) and y < self.height:
            scr.clrtoeol()
            scr.addstr(y, 0, self.strings[i])
            i += 1
            y += 1
        scr.move(0, 0)

    def _toggle_string(self, line, select):
        """
        @brief Modify the string at index @param line to mark as
            selected or unselected.

        @param line The index corresponding to the line in self.strings.
        @param select Whether to select (True) or unselect (False).
        """

        if select:
            self.strings[line] = "[*] " + self.strings[line][4:]
        else:
            self.strings[line] = "[ ] " + self.strings[line][4:]
