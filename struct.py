from pathlib import Path
import os
import sqlite3
import sys

#Set root directory of application:
#Use executable directory when frozen
if getattr(sys, "frozen", False):
    _ROOT_DIRECTORY = Path(sys.executable).parent
#Else, use the source root during development
else:
    _ROOT_DIRECTORY = Path(__file__).resolve().parents[0] # type: ignore

#Set up connection to SQLite database
conn = sqlite3.connect(_ROOT_DIRECTORY / "tasks.db")

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

def task_exists(id: int):
    """
    Check if task with given id exists.

    Arguments:
    id: task id to search for
    """
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COUNT(*)
    FROM tasks
    WHERE id = ?
    """, (id,))
    count = cursor.fetchone()[0]
    return count > 0


def add_task(task_name: str, weight: int = 1, completion: float = 0, parent: int = None, prerequesites: list[int] = []):
    """
    Add task to database.

    Arguments:
    task_name (str) - Name of task. Must be unique
    weight (int) - Weight of task. Must be a positive value. Defaults to 1.
    completion (float) - Weight units of task completed; defaults to 0.
    parent (int) - integer id of parent task. None if task has no parent
    prerequesites (list[int]) - list of integer ids for all prerequesite tasks (tasks that must be completed before this one can be)
    """
    if not isinstance(weight, int):
        print("Task could not be added. Assigned weight must be an integer.")
        return
    if not isinstance(weight, (int, float)):
            print("Task could not be added. Completion must be an integer or float.")
            return
    if completion > weight:
        print("Task could not be added. Completion cannot exceed assigned task weight.")
        return
    conn = sqlite3.connect(_ROOT_DIRECTORY / "tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tasks (parent_id, title, weight, completion)
    VALUES (?,?,?,?)
    """, (parent, task_name, weight, completion))
    conn.commit()

setup() #Setup call is here temporarily; TODO: Move to main.py after basic functions are complete.