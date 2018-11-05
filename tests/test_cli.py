import os
import sqlite3
import pytest
from krono.cli import CLI

@pytest.fixture(scope="function")
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
        assert not os.path.isfile(filepath)
        cli.do_create(filepath)
        assert "Creating database file {}".format(filepath) in caplog.messages
        assert os.path.isfile(filepath)

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

    def test_log_loaded(self, cli):
        """Test log_loaded attribute."""
        assert not cli.log_loaded
        cli.log = "arbitrary truthy value"
        assert cli.log_loaded

    def test_path(self, cli, capfd, caplog, tmpdir):
        """Test CLI path navigation methods."""

        # Check that initial path is correct.
        assert cli.path == os.getcwd()

        # Test getdir().
        cli.do_getdir(None)
        assert capfd.readouterr().out.rstrip() == os.getcwd()

        # Test cd() on nonexistent directory.
        nonexistent_dir = os.path.join(tmpdir.strpath, "nonexistentDir/")
        cli.do_cd(nonexistent_dir)
        error_msg = "The directory {} does not exist.".format(nonexistent_dir)
        assert error_msg in caplog.messages

        # Test cd() on existing directory.
        cli.do_cd(tmpdir.strpath)
        assert capfd.readouterr().out.rstrip() == tmpdir.strpath
        assert cli.path == tmpdir.strpath

        # Test ls() in empty directory.
        cli.do_ls(None)
        assert capfd.readouterr().out.rstrip() == ""

        # Test ls() in a directory with a single file.
        test_filename = "test"
        test_filepath = os.path.join(tmpdir.strpath, test_filename)
        with open(test_filepath, "w") as f:
            pass
        cli.do_ls(None)
        assert capfd.readouterr().out.rstrip() == test_filename

        # Test setcwd().
        cli.do_setcwd(None)
        assert cli.path == os.getcwd()
        assert capfd.readouterr().out.rstrip() == os.getcwd()
