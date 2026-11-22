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

def task_exists(task: int|str):
    """
    Check if task with given id exists.

    Arguments:
    id: task identifier to search for; id if int, else task name
    """
    cursor = conn.cursor()
    #If id is strint, it refers to an id; cast to int
    if util.is_strint(task):
        task = int(task)
    #If identifier is integer
    if isinstance(task, int):
        return cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE id = ?
        """, (task,)).fetchone()[0] > 0
    else:
        return cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE name = ?
        """, (task,)).fetchone()[0] > 0

def fetch_task_id(name: str):
    """
    Given the name of a task, find its integer id

    If a task with the given name does not exist, return -1
    """
    if not task_exists(name):
        return -1

    return conn.execute("""
    SELECT id
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[0]

def fetch_task_name(id: str):
    """
    Given the id of a task, find its name

    If a task with the given id does not exist, return -1
    """
    if not task_exists(id):
        return -1

    return conn.execute("""
    SELECT name
    FROM tasks
    WHERE id = ?
    """, (id,)).fetchone()[0]

def fetch_task_parent(id: int, give_name = True):
    """
    Given the id of a task, find its name

    If a task with the given id does not exist, return -1
    """
    if not task_exists(id):
        return -1

    parent = conn.execute("""
    SELECT parent_id
    FROM tasks
    WHERE id = ?
    """, (id,)).fetchone()[0]

    if give_name and parent:
        return fetch_task_name(parent)
    else:
        return parent

def in_cycle(task: int, parent: int):
    """
    Check whether task with parent forms a cycle.
    """
    #Traverse up task tree looking for a root task (parent is None)
    while parent is not None:
        parent = conn.execute("""
        SELECT parent_id
        FROM tasks
        WHERE id = ?
        """, (parent,)).fetchone()[0]
        #If parent is the original task, we have found a cycle.
        if parent == task:
            return True

    return False

def get_root_tasks():
    """
    Get ids of root tasks (tasks with no parents)
    """
    results = conn.execute("""
    SELECT id
    FROM tasks
    WHERE parent_id is NULL
    """).fetchall()
    return [res[0] for res in results]

def get_children(task: int|str|None):
    """
    Get ids of all tasks whose parent is specified by the id or name given.

    If an empty task (i.e. None) is given, return all root tasks.
    """
    if task is None:
        return get_root_tasks()
    #If task string is supplied, we cast to int first in order to search
    if isinstance(task, str):
        #If the user inputted a task id, it will be string
        if util.is_strint(task):
            task = int(task)
        #If the input was not a strint, it should be the name of a task. We fetch its corresponding task_id
        else:
            task = fetch_task_id(task)
    results = conn.execute("""
        SELECT id
        FROM tasks
        WHERE parent_id = ?
        """, (task,)).fetchall()
    return [res[0] for res in results]

def get_leafs():
    """
    Get ids of leaf tasks (tasks with no children)
    """
    results = conn.execute("""
        SELECT parent_id
        FROM tasks
        """).fetchall()
    task_ids = conn.execute("""
        SELECT id
        FROM tasks
    """).fetchall()
    return [id[0] for id in task_ids if id[0] not in [res[0] for res in results]]

def task_str(id: int):
    """
    Build string representation of given task with id.

    Note that all float values are rounded to two decimal places.
    """
    #Get task by id and unpack resultant tuple to obtain remaining task details.
    parent, name, weight, completed = conn.execute("""
    SELECT *
    FROM tasks
    WHERE id = ?
    """, (id,)).fetchone()[1:]
    return(f"{name} - {completed:.2f}/{weight} ({completed/weight*100:.2f}%)")

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
    INSERT INTO tasks (parent_id, name, weight, completion)
    VALUES (?,?,?,?)
    """, (parent, task_name, weight, completion))
    conn.commit()
