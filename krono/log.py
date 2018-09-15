import logging
import sqlite3
from interactive_list import InteractiveList
from interactive_params import InteractiveParams

class Log:
    """Class that interacts with and manipulates a Krono SQLite database."""

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
        """Make a new SQLite DB file."""

        try:
            self.conn = sqlite3.connect(filepath)
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.schema)
            self.select_all()
            return True
        except:
            return False

    def load_db(self, filepath):
        """Load an existing SQLite DB."""

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
        """Unload the currently loaded DB."""

        if self.conn is not None:
            self.conn.close()
        self.conn = None
        self.cursor = None
        self.rows = []
        self.last_inserted_row = None


    ### Methods that interact directly with a loaded DB. ###

    def add_row(self, new_row_vals):
        """Add a new row to the DB."""

        if self.cursor is None:
            raise RuntimeError("No database loaded")

        # Build SQL insert query.

        # Get the names of columns in new_row_vals corresponding to actual
        # columns in the table. These column names (and their values) will
        # be supplied to the INSERT INTO query.
        cols_with_vals = self.get_valid_columns(new_row_vals)

        query_insert_strings = []
        value_question_marks = []
        values = []

        for column in cols_with_vals:
            query_insert_strings.append("{} = ?".format(column))
            values.append(new_row_vals[column])
            value_question_marks.append("?")

        query = "INSERT INTO {} ({}) VALUES ({})".format(
                self.table,
                ",".join(cols_with_vals),
                ",".join(value_question_marks))

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.filter_rows()
        except:
            return False

        return True

    def filter_rows(self):
        """Select rows from the DB based on the current filter criteria."""

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
                return True
            except:
                return False
        else:
            return False

    def get_last_row_id(self):
        """Get the ID of the last row added to the DB."""

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

    def update_row(self, row_id, updated_params):
        """Update the columns a row in the DB based on its ID number."""

        if self.cursor is None:
            logging.error("No database loaded")
            return False

        cols_to_update = self.get_valid_columns(updated_params)

        if not cols_to_update:
            logging.debug("No matching keys in dict.")
            return False

        # Build SQL update query.
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


    ### Methods, properties that do not directly interact with a DB. ###

    @property
    def formatted_rows(self):
        """Format the currently selected rows and return a list of strings."""

        format_spec = "{{}} | {{}} | {{:{w}.{w}}} | {{:{w}.{w}}} | {{:{w}.{w}}}"
        width = 8
        format_spec = format_spec.format(w=width)
        return [format_spec.format(*row[1:]) for row in self.rows]

    def modify_filter(self):
        """Modify the parameters of the current filter."""

        filters = InteractiveParams(
                    self.filters, header_text="Filter Criteria").start()
        if filters:
            self.filters = filters
            self.filter_rows()

    @staticmethod
    def get_valid_columns(params):
        """Return a list of the valid columns in a dict."""

        valid_columns = ("start", "end", "project", "tags", "notes")
        return [column for column in valid_columns if column in params]

    def view(self):
        """List the rows in the current selection with a curses window."""

        formatted_rows = self.formatted_rows
        if formatted_rows:
            InteractiveList(formatted_rows, select_mode="off").start()
        else:
            # TODO: Standardize logging messages across modules.
            print("There are no entries matching the current selection.")
