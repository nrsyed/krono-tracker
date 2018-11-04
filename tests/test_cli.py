import os
import sqlite3
import pytest
from krono.cli import CLI

@pytest.fixture(scope="class")
def cli():
    return CLI()

class TestCLI:
    """Test methods for command line interface."""

    def test_create(self, cli, caplog, tmpdir):
        """Test do_create()."""

        # Test blank input.
        cli.do_create("")
        assert "No filename entered." in caplog.messages

        # Test creation of new database.
        filepath = os.path.join(tmpdir.strpath, "new.db")
        cli.do_create(filepath)
        assert "Creating database file {}".format(filepath) in caplog.messages

    def test_load(self, cli, caplog, database, tmpdir):
        """Test do_load()."""

        # Test blank input.
        cli.do_load("")
        assert "No filename entered." in caplog.messages

        # Attempt to load nonexistent database.
        invalid_filepath = os.path.join(tmpdir.strpath, "nonexistent.db")
        cli.do_load(invalid_filepath)
        error_msg = "The database {} was not found.".format(invalid_filepath)
        assert error_msg in caplog.messages

        # Load an existing database.
        _, _, filepath = database(tmpdir.strpath)
        cli.do_load(filepath)
        assert cli.log

        # Load a different database, testing that the reference to the new
        # database is different from the previously loaded database.
        previous_conn = cli.log.conn
        _, _, new_filepath = database(tmpdir.strpath)
        cli.do_load(new_filepath)
        assert cli.log
        assert cli.log.conn != previous_conn
