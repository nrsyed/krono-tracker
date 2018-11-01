import os
import sqlite3
import pytest
from krono.log import Log

@pytest.fixture(scope="function")
def database():
    """
    Database factory to mock valid or invalid SQLite database.
    """

    table_names = {
            "valid": "sessions",
            "invalid": "bad_table_name"
            }

    col_names = {
            "valid": ("start", "end", "project", "tags", "notes"),
            "invalid": ("badcol1", "badcol2", "badcol3", "badcol4", "badcol5")
            }

    # Rows with dummy data.
    row1 = ("2018-09-29 23:00:00", "2018-09-29 23:30:00",
            "dummy project 1", "dummy tag 1", "dummy notes 1")
    row2 = ("2018-10-29 23:00:00", "2018-10-29 23:30:00",
            "dummy project 2", "dummy tag 2", "dummy notes 2")
    row3 = ("2020-01-01 12:00:00", "2020-01-03 10:00:00",
            "dummy project 3", "dummy tag 3", "dummy notes 3")

    # Track number of times factory is called for use in DB filename to
    # create a unique DB each time instead of loading existing DB.
    num_calls = 0

    def _database(directory, table="valid", cols="valid"):
        nonlocal num_calls
        db_filename = "test{}.db".format(num_calls)
        db_filepath = os.path.join(directory, db_filename)
        num_calls += 1

        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        if table:
            schema = "CREATE TABLE " + table_names[table] + " (" \
                + "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                + "{} TEXT, {} TEXT, {} TEXT, {} TEXT, {} TEXT".format(
                        *col_names[cols]) \
                + ")"

            insert_query = "INSERT INTO " + table_names[table] \
                    + " ({}, {}, {}, {}, {}) ".format(*col_names[cols]) \
                    + "VALUES (?, ?, ?, ?, ?)"

            cursor.execute(schema)
            cursor.execute(insert_query, row1)
            cursor.execute(insert_query, row2)
            cursor.execute(insert_query, row3)
            conn.commit()

        return (conn, cursor)

    return _database

@pytest.fixture(scope="function")
def log():
    log = Log()
    return log

@pytest.fixture(scope="function")
def log_db(log, database, tmpdir):
    log.conn, log.cursor = database(tmpdir.strpath)
    return log
