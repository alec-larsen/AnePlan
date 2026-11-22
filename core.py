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

def task_exists(name: str):
    """
    Check if task with given name exists.
    """
    cursor = conn.cursor()
    return cursor.execute("""
    SELECT COUNT(*)
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[0] > 0

def get_weight(name: str):
    """
    Given the name of a task, find its weight

    If a task with the given name does not exist, return -1
    """
    if not task_exists(name):
        return -1

    return conn.execute("""
    SELECT weight
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[0]

def get_parent(name: str):
    """
    Given the name of a task, find its parent
    """
    if not task_exists(name):
        return -1
    return conn.execute("""
    SELECT parent
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[0]

def in_cycle(task: str, parent: str):
    """
    Check whether task with parent forms a cycle.
    """
    #Traverse up task tree looking for a root task (parent is None)
    while parent is not None:
        parent = conn.execute("""
        SELECT parent
        FROM tasks
        WHERE name = ?
        """, (parent,)).fetchone()[0]
        #If parent is the original task, we have found a cycle.
        if parent == task:
            return True

    return False

def get_root_tasks():
    """
    Get names of root tasks (tasks with no parents)
    """
    results = conn.execute("""
    SELECT name
    FROM tasks
    WHERE parent is NULL
    """).fetchall()
    return [res[0] for res in results]

def get_children(task: str|None):
    """
    Get names of all tasks whose parent is specified by the name given.

    If an empty task (i.e. None) is given, return all root tasks.
    """
    if task is None:
        return get_root_tasks()
    results = conn.execute("""
        SELECT name
        FROM tasks
        WHERE parent = ?
        """, (task,)).fetchall()
    return [res[0] for res in results]

def get_leafs():
    """
    Get names of leaf tasks (tasks with no children)
    """
    results = conn.execute("""
        SELECT parent
        FROM tasks
        """).fetchall()
    tasks = conn.execute("""
        SELECT name
        FROM tasks
    """).fetchall()
    return [name[0] for name in tasks if name[0] not in [res[0] for res in results]]

def task_str(name: str):
    """
    Build string representation of given task with name.

    Note that all float values are rounded to two decimal places.
    """
    #Get task by name and unpack resultant tuple to obtain remaining task details.
    parent, weight, completed = conn.execute("""
    SELECT *
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[1:]
    if weight == 0:
        return(f"{name} - {completed:.2f}/{weight} (-%)")
    else:
        return(f"{name} - {completed:.2f}/{weight} ({completed/weight*100:.2f}%)")

def add_task(task_name: str, weight: int = 1, completion: float = 0, parent: int = None):
    """
    Add task to database.

    Arguments:
    task_name (str) - Name of task. Must be unique
    weight (int) - Weight of task. Must be a positive value. Defaults to 1.
    completion (float) - Weight units of task completed; defaults to 0.
    parent (int) - name of parent task. None if task has no parent
    """
    if not isinstance(weight, int):
        print("Task could not be added. Assigned weight must be an integer.")
        return
    if not isinstance(completion, (int, float)):
            print("Task could not be added. Completion must be an integer or float.")
            return
    if completion > weight:
        print("Task could not be added. Completion cannot exceed assigned task weight.")
        return
    conn.execute("""
    INSERT INTO tasks (name, parent, weight, completion)
    VALUES (?,?,?,?)
    """, (task_name, parent, weight, completion))
    conn.commit()

def remove_task(task: str):
    """
    Remove task by name.

    All children of task become children of deleted task's parent.
    """
    #Get parent of task to be deleted.
    parent = conn.execute("""
    SELECT parent
    FROM tasks
    WHERE name = ?
    """, (task,)).fetchone()[0]
    #Any children of task become children of parent.
    conn.execute("""
    UPDATE tasks
    SET parent = ?
    WHERE parent = ?
    """, (parent,task))
    #Remove task from database
    conn.execute("""
    DELETE
    FROM tasks
    WHERE name = ?
    """, (task,))
    conn.commit()

def clear_tasks():
    """
    Removes all tasks from tasklist.
    """
    #Remove task from database
    conn.execute("""DELETE FROM tasks""")
    conn.commit()
