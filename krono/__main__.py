from __future__ import print_function
import argparse
import datetime
import logging
import os
import sys
import threading
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
        # If interactive mode chosen, enter curses-based command line
        # interface via CLI class.
        CLI().cmdloop()
    elif args["view"]:
        # If view chosen, view using Log.view() curses interface.
        try:
            log = Log()
            log.load_db(filepath)
            log.select_all()
            log.view()
            log.unload_db()
        except Exception as e:
            logging.error(e)
    else:
        # Instantiate Log object. Create DB if necessary, else load existing.
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
                # TODO: Throw exception instead of return 1.
                return 1

        # Add new row to end of DB with current datetime as start time.
        start_time = datetime.datetime.now()
        log.add_row({
                "start": datetime_to_string(start_time),
                "project": args["project"],
                "tags": args["tags"],
                "notes": args["notes"]})

        # Get id of last row added. This will be used to periodically update
        # DB with new end time in Session thread, as well as at the end of
        # this function (__main__.main()).
        last_row_id = log.get_last_row_id()

        # Use lock to manage access to DB between this and Session threads.
        db_lock = threading.Lock()
        sess = Session(log, last_row_id,
                       autosave_interval=int(args["autosave"]), lock=db_lock)
        sess.start()

        logging.info("New session started. Press Enter to stop.")
        if sys.version_info.major < 3:
            raw_input()
        else:
            input()

        # Write current datetime as end time before exiting.
        current_datetime = datetime_to_string(datetime.datetime.now())
        
        try:
            db_lock.acquire()
            log.update_row(last_row_id, {"end": current_datetime})
        except Exception as e:
            logging.error(e)
        finally:
            db_lock.release()
            log.unload_db()

if __name__ == "__main__":
    main()
