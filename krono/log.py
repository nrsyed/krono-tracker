import sqlite3

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
        self.last_inserted_row = None

    def add_row(self, start="", end="", project="", tags="", notes=""):
        if self.cursor is None:
            raise RuntimeError("No database loaded")

        try:
            self.cursor.execute(
                "INSERT INTO {} (start, end, project, tags, notes)".format(
                    self.table) + "VALUES (?, ?, ?, ?, ?)",
                (start, end, project, tags, notes))
            self.conn.commit()
        except:
            return False

        return True

    def update_row(self, row_id, **kwargs):
        # Build SQL update query.

        if self.cursor is None:
            raise RuntimeError("No database loaded")
        elif kwargs is None:
            return False

        columns = ("start", "end", "project", "tags", "notes")
        columns_to_update = [column for column in columns if column in kwargs]

        if not columns_to_update:
            return False

        query = "UPDATE {} SET\n".format(self.table)
        query_update_strings = []
        values = []

        for column in columns_to_update:
            query_update_strings.append("{} = ?".format(column))
            values.append(kwargs[column])
        values.append(row_id)

        query = "UPDATE {} SET\n{}\nWHERE id = ?".format(
            self.table, ",\n".join(query_update_strings))

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except:
            return False

    def create_db(self, filepath):
        try:
            self.conn = sqlite3.connect(filepath)
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.schema)
            return True
        except:
            return False

    def load_db(self, filepath):
        try:
            self.conn = sqlite3.connect(filepath)
            self.cursor = self.conn.cursor()
        except:
            return False

        # Check that the created or loaded DB has the correct table/schema.
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        # Check table name.
        if not tables or tables[0][0] != self.table:
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

    def unload_db(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None
        self.cursor = None
        self.rows = []
        self.last_inserted_row = None

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

        self.cursor.execute("SELECT * FROM {}".format(self.table))
        self.rows = self.cursor.fetchall()

    def format_selected(self):
        """Format the currently selected rows and return a list of strings."""

        width = 8
        fmt_spec = "{{}} | {{}} | {{:{w}.{w}}} | {{:{w}.{w}}} | {{:{w}.{w}}}".format(w=width)
        formatted = [fmt_spec.format(*row[1:]) for row in self.rows]
        return formatted
