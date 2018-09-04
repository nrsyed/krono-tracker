import threading
from helpers import datetime_to_string

class Session(threading.Thread):
    def __init__(self, log, last_row_id, autosave_interval=60):
        self.log = log
        self.last_row_id = last_row_id
        self.autosave_interval = autosave_interval
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        while True:
            time.sleep(self.autosave_interval)
            current_datetime = datetime_to_string(datetime.datetime.now())
            self.log.update_row(self.last_row_id, end=current_datetime)
