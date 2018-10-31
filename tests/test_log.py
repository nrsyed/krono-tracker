import os
import sqlite3
import pytest
from krono.log import Log

@pytest.fixture(scope="function")
def database():
    table_names = {
            "valid": "sessions",
            "invalid": "bad_table_name"
            }

    col_names = {
            "valid": ("start", "end", "project", "tags", "notes"),
            "invalid": ("badcol1", "badcol2", "badcol3", "badcol4", "badcol5")
            }

    row = ("2018-09-29 23:00:00", "2018-09-29 23:30:00",
            "dummy project", "dummy tag", "dummy notes")

    num_calls = 0

    def _database(directory, table="valid", cols="valid"):
        nonlocal num_calls
        db_filename = "test{}.db".format(num_calls)
        db_filepath = os.path.join(directory, db_filename)
        num_calls += 1

        conn = sqlite3.connect(db_filepath)
        if table:
            schema = "CREATE TABLE " + table_names[table] + " (" \
                + "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                + "{} TEXT, {} TEXT, {} TEXT, {} TEXT, {} TEXT".format(
                        *col_names[cols]) \
                + ")"

            insert_query = "INSERT INTO " + table_names[table] \
                    + " ({}, {}, {}, {}, {}) ".format(*col_names[cols]) \
                    + "VALUES (?, ?, ?, ?, ?)"

            conn.execute(schema)
            conn.execute(insert_query, row)
            conn.commit()

        return conn

    return _database

@pytest.fixture(scope="function")
def log():
    log = Log()
    return log

class TestLogObject:
    """Test instantiation of Log object."""

    def test_instantiate_log(self, log):
        assert log
        assert log.conn == None
        assert log.cursor == None
        assert log.table == "sessions"
        assert log.schema == "CREATE TABLE " + log.table + " ("\
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"\
             "start TEXT,"\
             "end TEXT,"\
             "project TEXT,"\
             "tags TEXT,"\
             "notes TEXT)"

        assert log.rows == []
        assert log.last_inserted_row == None

        assert log.default_params == {
            "start": "0000-01-01 00:00:00",
            "end": "9999-12-31 23:59:59",
            "project": "",
            "tags": "",
            "notes": ""
            }

        assert log.filters == dict(log.default_params)

class TestCreateLoadUnload:
    """Test methods for creating, loading, unloading a DB (file).""" 

    filename = "test.db"

    def test_create_db(self, log, tmpdir):
        """
        Test whether a new DB file is created, whether resulting DB is
        loaded properly, and whether an exception is thrown if the file to be
        created already exists.
        """
        filepath = str(tmpdir.join(self.filename))
        log.create_db(filepath)
        assert os.path.isfile(filepath)
        assert log.conn
        assert log.cursor

        with pytest.raises(FileExistsError):
            log.create_db(filepath)

    def test_unload_db(self, log, database, tmpdir):
        """Test DB unload method."""

        # Set Log attributes to dummy truthy values.
        conn = database(tmpdir.strpath, table="valid", cols="valid")
        log.conn = conn
        log.cursor = conn.cursor()
        log.last_inserted_row = 1

        log.unload_db()
        assert log.conn is None
        assert log.cursor is None
        assert log.rows == []
        assert log.last_inserted_row is None

    def test_load_db(self, log, tmpdir):
        """Test DB load and unload."""

        filepath = str(tmpdir.join(self.filename))

        # Attempt to load nonexistent file.
        with pytest.raises(FileNotFoundError):
            log.load_db(filepath)

        # Create DB (which should automatically load it), then unload.
        log.create_db(filepath)
        assert log.conn
        assert log.cursor

    def test_verify_db(self, database, tmpdir):
        """Test verification of DB table and schema."""

        valid_conn = database(tmpdir.strpath, table="valid", cols="valid")
        no_table_conn = database(tmpdir.strpath, table=None, cols="valid")
        invalid_table_conn = database(tmpdir.strpath, table="invalid", cols="valid")
        invalid_cols_conn = database(tmpdir.strpath, table="valid", cols="invalid")

        # Test valid database.
        log = Log()
        log.conn = valid_conn
        log.cursor = valid_conn.cursor()
        log._verify_db()

        # Test invalid database with no table.
        log = Log()
        log.conn = no_table_conn
        log.cursor = no_table_conn.cursor()
        with pytest.raises(RuntimeError) as e:
            log._verify_db()
        assert str(e.value) == "Database does not contain correct table." 

        # Test invalid database with incorrect table name.
        log = Log()
        log.conn = invalid_table_conn
        log.cursor = invalid_table_conn.cursor()
        with pytest.raises(RuntimeError) as e:
            log._verify_db()
        assert str(e.value) == "Database does not contain correct table." 

        # Test invalid database with incorrect columns (but correct table name).
        log = Log()
        log.conn = invalid_cols_conn
        log.cursor = invalid_cols_conn.cursor()
        with pytest.raises(RuntimeError) as e:
            log._verify_db()
        assert str(e.value) == "Table does not contain correct columns."
