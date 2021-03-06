import os
import sqlite3
import pytest
from krono.log import Log

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

    def test_unload_db(self, log_db):
        """Test DB unload."""

        # Set Log attributes to dummy truthy values.
        log = log_db
        log.last_inserted_row = 1

        log.unload_db()
        assert log.conn is None
        assert log.cursor is None
        assert log.rows == []
        assert log.last_inserted_row is None

    def test_load_db(self, log, tmpdir):
        """Test DB load, confirm exception in loading nonexistent file."""

        filepath = str(tmpdir.join(self.filename))

        # Attempt to load nonexistent file.
        with pytest.raises(FileNotFoundError):
            log.load_db(filepath)

        # Create DB (which should automatically load it).
        log.create_db(filepath)
        assert log.conn
        assert log.cursor

    def test_verify_db(self, database, tmpdir):
        """Test verification of DB table and schema."""

        valid_conn, valid_cursor, _ = database(
                tmpdir.strpath, table="valid", cols="valid")
        no_table_conn, no_table_cursor, _ = database(
                tmpdir.strpath, table=None, cols="valid")
        invalid_table_conn, invalid_table_cursor, _ = database(
                tmpdir.strpath, table="invalid", cols="valid")
        invalid_cols_conn, invalid_cols_cursor, _ = database(
                tmpdir.strpath, table="valid", cols="invalid")

        # Test valid database.
        log = Log()
        log.conn, log.cursor = valid_conn, valid_cursor
        log._verify_db()

        # Test invalid database with no table.
        log = Log()
        log.conn, log.cursor = no_table_conn, no_table_cursor
        with pytest.raises(RuntimeError) as e:
            log._verify_db()
        assert str(e.value) == "Database does not contain correct table." 

        # Test invalid database with incorrect table name.
        log = Log()
        log.conn, log.cursor = invalid_table_conn, invalid_table_cursor
        with pytest.raises(RuntimeError) as e:
            log._verify_db()
        assert str(e.value) == "Database does not contain correct table." 

        # Test invalid database with incorrect columns (but correct table name).
        log = Log()
        log.conn, log.cursor = invalid_cols_conn, invalid_cols_cursor
        with pytest.raises(RuntimeError) as e:
            log._verify_db()
        assert str(e.value) == "Table does not contain correct columns."

