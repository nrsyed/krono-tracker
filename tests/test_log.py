import pytest
from krono.log import Log

class TestLog:
    @pytest.fixture(scope="class")
    def log(self):
        log = Log()
        return log

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
