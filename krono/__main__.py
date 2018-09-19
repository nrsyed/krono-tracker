from __future__ import print_function
import argparse
import datetime
import logging
import os
import sys
from cli import CLI
from helpers import datetime_to_string
from log import Log
from session import Session

# NOTE: The builtin logging module is not to be confused with the custom Log
# class in the log module of this package, which provides functionality for
# interfacing with a Krono Tracker event log sqlite file.

def main():
    logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s] %(message)s")

    default_file = "krono.sqlite"

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--autosave", default=60, type=int)
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
            logging.error("The database at {} does not exist.".format(filepath))
        else:
            log = Log()
            log.load_db(filepath)
            log.select_all()
            log.view()
            log.unload_db()
    else:
        log = Log()
        if not os.path.isfile(filepath):
            logging.info("Creating database file {}".format(filepath))
            db_created = log.create_db(filepath)
            if db_created:
                logging.info("Database created.")
            else:
                logging.error("Database could not be created.")
        else:
            logging.info("Loading database {}".format(filepath))
            if (log.load_db(filepath)):
                logging.info("Database loaded.")
            else:
                logging.error("Database could not be loaded.")
                return 1

        start_time = datetime.datetime.now()
        log.add_row({
                "start": datetime_to_string(start_time),
                "project": args["project"],
                "tags": args["tags"],
                "notes": args["notes"]})

        last_row_id = log.get_last_row_id()
        sess = Session(log, last_row_id, autosave_interval=args["autosave"])
        sess.start()

        if sys.version_info.major < 3:
            raw_input("[INFO] New session started. Press Enter to stop.")
        else:
            input("[INFO] New session started. Press Enter to stop.")
        current_datetime = datetime_to_string(datetime.datetime.now())
        log.update_row(last_row_id, {"end": current_datetime})
        log.unload_db()

if __name__ == "__main__":
    main()