class TestDatabaseOperations:
    """
    Test methods for Log methods that directly interact with and/or modify
    the DB: add/delete/update rows and obtain last inserted row ID.
    """

    def test_add_row(self, log, database, tmpdir):
        """Test Log.add_row()."""

        # Define test rows to be added.

        # New row with value for just one column
        new_row_1 = {"start": "2018-10-01 00:00:00"}

        # New row with values for three columns.
        new_row_2 = {
                "start": "2018-10-01 00:00:00",
                "end": "2018-10-01 08:00:00"
                }

        # New row with values for all columns.
        new_row_3 = {
                "start": "2018-10-01 00:00:00",
                "end": "2018-10-01 08:00:00",
                "project": "dummy project",
                "tags": "",
                "notes": "dummy notes"
                }

        # Attempt to call Log.add_row() without a DB connection/cursor.
        with pytest.raises(RuntimeError) as e:
            log.add_row(new_row_1)
        assert str(e.value) == "No database loaded."

        # Assign SQL connection/cursor to Log object.
        conn, cursor, _ = database(tmpdir.strpath)
        log.conn, log.cursor = conn, cursor

        # Add and check first row.
        log.add_row(new_row_1)
        cursor.execute("SELECT last_insert_rowid();")
        last_row_id = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM sessions WHERE id={}".format(last_row_id))
        row = cursor.fetchone()
        assert row[1:] == ("2018-10-01 00:00:00", None, None, None, None)

        # Add and check second row.
        log.add_row(new_row_2)
        cursor.execute("SELECT last_insert_rowid();")
        last_row_id = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM sessions WHERE id={}".format(last_row_id))
        row = cursor.fetchone()
        assert row[1:] == ("2018-10-01 00:00:00", "2018-10-01 08:00:00",
                None, None, None)

        # Add and check third row.
        log.add_row(new_row_3)
        cursor.execute("SELECT last_insert_rowid();")
        last_row_id = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM sessions WHERE id={}".format(last_row_id))
        row = cursor.fetchone()
        assert row[1:] == ("2018-10-01 00:00:00", "2018-10-01 08:00:00",
                "dummy project", "", "dummy notes")

    def test_delete(self, log, database, tmpdir):
        """Test row delete method."""

        # Attempt to call Log.delete() without a DB connection/cursor.
        with pytest.raises(RuntimeError) as e:
            log.delete([1])
        assert str(e.value) == "No database loaded."

        # Assign SQL connection/cursor to Log object.
        conn, cursor, _ = database(tmpdir.strpath)
        log.conn, log.cursor = conn, cursor

        # Attempt to pass int instead of list.
        with pytest.raises(TypeError) as e:
            log.delete(1)
        assert str(e.value) == "object of type 'int' has no len()"

        # Get initial number of DB rows.
        cursor.execute("SELECT * FROM sessions")
        initial_num_db_rows = len(cursor.fetchall())

        # Delete two rows, then check length and verify identity of result.
        log.delete([1, 3])
        cursor.execute("SELECT * FROM sessions")
        db_rows = cursor.fetchall()
        assert len(db_rows) == initial_num_db_rows - 2
        assert db_rows[0][0] == 2   # remaining row id should be 2

        # Delete remaining row, then check length
        log.delete([2])
        cursor.execute("SELECT * FROM sessions")
        db_rows = cursor.fetchall()
        assert len(db_rows) == initial_num_db_rows - 3

    def test_filter_rows(self, log, database, tmpdir):
        """
        Test Log.filter_rows().

        The Log.filters attribute is a dict containing keys/values
        corresponding to the columns of the DB. In the interactive command
        line interface, the values are updated by the user via an ncurses
        interface (or by additional command line flags in non-interactive
        mode).

        Per Log.__init__() method, the default value for Log.filters are:

            self.default_params = {
                "start": "0000-01-01 00:00:00",
                "end": "9999-12-31 23:59:59",
                "project": "",
                "tags": "",
                "notes": ""
                }

            self.filters = dict(self.default_params)
        """

        # Attempt to call method without a DB connection/cursor.
        with pytest.raises(RuntimeError) as e:
            log.filter_rows()
        assert str(e.value) == "No database loaded."

        # Assign DB connection/cursor to Log object.
        conn, cursor, _ = database(tmpdir.strpath)
        log.conn, log.cursor = conn, cursor

        # Run default filter (should return all results).
        log.filter_rows()
        assert len(log.rows) == 3

        # Test date filters.
        log.filters["start"] = "2018-09-01 00:00:00"
        log.filters["end"] = "2018-11-01 00:00:00"
        log.filter_rows()
        assert len(log.rows) == 2
        assert [row[0] for row in log.rows] == [1, 2]   # Verify filtered row IDs

        log.filters["start"] = "2020-01-01 11:00:00"
        log.filters["end"] = "2020-01-02 00:00:00"
        log.filter_rows()
        assert len(log.rows) == 0

        # Test "project" filter.
        log.filters["start"] = "0000-01-01 00:00:00"
        log.filters["end"] = "9999-12-12 23:59:59"
        log.filters["project"] = "dummy project 3"
        log.filter_rows()
        assert len(log.rows) == 1
        assert log.rows[0][0] == 3      # verify row ID

        # Test changing "project" filter back to blank string.
        log.filters["project"] = ""
        log.filter_rows()
        assert len(log.rows) == 3

        # Test "tags" filter.
        log.filters["tags"] = "dummy tag 1"
        log.filter_rows()
        assert len(log.rows) == 1
        assert log.rows[0][0] == 1      # verify row ID

        # Test changing "tags" filter back to blank string.
        log.filters["tags"] = ""
        log.filter_rows()
        assert len(log.rows) == 3

        # Test "notes" filter.
        log.filters["notes"] = "dummy notes 2"
        log.filter_rows()
        assert len(log.rows) == 1
        assert log.rows[0][0] == 2      # verify row ID

        # Test changing "notes" filter back to blank string.
        log.filters["notes"] = ""
        log.filter_rows()
        assert len(log.rows) == 3

        # Test multiple filter values.
        log.filters["start"] = "2018-09-01 12:00:00"
        log.filters["end"] = "2018-12-01 12:00:00"
        log.filters["project"] = "dummy project 2"
        log.filter_rows()
        assert len(log.rows) == 1
        assert log.rows[0][0] == 2

        # Check that nonexistent columns have no effect.
        log.filters["project"] = ""
        log.filters["not_real_column"] = "dummy value"
        log.filter_rows()
        assert len(log.rows) == 2

    def test_update_row(self, log, database, tmpdir):
        """Test row update method."""

        # Attempt to call method without a DB connection/cursor.
        with pytest.raises(RuntimeError) as e:
            log.update_row(1, None)
        assert str(e.value) == "No database loaded."

        # Assign DB connection/cursor to Log object.
        conn, cursor, _ = database(tmpdir.strpath)
        log.conn, log.cursor = conn, cursor

        # Check that exception is raised if no valid column names
        # (dict keys) are supplied.
        with pytest.raises(RuntimeError) as e:
            log.update_row(1, {})
        assert str(e.value) == "No valid parameters supplied."

        with pytest.raises(RuntimeError) as e:
            log.update_row(1, {"invalid_col": "dummy value"})
        assert str(e.value) == "No valid parameters supplied."

        # Test update of various combinations of (valid) parameters.
        log.update_row(1, {"start": "2006-06-06 06:00:00"})
        assert log.rows[0] == (1, "2006-06-06 06:00:00", "2018-09-29 23:30:00",
                "dummy project 1", "dummy tag 1", "dummy notes 1")

        log.update_row(2, {
            "start": "2016-07-07 07:00:00",
            "end": "2016-07-07 15:00:00",
            "project": "updated project name",
            "tags": "updated tag",
            "notes": ""
            })
        assert log.rows[1] == (2, "2016-07-07 07:00:00", "2016-07-07 15:00:00",
                "updated project name", "updated tag", "")

        # Test a mix of valid and invalid parameters.
        log.update_row(3, {
            "start": "2019-12-31 22:30:00",
            "invalid_col": "dummy value",
            "tags": "updated tag 3",
            "invalid_col_2": "dummy value 2"
            })
        assert log.rows[2] == (3, "2019-12-31 22:30:00", "2020-01-03 10:00:00",
                "dummy project 3", "updated tag 3", "dummy notes 3")

    def test_select_all(self, log_db):
        """Test Log.select_all()."""

        log = log_db

        # Select one row, then run select_all() to ensure all are selected.
        log.filters["project"] = "dummy project 1"
        log.filter_rows()
        assert len(log.rows) == 1

        log.select_all()
        assert len(log.rows) == 3
