from tkinter import *
import tkinter.font as font
import tkinter.messagebox as mb
from tkinter.ttk import *

import core
import util

STATE = {
    "render_mode": "L", #Current mode tasklist renders in (Leaf-Only, Root-Only, Hierarchy)
    "head_task": None #Task whose subtasks are rendered in hierarchy view. None renders all tasks.
}

#Initialize control panel
master = Tk()
master.geometry("600x600")
master.title("AneTask Control Panel")

tasks = Tk()
tasks.geometry("400x400")
tasks.title("AneTasklist")

FONTS = {
    "head": font.Font(family="Helvetica", size=14, weight=font.BOLD),
    "subhead": font.Font(family="Helvetica", size=12, weight=font.BOLD)
}

def shutdown():
    """
    Confirm user exit and close both AneTask windows.
    """
    if mb.askokcancel("Exit", "Exit AneTask?\nThis will close both the control panel and tasklist."):
        tasks.destroy()
        master.destroy()

def task_str(name: int):
    """
    Build string representation of given task with name.

    Note that all float values are rounded to two decimal places.
    """
    #Get task by name and unpack resultant tuple to obtain remaining task details.
    parent, weight, completed = core.conn.execute("""
    SELECT *
    FROM tasks
    WHERE name = ?
    """, (name,)).fetchone()[1:]
    if weight == 0:
        return[f"{name}", f"{completed:.2f}/{weight}", f"-%"]
    else:
        return[f"{name}", f"{completed:.2f}/{weight}", f"{completed/weight*100:.2f}%"]

def clear_window(window):
    for w in window.winfo_children():
        w.destroy()

def render_tasklist_lr(mode: str):
    """
    Render list of all root/leaf tasks, depending on mode selected.

    mode L: render all leaf tasks (tasks with no children)
    mode R: render all root tasks (tasks with no parent)
    """
    clear_window(tasks)
    if mode == "L":
        #If viewing leaf tasks, ensure mode is set to L for future calls to render_tasklist()
        STATE["render_mode"] = "L"
        #Get all leaf tasks
        task_names = core.get_leafs()
        #Print appropriate table heading
        Label(tasks,text="COMPONENT TASKS",font=FONTS["head"]).grid(column=0,row=0)
    else:
        #If viewing root tasks, ensure mode is set to R for future calls to render_tasklist()
        STATE["render_mode"] = "R"
        #Get all root tasks
        task_names = core.get_root_tasks()
        #Print appropriate table heading
        Label(tasks,text="ROOT TASKS",font=FONTS["head"]).grid(column=0,row=0)
    #Place tasklist in its own frame. This ensures the table heading rendered previously is centered
    task_table = Frame(tasks)
    task_table.grid(column=0,row=1)
    #Render column headers
    Label(task_table, text="Task Name").grid(column = 0, row = 0, sticky = 'w')
    Label(task_table, text="Progress").grid(column = 1, row = 0, sticky = 'e', padx = 20)
    Label(task_table, text="Percent Completed").grid(column = 2, row = 0, sticky = 'e', padx = 20)
    #Render rows of task table from fetched tasks
    for index, n in enumerate(task_names,1):
        task_pieces = task_str(n)
        Label(task_table, text=task_pieces[0]).grid(column = 0, row = index, sticky = 'w')
        Label(task_table, text=task_pieces[1]).grid(column = 1, row = index, sticky = 'e', padx = 20)
        Label(task_table, text=task_pieces[2]).grid(column = 2, row = index, sticky = 'e', padx = 20)

def render_tasklist_h(task: int = None, depth: int = 0, row: int = 0, task_tree = None):
    """
    Render list of all tasks in hierarchy format.
    """
    #Initialize frame widgets in the first pass only.
    if depth == 0:
        #Change head task if this function was called from 'Change View' button.
        STATE["head_task"] = task
        clear_window(tasks)
        #If viewing task hierarchy, ensure mode is set to H for future calls to render_tasklist()
        STATE["render_mode"] = "H"
        #Print appropriate table heading
        if task is None:
            Label(tasks,text="ALL TASKS",font=FONTS["head"]).grid(column=0,row=0)
        elif not core.task_exists(task):
            Label(tasks,text=f"Task '{task}' not found",font=FONTS["head"]).grid(column=0,row=0)
        else:
            Label(tasks,text=task.upper(),font=FONTS["head"]).grid(column=0,row=0)
        task_tree = Frame(tasks)
        task_tree.grid(column=0,row=1)
    #Get all children of current task
    for subtask in core.get_children(task):
        #Add indent for every level of depth subtask sits at in tree
        Label(task_tree,text='● ' + core.task_str(subtask)).grid(column=0,row=row,padx=50*depth,pady=2,sticky="w")
        #Recursively call rendering from subtask. Increase depth by 1
        row = render_tasklist_h(subtask, depth+1, row+1, task_tree)
    return row

def render_tasklist():
    if STATE["render_mode"] == "L":
        render_tasklist_lr("L")
    elif STATE["render_mode"] == "R":
        render_tasklist_lr("R")
    else:
        render_tasklist_h(task=STATE["head_task"])

def clear_tasklist():
    if mb.askokcancel("Clear all tasks?","This action will clear ALL tasks from the tasklist.\nAre you sure you want to do this?"):
        core.clear_tasks()
        render_tasklist()

