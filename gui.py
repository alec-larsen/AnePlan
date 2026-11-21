from tkinter import *
from tkinter.ttk import *

import core

#Initialize control panel
master = Tk()
master.geometry("400x80")
master.title("AneTask Control Panel")

Label(master, text="Tasklist Rendering Options:").grid(column = 0, row = 0)

tasks = Tk()
tasks.geometry("400x300")
tasks.title("AneTasklist")

def clear_window(window):
    for w in window.winfo_children():
        w.destroy()

def render_tasklist_l():
    clear_window(tasks)
    leaf_ids = core.get_leafs()
    for index, id in enumerate(leaf_ids):
        Label(tasks, text=core.task_str(id)).grid(column = 0, row = index, sticky = 'w')

def render_tasklist_r():
    """
    Print current tasklist in root-only format.
    """
    clear_window(tasks)
    root_ids = core.get_root_tasks()
    for index, id in enumerate(root_ids):
        Label(tasks, text=core.task_str(id)).grid(column = 0, row = index, sticky = 'w')

Button(master, text="Leaf-Only Mode", command=render_tasklist_l).grid(column = 1, row = 0)
Button(master, text="Root-Only Mode", command=render_tasklist_r).grid(column = 2, row = 0)

master.mainloop()
