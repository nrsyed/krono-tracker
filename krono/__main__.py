from __future__ import print_function
import argparse
import datetime
import os
import sys
from cli import CLI
from helpers import datetime_to_string
from interactive_list import InteractiveList
from log import Log
from session import Session


def main():
    default_file = "krono.sqlite"

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--autosave", default=60)
    ap.add_argument("-f", "--file", default=default_file)
    ap.add_argument("-i", "--interactive", action="store_true")
    ap.add_argument("-p", "--project", default="")
    ap.add_argument("-n", "--notes", default="")
    ap.add_argument("-t", "--tags", default="")
    ap.add_argument("-v", "--view", action="store_true")
    args = vars(ap.parse_args())

    filepath = os.path.abspath(args["file"])

    if args["interactive"]:
        CLI().cmdloop()
    elif args["view"]:
        if not os.path.isfile(filepath):
            print("[ERROR] The database at {} does not exist.".format(filepath))
        else:
            log = Log()
            log.load_db(filepath)
            log.select_all()
            formatted_rows = log.format_selected()
            if formatted_rows:
                InteractiveList(formatted_rows, select_mode="off").start()
            log.unload_db
    else:
        log = Log()
        if not os.path.isfile(filepath):
            print("[INFO] Creating database file {}".format(filepath))
            db_created = log.create_db(filepath)
            if db_created:
                print("[INFO] Database created.")
            else:
                print("[ERROR] Database could not be created.")
        else:
            log.load_db(filepath)

        start_time = datetime.datetime.now()
        log.add_row(
            start=datetime_to_string(start_time), project=args["project"],
            tags=args["tags"], notes=args["notes"])

        last_row_id = log.get_last_row_id()
        sess = Session(log, last_row_id, autosave_interval=args["autosave"])
        sess.start()

        if sys.version_info.major < 3:
            raw_input("[INFO] New session started. Press Enter to stop.")
        else:
            input("[INFO] New session started. Press Enter to stop.")
        current_datetime = datetime_to_string(datetime.datetime.now())
        log.update_row(last_row_id, end=current_datetime)
        log.unload_db()

if __name__ == "__main__":
    main()
