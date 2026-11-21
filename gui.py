from tkinter import *
import tkinter.font as font
from tkinter.ttk import *

import core

STATE = {
    "render_mode": "L"
}

#Initialize control panel
master = Tk()
master.geometry("400x80")
master.title("AneTask Control Panel")

tasks = Tk()
tasks.geometry("400x300")
tasks.title("AneTasklist")

FONTS = {
    "head": font.Font(family="Helvetica", size=12, weight=font.BOLD)
}

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

def render_tasklist_l():
    clear_window(tasks)
    STATE["render_mode"] = "L"
    leaf_ids = core.get_leafs()
    Label(tasks,text="COMPONENT TASKS",font=FONTS["head"]).grid(column=0,row=0)
    task_table = Frame(tasks)
    task_table.grid(column=0,row=1)
    Label(task_table, text="Task Name").grid(column = 0, row = 1, sticky = 'w')
    Label(task_table, text="Progress").grid(column = 1, row = 1, sticky = 'e', padx = 20)
    Label(task_table, text="Percent Completed").grid(column = 2, row = 1, sticky = 'e', padx = 20)
    for index, id in enumerate(leaf_ids,2):
        task_pieces = task_str(id)
        Label(tasks, text=task_pieces[0]).grid(column = 0, row = index, sticky = 'w')
        Label(tasks, text=task_pieces[1]).grid(column = 1, row = index, sticky = 'e', padx = 20)
        Label(tasks, text=task_pieces[2]).grid(column = 2, row = index, sticky = 'e', padx = 20)

def render_tasklist_r():
    """
    Print current tasklist in root-only format.
    """
    clear_window(tasks)
    #This function only runs if R mode is already active or user requests switching to R mode.
    STATE["render_mode"] = "R"
    root_ids = core.get_root_tasks()
    Label(tasks,text="ROOT TASKS",font=FONTS["head"]).grid(column=0,row=0)
    task_table = Frame(tasks)
    task_table.grid(column=0,row=1)
    Label(task_table, text="Task Name").grid(column = 0, row = 1, sticky = 'w')
    Label(task_table, text="Progress").grid(column = 1, row = 1, sticky = 'e', padx = 20)
    Label(task_table, text="Percent Completed").grid(column = 2, row = 1, sticky = 'e', padx = 20)
    for index, id in enumerate(root_ids,2):
        task_pieces = task_str(id)
        Label(task_table, text=task_pieces[0]).grid(column = 0, row = index, sticky = 'w')
        Label(task_table, text=task_pieces[1]).grid(column = 1, row = index, sticky = 'e', padx = 20)
        Label(task_table, text=task_pieces[2]).grid(column = 2, row = index, sticky = 'e', padx = 20)

def render_tasklist():
    if STATE["render_mode"] == "L":
        render_tasklist_l()
    elif STATE["render_mode"] == "R":
        render_tasklist_r()
    else:
        pass
        #TODO: implement render_tasklist_h

Label(master, text="Options:", font=FONTS["head"]).grid(column=0,row=0)

render_options = Frame(master)
render_options.grid(column=0,row=1)

render_label = Label(render_options, text="Tasklist View:").grid(column = 0, row = 0)
render_leafs = Button(render_options, text="Leaf-Only Mode", command=render_tasklist_l).grid(column = 1, row = 0)
render_roots = Button(render_options, text="Root-Only Mode", command=render_tasklist_r).grid(column = 2, row = 0)

render_tasklist()
master.mainloop()
