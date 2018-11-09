import os
import sqlite3
import threading
import pytest
from krono.session import Session

class TestSessionObject:
    """Test methods for Session."""

    def test_instantiate(self, log):
        sess = Session(log, 1)
        assert not sess.lock
        assert sess.autosave_interval == 60
        del sess

        sess = Session(log, 1, lock=threading.Lock())
        assert sess.lock
