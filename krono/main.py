import argparse
import datetime
import os
from cli import CLI
from helpers import datetime_to_string
from log import Log


#if __name__ == "__main__":
def main():
    default_file = "krono.sqlite"

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--interactive", action="store_true")
    ap.add_argument("-f", "--file", default=default_file)
    ap.add_argument("-p", "--project", default="")
    ap.add_argument("-n", "--notes", default="")
    ap.add_argument("-t", "--tags", default="")
    ap.add_argument("-a", "--autosave", default=60)
    args = vars(ap.parse_args())

    filepath = os.path.abspath(args["file"])

    if args["interactive"]:
        CLI().cmdloop()
    else:
        log = Log()
        if not os.path.isfile(filepath):
            print("[INFO] Creating database file {}...".format(filepath))
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
        input("[INFO] New session started. Press any key to stop.")
