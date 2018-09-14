import logging
import sqlite3
from interactive_list import InteractiveList
from interactive_params import InteractiveParams

class Log:
    def __init__(self):

        # SQL parameters and variables.
        self.conn = None
        self.cursor = None
        self.table = "sessions"
        self.schema = "CREATE TABLE " + self.table + " ("\
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"\
             "start TEXT,"\
             "end TEXT,"\
             "project TEXT,"\
             "tags TEXT,"\
             "notes TEXT)"

        self.rows = []
        self.formatted_rows = []
        self.last_inserted_row = None

        self.default_params = {
            "start": "0000-01-01 00:00:00",
            "end": "9999-12-31 23:59:59",
            "project": "",
            "tags": "",
            "notes": ""
            }

        self.filters = dict(self.default_params)


    ### Methods for creating, loading, and unloading SQLite DB. ###

    def create_db(self, filepath):
        try:
            self.conn = sqlite3.connect(filepath)
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.schema)
            self.select_all()
            return True
        except:
            return False

    def load_db(self, filepath):
        try:
            self.conn = sqlite3.connect(filepath)
            self.cursor = self.conn.cursor()
            # Check that the created or loaded DB has the correct table/schema.
            self.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
        except sqlite3.DatabaseError as e:
            logging.error(e)
            return False


        if not tables or tables[0][0] != self.table:
            logging.error("Database does not contain correct table.")
            self.conn.close()
            self.conn = None
            self.cursor = None
            return False

        column_names = [column[1] for column in self.cursor.execute(
            "PRAGMA table_info('{}')".format(self.table)).fetchall()]

        if column_names != ["id", "start", "end", "project", "tags", "notes"]:
            logging.error("Table does not contain correct columns.")
            self.conn.close()
            self.conn = None
            self.cursor = None
            return False

        self.select_all()
        return True

    def unload_db(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None
        self.cursor = None
        self.rows = []
        self.last_inserted_row = None


    ### Methods that interact directly with a loaded DB. ###

    def add_row(self, start="", end="", project="", tags="", notes=""):
        if self.cursor is None:
            raise RuntimeError("No database loaded")

        try:
            self.cursor.execute(
                "INSERT INTO {} (start, end, project, tags, notes)".format(
                    self.table) + "VALUES (?, ?, ?, ?, ?)",
                (start, end, project, tags, notes))
            self.conn.commit()
            self.filter_rows()
        except:
            return False

        return True

    def filter_rows(self):

        # TODO: sort rows by datetime
        if self.cursor is None:
            raise RuntimeError("No database loaded")

        if self.filters:
            # Build filter select query. Always include date in query.
            filter_query = "SELECT * FROM {} WHERE ".format(self.table)
            filter_query += "(start >= ? AND end <= ?"

            filter_values = [self.filters["start"], self.filters["end"]]
            for column in ("project", "tags", "notes"):
                if self.filters[column]:
                    filter_query += " AND {} LIKE ?".format(column)
                    filter_values.append("%{}%".format(self.filters[column]))
            filter_query += ")"

            try:
                self.cursor.execute(filter_query, filter_values)
                self.rows = self.cursor.fetchall()
                self.format_selected()
                return True
            except:
                return False
        else:
            return False

    def get_last_row_id(self):
        if not self.conn or not self.cursor:
            return 0

        try:
            self.cursor.execute("SELECT last_insert_rowid();")
            self.last_inserted_row = self.cursor.fetchone()[0]
            return self.last_inserted_row
        except:
            return 0

    def select_all(self):
        """Select all sessions in the DB."""
        # TODO: sort rows by datetime

        self.cursor.execute("SELECT * FROM {}".format(self.table))
        self.rows = self.cursor.fetchall()
        self.format_selected()

    def update_row(self, row_id, updated_params):

        if self.cursor is None:
            logging.error("No database loaded")
            return False

        columns = ("start", "end", "project", "tags", "notes")
        cols_to_update = [column for column in columns if column in updated_params]

        if not cols_to_update:
            logging.debug("No matching keys in dict.")
            return False

        # Build SQL update query.
        query = "UPDATE {} SET\n".format(self.table)
        query_update_strings = []
        values = []

        for column in cols_to_update:
            query_update_strings.append("{} = ?".format(column))
            values.append(updated_params[column])
        values.append(row_id)

        query = "UPDATE {} SET\n{}\nWHERE id = ?".format(
            self.table, ",\n".join(query_update_strings))

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.filter_rows()
            return True
        except:
            return False


    ### Methods that interact with data already extracted from a DB. ###

    def format_selected(self):
        """Format the currently selected rows and return a list of strings."""

        width = 8
        fmt_spec = "{{}} | {{}} | {{:{w}.{w}}} | {{:{w}.{w}}} | {{:{w}.{w}}}".format(w=width)
        self.formatted_rows = [fmt_spec.format(*row[1:]) for row in self.rows]

    def modify_filter(self):

        filters = InteractiveParams(
                    self.filters, header_text="Filter Criteria").start()
        if filters:
            self.filters = filters
            self.filter_rows()

    def view(self):

        if self.formatted_rows:
            InteractiveList(self.formatted_rows, select_mode="off").start()
        else:
            # TODO: Standardize logging messages across modules.
            print("There are no entries matching the current selection.")
