from __future__ import print_function
import cmd
import logging
import os
import subprocess
from helpers import clear
from log import Log

class CLI(cmd.Cmd):
    def __init__(self):
        self.intro = "Krono Tracker.\nType help or ? to list commands.\n"
        self.prompt = "(krono) "
        self.path = os.getcwd()
        self.log = None
        cmd.Cmd.__init__(self)

    @property
    def log_loaded(self):
        return bool(self.log)

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

        new_path = os.path.join(self.path, arg)
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
            return

        logging.info("Creating database file {}".format(filepath))
        try:
            Log().create_db(filepath)
        except Exception as e:
            logging.error(e)

    def do_delete(self, arg):
        """
        Delete entries from the currently loaded log.
        """

        if self.log_loaded:
            self.log.delete_entries()

    def do_exit(self, arg):
        """
        Exit Krono Tracker.
        """

        return True

    def do_filter(self, arg):
        """
        Select criteria to filter entries.
        """

        if self.log_loaded:
            self.log.modify_filter()

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
            logging.error("No filename entered.")
            return

        filepath = os.path.normpath(os.path.join(self.path, arg))

        try:
            if self.log_loaded:
                self.log.unload_db()
            else:
                self.log = Log()

            self.log.load_db(filepath)
            self.log.select_all()
        except Exception as e:
            logging.error(e)

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
        print(self.path)

    def do_view(self, arg):
        """
        View the currently loaded log file.
        """

        if self.log_loaded:
            self.log.view()
