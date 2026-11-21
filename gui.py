from tkinter import *
import tkinter.font as font
import tkinter.messagebox as mb
from tkinter.ttk import *

import core
import util

STATE = {
    "render_mode": "L",
}

#Initialize control panel
master = Tk()
master.geometry("400x600")
master.title("AneTask Control Panel")

tasks = Tk()
tasks.geometry("400x300")
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

def task_str(id: int):
    """
    Build string representation of given task with id.

    Note that all float values are rounded to two decimal places.
    """
    #Get task by id and unpack resultant tuple to obtain remaining task details.
    parent, name, weight, completed = core.conn.execute("""
    SELECT *
    FROM tasks
    WHERE id = ?
    """, (id,)).fetchone()[1:]
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
        task_ids = core.get_leafs()
        #Print appropriate table heading
        Label(tasks,text="COMPONENT TASKS",font=FONTS["head"]).grid(column=0,row=0)
    else:
        #If viewing root tasks, ensure mode is set to R for future calls to render_tasklist()
        STATE["render_mode"] = "R"
        #Get all root tasks
        task_ids = core.get_root_tasks()
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
    for index, id in enumerate(task_ids,1):
        task_pieces = task_str(id)
        Label(task_table, text=task_pieces[0]).grid(column = 0, row = index, sticky = 'w')
        Label(task_table, text=task_pieces[1]).grid(column = 1, row = index, sticky = 'e', padx = 20)
        Label(task_table, text=task_pieces[2]).grid(column = 2, row = index, sticky = 'e', padx = 20)

def render_tasklist_h(task: int = None, depth: int = 0, row: int = 0, task_tree = None):
    """
    Render list of all tasks in hierarchy format.
    """
    #Initialize frame widgets in the first pass only.
    if depth == 0:
        clear_window(tasks)
        #If viewing task hierarchy, ensure mode is set to H for future calls to render_tasklist()
        STATE["render_mode"] = "H"
        #Print appropriate table heading
        Label(tasks,text="ALL TASKS",font=FONTS["head"]).grid(column=0,row=0)
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
        render_tasklist_h()
        #TODO: implement render_tasklist_h

Label(master, text="Options", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

render_options = Frame(master)
render_options.grid(column=0,row=1)

Label(render_options, text="Tasklist Quickview:").grid(column = 0, row = 0)
Button(render_options, text="Leaf-Only Mode", command=lambda: render_tasklist_lr("L")).grid(column = 1, row = 0)
Button(render_options, text="Root-Only Mode", command=lambda: render_tasklist_lr("R")).grid(column = 2, row = 0)
Button(render_options, text="All Tasks", command=lambda: render_tasklist_h()).grid(column = 3, row = 0)

#TODO: Implement tasklist clearing
#Label(render_options, text="Clear All:").grid(column = 0, row = 1, sticky='w')
#Button(render_options, text="Clear", command=lambda: render_tasklist_lr("L")).grid(column = 1, row = 1, sticky='w')

add_task_options = Frame(master)
add_task_options.grid(column=0,row=2, pady=20, sticky='w')
Label(add_task_options, text="Add New Task", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

Label(add_task_options, text="Task Name:").grid(column=0,row=1,sticky='w')
name = Entry(add_task_options)
name.grid(column=1,row=1, sticky='w', padx=20)
invalid_name = Label(add_task_options,text="")
invalid_name.grid(column=2,row=1, sticky='w', padx=20)

Label(add_task_options, text="Weight:").grid(column=0,row=2,sticky='w')
weight = Entry(add_task_options)
weight.grid(column=1,row=2, sticky='w', padx=20)
invalid_weight= Label(add_task_options,text="")
invalid_weight.grid(column=2,row=2, sticky='w', padx=20)

Label(add_task_options, text="Parent Task:").grid(column=0,row=3,sticky='w')
parent = Entry(add_task_options)
parent.grid(column=1,row=3, sticky='w', padx=20)
invalid_parent = Label(add_task_options,text="")
invalid_parent.grid(column=2,row=3, sticky='w', padx=20)

def reset_add_task_errors():
    """
    Reset error flags for adding task
    """
    invalid_name.config(text="")
    invalid_weight.config(text="")
    invalid_parent.config(text="")

def add_task(name: str, weight: str, parent: str):
    reset_add_task_errors()
    valid_task = True
    if not name:
        invalid_name.config(text="Task name must be non-empty")
        valid_task = False
    elif util.is_strint(name):
        invalid_name.config(text="Task name cannot be an integer")
        valid_task = False
    elif core.task_exists(name):
        invalid_name.config(text="Task with this name already exists")
        valid_task = False
    if not util.is_strint(weight) or int(weight) <= 0:
        invalid_weight.config(text="Weight must be a positive integer")
        valid_task = False
    if not core.task_exists(parent) and parent:
        invalid_parent.config(text="Task with this name does not exist")
        valid_task = False
    #Empty string (meaning no entry) implies no task parent
    if not parent:
        parent = None
    else:
        parent = core.fetch_task_id(parent)
    if valid_task:
        core.add_task(name, int(weight), 0, parent)
        #After adding, we need to re-render the tasklist to see changes
        render_tasklist()

Button(add_task_options, text="Add Task", command=lambda: add_task(name.get().strip(),weight.get(),parent.get().strip())).grid(column=0, row=4, sticky= "w")

render_tasklist()

#Attempting to close either window should trigger both to close
master.protocol("WM_DELETE_WINDOW", shutdown)
tasks.protocol("WM_DELETE_WINDOW", shutdown)

master.mainloop()
