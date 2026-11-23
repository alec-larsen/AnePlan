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

#Util functions
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

def get_completion(name: str):
    """
    Given the name of a task, find its weight
    
    If a task with the given name does not exist, return -1
    """
    if not task_exists(name):
        return -1
    
    return conn.execute("""
    SELECT completion
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[0]

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

#Check functions; ensure key properties of tasklist aren't violated
def in_cycle(task: str, parent: str):
    """
    Check whether task with parent forms a cycle.
    """
    #Task being its own parent is a 1-cycle
    if task == parent:
        return True
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

#TODO (after implementing task prereqs): implement check function to catch cyclical prereq paths

#Tasklist manipulation/rendering functions
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

#Setter functions. All assume that arguments are well behaved (all ill-defined arguments are filtered out in gui input handlers)
def set_weight(task: str, weight: int):
    """
    Set task weight.

    NOTE: Only leaf tasks keep their weight. All higher-level tasks have a weight equal to the sum of their children.
    """
    #Leaf tasks get the set weight
    if not get_children(task):
        conn.execute("""
        UPDATE tasks
        SET weight = ?
        WHERE name = ?
        """, (weight,task))
        task = get_parent(task)
    while task is not None:
        #Any weight of a non-leaf task is the sum of its children's weights
        agg_weight = sum([get_weight(child) for child in get_children(task)])
        conn.execute("""
        UPDATE tasks
        SET weight = ?
        WHERE name = ?
        """, (agg_weight,task))
        task = get_parent(task)
    conn.commit()

def set_completion(task: str, completion: float):
    """
    Set task completion.
    
    NOTE: Only leaf tasks keep their set completion. All higher-level tasks have completion equal to the sum of their children.
    """
    #Leaf tasks get the set weight
    if not get_children(task):
        conn.execute("""
        UPDATE tasks
        SET completion = ?
        WHERE name = ?
        """, (completion,task))
        task = get_parent(task)
    while task is not None:
        #Any completion of a non-leaf task is the sum of its children's completions
        agg_completion = sum([get_completion(child) for child in get_children(task)])
        conn.execute("""
        UPDATE tasks
        SET completion = ?
        WHERE name = ?
        """, (agg_completion,task))
        task = get_parent(task)
    conn.commit()

def set_parent(task: str, parent: str):
    """
    Set task parent.

    Note that parents should not be set in such a way that a loop of parent-child relationships forms. Input handlers in gui protect from these cases.
    """
    old_parent = get_parent(task)
    conn.execute("""
    UPDATE tasks
    SET parent = ?
    WHERE name = ?
    """, (parent,task))
    conn.commit()
    #This parent reassignment changes the weight and completion of both the old and new parent
    set_weight(parent,0)
    set_weight(old_parent,0)
    set_completion(parent,0)
    set_completion(old_parent,0)

def set_name(task: str, name: str):
    """
    Rename task.
    """
    #Add new task
    add_task(name, get_weight(task), get_completion(task), get_parent(task))
    #Update parent field of all children with new name
    for child in get_children(task):
        set_parent(child, name)
    #Delete outdated task
    remove_task(task)
