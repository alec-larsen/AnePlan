from pathlib import Path
import os
import sqlite3
import sys

def setup():
    """
    Initialize SQLite database and set up tables if any are missing
    """
    #Root directory in source tree
    _DEV_ROOT = Path(__file__).resolve().parents[0]

    #Root directory of application:
    #Use executable directory when frozen
    if getattr(sys, "frozen", False):
        _ROOT_DIRECTORY = Path(sys.executable).parent
    #Else, use the source root during development
    else:
        _ROOT_DIRECTORY = _DEV_ROOT # type: ignore

    #Initialize sqlite3 connection
    conn = sqlite3.connect(_ROOT_DIRECTORY / "tasks.db")
    cursor = conn.cursor()
    #Run SQL setup script
    with open(_ROOT_DIRECTORY / "aneplan_setup.sql") as f:
        setup_code = f.read()
    cursor.executescript(setup_code)
    conn.commit()
    conn.close()

setup() #Setup call is here temporarily; TODO: Move to main.py after basic functions are complete.