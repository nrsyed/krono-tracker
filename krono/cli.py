from __future__ import print_function
import cmd
import logging
import os
import subprocess
from helpers import clear
from log import Log

# TODO: Refactor to utilize method to check if log loaded.

class CLI(cmd.Cmd):
    def __init__(self):
        self.intro = "Krono Tracker.\nType help or ? to list commands.\n"
        self.prompt = "(krono) "
        self.path = os.getcwd()
        self.log = None
        cmd.Cmd.__init__(self)

    def emptyline(self):
        pass

    def postcmd(self, stop, line):
        if stop:
            clear()
            return True

        print()
        return False

    def preloop(self):
        clear()

    def do_cd(self, arg):
        """
        Change to the given directory.

        USAGE: setdir [../PATH/TO/NEW/DIRECTORY]
        """

        new_path = os.path.normpath(os.path.join(self.path, arg))
        if os.path.isdir(new_path):
            self.path = new_path
            print(self.path)
        else:
            logging.error("The directory {} does not exist.".format(new_path))

    def do_create(self, arg):
        """
        Create a new log file. New file is not automatically loaded.
        """

        filepath = os.path.abspath(arg)
        if arg == "":
            logging.error("No filename entered.")
        elif os.path.isfile(filepath):
            logging.error("File already exists.")
        else:
            logging.info("Creating database file {}".format(filepath))
            db_created = Log().create_db(filepath)
            if db_created:
                print("Database created.")
            else:
                print("Database could not be created.")

    def do_exit(self, arg):
        """
        Exit Krono Tracker.
        """

        return True

    def do_filter(self, arg):
        """
        Select criteria to filter entries.
        """

        if self.log is not None:
            self.log.modify_filter()
        else:
            logging.error("No log file loaded.")


    def do_getdir(self, arg):
        """
        Get the path to the currently active directory.
        """

        print(self.path)

    def do_load(self, arg):
        """
        Load an existing log file.
        """

        if arg == "":
            print("Error: No filename entered.")
            return

        filepath = os.path.normpath(os.path.join(self.path, arg))
        if not os.path.isfile(filepath):
            logging.error("File does not exist. Use create to make a new database.")
            return

        try:
            if self.log is None:
                self.log = Log()
            else:
                self.log.unload_db()

            self.log.load_db(filepath)
            self.log.select_all()
        except:
            logging.error("File could not be loaded.")

    def do_ls(self, arg):
        """
        List files in the currently active directory.
        """

        subprocess.call("ls " + self.path, shell=True)

    def do_modify(self, arg):
        """
        Modify an entry in the currently loaded log file.
        """

        if self.log_loaded:
            self.log.modify_entry()

    def do_setcwd(self, arg):
        """
        Set the active path to the current working directory
        (the directory in which you started running this program).
        """

        self.path = os.getcwd()

    def do_view(self, arg):
        """
        View the currently loaded log file.
        """

        if self.log_loaded:
            self.log.view()

    @property
    def log_loaded(self):
        if self.log is not None:
            logging.debug("Log file loaded.")
            return True
        else:
            logging.error("No log file loaded.")
            return False
