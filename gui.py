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

def render_tasklist():
    if STATE["render_mode"] == "L":
        render_tasklist_lr("L")
    elif STATE["render_mode"] == "R":
        render_tasklist_lr("R")
    else:
        pass
        #TODO: implement render_tasklist_h

Label(master, text="Options:", font=FONTS["head"]).grid(column=0,row=0)

render_options = Frame(master)
render_options.grid(column=0,row=1)

render_label = Label(render_options, text="Tasklist View:").grid(column = 0, row = 0)
render_leafs = Button(render_options, text="Leaf-Only Mode", command=lambda: render_tasklist_lr("L")).grid(column = 1, row = 0)
render_roots = Button(render_options, text="Root-Only Mode", command=lambda: render_tasklist_lr("R")).grid(column = 2, row = 0)

render_tasklist()
master.mainloop()