Label(master, text="Options", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

render_options = Frame(master)
render_options.grid(column=0,row=1,sticky="w")

Label(render_options, text="Tasklist Quickview:").grid(column = 0, row = 0, sticky='w')
Button(render_options, text="Leaf-Only Mode", command=lambda: render_tasklist_lr("L")).grid(column = 1, row = 0)
Button(render_options, text="Root-Only Mode", command=lambda: render_tasklist_lr("R")).grid(column = 2, row = 0)
Button(render_options, text="All Tasks", command=render_tasklist_h).grid(column = 3, row = 0)

Label(render_options, text="View Subtasks Of:").grid(column = 0, row = 1, sticky='w')
v_name = Entry(render_options)
v_name.grid(column=1,row=1, sticky='w')
Button(render_options, text="Change View", command=lambda: render_tasklist_h(task=v_name.get())).grid(column = 2, row = 1)

Label(render_options, text="Clear All:").grid(column = 0, row = 2, sticky='w')
Button(render_options, text="Clear", command=clear_tasklist).grid(column = 1, row = 2, sticky='w')

add_task_options = Frame(master)
add_task_options.grid(column=0,row=2, pady=20, sticky='w')
Label(add_task_options, text="Add New Task", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

Label(add_task_options, text="Task Name:").grid(column=0,row=1,sticky='w')
a_name = Entry(add_task_options)
a_name.grid(column=1,row=1, sticky='w', padx=20)
a_invalid_name = Label(add_task_options,text="")
a_invalid_name.grid(column=2,row=1, sticky='w', padx=20)

Label(add_task_options, text="Weight:").grid(column=0,row=2,sticky='w')
a_weight = Entry(add_task_options)
a_weight.grid(column=1,row=2, sticky='w', padx=20)
a_invalid_weight= Label(add_task_options,text="")
a_invalid_weight.grid(column=2,row=2, sticky='w', padx=20)

Label(add_task_options, text="Parent Task:").grid(column=0,row=3,sticky='w')
a_parent = Entry(add_task_options)
a_parent.grid(column=1,row=3, sticky='w', padx=20)
a_invalid_parent = Label(add_task_options,text="")
a_invalid_parent.grid(column=2,row=3, sticky='w', padx=20)

add_task_flags = [a_invalid_name, a_invalid_weight, a_invalid_parent]

def reset_errors(flags: list[Label]):
    """
    Reset error flags provided in list.
    """
    for flag in flags:
        flag.config(text="")

def add_task(name: str, weight: str, parent: str):
    reset_errors(add_task_flags)
    valid_task = True
    if not name:
        a_invalid_name.config(text="Task name must be non-empty")
        valid_task = False
    elif util.is_strint(name):
        a_invalid_name.config(text="Task name cannot be an integer")
        valid_task = False
    elif core.task_exists(name):
        a_invalid_name.config(text="Task with this name already exists")
        valid_task = False
    if not util.is_strint(weight) or int(weight) < 0:
        a_invalid_weight.config(text="Weight must be non-negative")
        valid_task = False
    if not core.task_exists(parent) and parent:
        a_invalid_parent.config(text="Task with this name does not exist")
        valid_task = False
    #Empty string (meaning no entry) implies no task parent
    if not parent:
        parent = None
    if valid_task:
        #Add task
        core.add_task(name, int(weight), 0, parent)
        #Update weights of all higher-level tasks.
        core.set_weight(parent,0)
        #Re-render the tasklist to see changes
        render_tasklist()

Button(add_task_options, text="Add Task", command=lambda: add_task(a_name.get().strip(),a_weight.get(),a_parent.get().strip())).grid(column=0, row=4, sticky= "w")

remove_task_options = Frame(master)
remove_task_options.grid(column=0,row=3, pady=20, sticky='w')
Label(remove_task_options, text="Remove Task", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

Label(remove_task_options, text="Task Name:").grid(column=0,row=1,sticky='w')
r_name = Entry(remove_task_options)
r_name.grid(column=1,row=1, sticky='w', padx=20)
r_invalid_name = Label(remove_task_options,text="")
r_invalid_name.grid(column=2,row=1, sticky='w', padx=20)

def remove_task(name: str):
    reset_errors([r_invalid_name])
    valid_task = True
    if not name:
        r_invalid_name.config(text="A task name is required")
        valid_task = False
    elif util.is_strint(name):
        r_invalid_name.config(text="Task name should not be an integer")
        valid_task = False
    elif not core.task_exists(name):
        r_invalid_name.config(text="Task with this name does not exist")
        valid_task = False
    if valid_task:
        children = [child for child in core.get_children(name)]
        parent = core.get_parent(name)
        removal_message = f"Remove {name}?"
        if len(children) > 1:
            removal_message += f"\n{len(children)} tasks ({', '.join(children)}) will be reassigned as " + ("root tasks." if not parent else f"children of task {parent}.")
        elif len(children) == 1:
            removal_message += f"\n1 task ({children[0]}) will be reassigned as " + ("a root task." if not parent else f"a child of task {parent}.")
        if mb.askokcancel(f"Remove {name}?", removal_message):
            core.remove_task(name)
            #Update parent weights. 0 as weight argument sets parent weight to 0 if previously remvoed task was its last child - NOTE: may add a config option to allow users to opt between this and parent inheriting last child's weight
            core.set_weight(parent,0)
            #After adding, we need to re-render the tasklist to see changes
            render_tasklist()

Button(remove_task_options, text="Remove Task", command=lambda: remove_task(r_name.get().strip())).grid(column=0, row=2, sticky= "w")

#Attempting to close either window should trigger both to close
master.protocol("WM_DELETE_WINDOW", shutdown)
tasks.protocol("WM_DELETE_WINDOW", shutdown)
