from __future__ import print_function
import cmd
import curses
import os
import subprocess
import sys
from helpers import clear
from interactive_list import InteractiveList
from log import Log

class CLI(cmd.Cmd):
    intro = "Krono Tracker.\nType help or ? to list commands.\n"
    prompt = "(krono) "
    path = os.getcwd()
    log = None

    def postcmd(self, stop, line):
        if stop:
            clear()
            return True
        else:
            print()

    def preloop(self):
        clear()
        
    def do_exit(self, arg):
        return True

    def do_load(self, arg):
        if arg == "":
            print("Error: No filename entered.")
            return

        filepath = os.path.normpath(os.path.join(self.path, arg))
        if not os.path.isfile(filepath):
            print("Error: File does not exist. Use create to make a new database.")
            return

        try:
            if self.log is None:
                self.log = Log()
            else:
                self.log.unload_db()

            self.log.load_db(filepath)
            self.log.select_all()
        except:
            print("Error: File could not be loaded.")
    
    def do_getdir(self, arg):
        """
        Get the path to the currently active directory."""
        print(self.path)

    def do_ls(self, arg):
        """
        List files in the currently active directory."""
        subprocess.call("ls " + self.path, shell=True)

    def do_setcwd(self, arg):
        """
        Set the active path to the current working directory (directory from
        which this program is running).
        """
        self.path = os.getcwd()

    def do_setdir(self, arg):
        """
        USAGE: setdir [../PATH/TO/NEW/DIRECTORY]

        Set the path for the active directory."""
        new_path = os.path.normpath(os.path.join(self.path, arg))
        if os.path.isdir(new_path):
            self.path = new_path
            print(self.path)
        else:
            print("Error: The directory {} does not exist.".format(new_path))

    def do_view(self, arg):
        """
        View the currently loaded log file.
        """
        if self.log is not None:
            formatted_rows = self.log.format_selected()
            if formatted_rows:
                InteractiveList(formatted_rows, select_mode="off").start()
            else:
                print("There are no entries in the current selection.")
        else:
            print("Error: No log file loaded.")
