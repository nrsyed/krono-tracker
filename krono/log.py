import datetime
import os
import pickle
import sqlite3

class Log:
    def __init__(self):
        # SQL parameters and variables.
        self.conn = None
        self.cursor = None
        self.table = "sessions"
        #self.schema = "CREATE TABLE {} (".format(self.table)\
        self.schema = "CREATE TABLE " + self.table + " ("\
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"\
             "start TEXT,"\
             "end TEXT,"\
             "project TEXT,"\
             "tags TEXT,"\
             "notes TEXT)"

        self.indices = []
        self.sessions = None

    def create_db(self, filepath):
        try:
            self.conn = sqlite3.connect(filepath)
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.schema)
            print("{} successfully created.".format(filepath))
            return True
        except Error as e:
            return False

    def load_file(self, filepath):
        if not os.path.isfile(filepath):
            create_file = input("The sqlite database at {}".format(filepath)
                + " was not found. Create file? (y/n)\n")
            if create_file.lower() == "y":
                self.create_db(filepath)
            else:
                print("Operation canceled.")
                return False
        else:
            try:
                self.conn = sqlite3.connect(filepath)
                self.cursor = self.conn.cursor()
            except Error as e:
                return False

        # Check that the created or loaded DB has the correct table/schema.
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        # Check table name.
        if len(tables) == 0 or tables[0][0] != self.table:
            print("Error: Database does not contain correct table.")
            self.conn.close()
            self.conn = None
            self.cursor = None
            return False

        column_names = [column[1] for column in self.cursor.execute(
            "PRAGMA table_info('{}')".format(self.table)).fetchall()]

        if column_names != ["id", "start", "end", "project", "tags", "notes"]:
            print("Error: Table does not contain correct columns.")
            self.conn.close()
            self.conn = None
            self.cursor = None
            return False
            
        print("Database {} loaded.".format(filepath))
        return True

    def sessions_in_range(self, min_date=datetime.date.min,
        max_date=datetime.date.max, exclude_by="both"):
        """
        Given a list of sessions, return a list of indices of those sessions
        that fall within the given date range.

        @param sessions: List of dicts, where each dict is a session.
        @param min_date: date object representing date lower bound (inclusive).
        @param max_date: date object representing date upper bound (inclusive).
        @param exclude_by: String ("both", "start", "end") indicating whether the
            start date of a session ("start"), the end date of a session ("end"),
            or both ("both") must fall within the date range for it to be included
            in the final list.
        @return sessions_in_range: List containing only sessions within the date range.
        """

        if exclude_by == "start":
            indices_in_range = [i for i, session in enumerate(sessions) if
                min_date <= session["start_time"].date() <= max_date]
        elif exclude_by == "end":
            indices_in_range = [i for i, session in enumerate(sessions) if
                min_date <= session["end_time"].date() <= max_date]
        else:
            indices_in_range = [i for i, session in enumerate(sessions) if
                min_date <= session["start_time"].date() <= max_date
                and min_date <= session["end_time"].date() <= max_date]

        self.indices = indices_in_range
        return indices_in_range 

    @staticmethod
    def subdivide_sessions_by_date(sessions):
        """
        Check list of sessions for sessions spanning multiple days. Subdivide
        these sessions into several multiple sessions (one per day). Return
        new list.
        """
        updated_sessions = []
        q = Queue()
        for i, session in enumerate(sessions):
            q.put(session)
            while not q.empty():
                sess = q.get()
                if sess["start_time"].day != sess["end_time"].day:
                    # Get a datetime object corresponding to the beginning of the
                    # day after the session start time by adding a day and setting
                    # hour, min, sec, and usec to zero (ie, midnight).
                    next_day = ((sess["start_time"] + datetime.timedelta(days=1)
                        ).replace(hour=0, minute=0, second=0, microsecond=0))

                    # Make two copies of the current session. sess_first is the
                    # part from the start time to the end of the day. sess_next
                    # is the part from the beginning of the next day to the end_time.
                    sess_first = dict(sess)
                    sess_next = dict(sess)

                    # Set the end time of sess_first equal to beginning of next day
                    # minus one microsecond. Append to new list of sessions.
                    sess_first["end_time"] = (next_day - datetime.timedelta(microseconds=1))
                    updated_sessions.append(sess_first)

                    # Set start time of sess_next equal to beginning of next day.
                    # Add to queue.
                    sess_next["start_time"] = next_day
                    q.put(sess_next)
                else:
                    updated_sessions.append(sess)

        return updated_sessions
                
    def list_sessions(self):
        """Print a list of sessions, each separated by a newline, to terminal."""

        print("\nList of sessions in currently loaded log file:")
        for i in self.indices:
            start_str = "Start: " + self.sessions[i]["start_time"].strftime("%x, %X")
            end_str = "End: " + self.sessions[i]["end_time"].strftime("%x, %X")
            print("Session {:d}: ".format(i+1) + start_str + " | " + end_str)

    def total_time(self):
        """Return the total amount of time of all sessions."""

        total_timedelta = datetime.timedelta()
        for i in self.indices:
            total_timedelta += (
                self.sessions[i]["end_time"] - self.sessions[i]["start_time"])

        total_seconds = total_timedelta.total_seconds()
        total_time = {
            "hours": int(total_seconds // 3600),
            "minutes": int((total_seconds % 3600) // 60),
            "seconds": int(total_seconds % 60),
            "hours_only": total_seconds / 3600,
            "minutes_only": total_seconds / 60,
            "seconds_only": total_seconds
            }
        return total_time
