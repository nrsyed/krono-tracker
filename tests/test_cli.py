import os
import sqlite3
import pytest
from krono.cli import CLI

@pytest.fixture(scope="class")
def cli():
    return CLI()

class TestCLI:
    """Test methods for command line interface."""

    def test_load(self, cli, capfd, tmpdir):
        """Test do_load()."""

        # Test blank input.
        cli.do_load("")
        stdout = capfd.readouterr().out
        assert stdout.rstrip() == "Error: No filename entered."

        # TODO: remaining tests
