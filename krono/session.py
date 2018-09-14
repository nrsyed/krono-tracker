import datetime
import sys
import threading
import time
from helpers import datetime_to_string

class Session(threading.Thread):
    def __init__(self, log, last_row_id, autosave_interval=60):
        self.log = log
        self.last_row_id = last_row_id
        self.autosave_interval = autosave_interval

        py_version = sys.version_info
        if py_version.major >= 3 and py_version.minor >= 3:
            threading.Thread.__init__(self, daemon=True)
        else:
            threading.Thread.__init__(self)
            self.daemon = True

    def run(self):
        while True:
            time.sleep(self.autosave_interval)
            current_datetime = datetime_to_string(datetime.datetime.now())
            self.log.update_row(self.last_row_id, {"end": current_datetime})
