from pathlib import Path
import os
import sqlite3
import sys
import util

#Set root directory of application:
#Use executable directory when frozen
if getattr(sys, "frozen", False):
    _ROOT_DIRECTORY = Path(sys.executable).parent
#Else, use the source root during development
else:
    _ROOT_DIRECTORY = Path(__file__).resolve().parents[0] # type: ignore

#_ROOT_DIRECTORY may route tasks.db to temporary directory, wiping any progress. Send data to APPDATA to carry over between sessions
_DATA_DIRECTORY = Path(os.getenv("LOCALAPPDATA")) / "AnePlan"
_DATA_DIRECTORY.mkdir(exist_ok=True)

#Set up connection to SQLite database
conn = sqlite3.connect(_DATA_DIRECTORY / "tasks.db")

def setup():
    """
    Set up required tables in SQLite database if any are missing
    """
    #Initialize sqlite3 connection
    cursor = conn.cursor()
    #Run SQL setup script
    with open(_ROOT_DIRECTORY / "aneplan_setup.sql") as f:
        setup_code = f.read()
    cursor.executescript(setup_code)
    conn.commit()
