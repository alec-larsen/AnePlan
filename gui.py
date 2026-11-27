from tkinter import *
import tkinter.font as font
import tkinter.messagebox as mb
from tkinter.ttk import *

from core import _ROOT_DIRECTORY
from task import *
import util

STATE = {
    "render_mode": "H", #Current mode tasklist renders in (Leaf-Only, Root-Only, Hierarchy)
    "head_task": SUPERTASK, #Task whose subtasks are rendered in hierarchy view. None renders all tasks.
    "show_completed": True
}

#Initialize control panel
master = Tk()
master.iconbitmap(str(_ROOT_DIRECTORY) + "/assets/AnePlanL.ico")
master.geometry("530x600")
master.title("AneTask Control Panel")

tasks = Toplevel()
tasks.iconbitmap(str(_ROOT_DIRECTORY) + "/assets/AnePlanL.ico")
tasks.geometry("500x800")
tasks.title("AneTasklist")

#Add canvas, which we can use to attach scrollbar.
canvas = Canvas(tasks,width=500,height=800)
canvas.pack(anchor="nw",side="left",fill="both", expand=True)

#Add scrollbar; pack arguments keep bar on right side
scroll_controls = Scrollbar(tasks,orient="vertical",command=canvas.yview)
scroll_controls.pack(side="right",fill="y")

canvas.configure(yscrollcommand=scroll_controls.set)

#Build frame that will contain all main content of tasklist
tasks_content = Frame(canvas)
#Attach frame to canvas
canvas.create_window((0,0),window=tasks_content,anchor="nw")
#Bind scrollbar movement and mousewheel scrolling to canvas
tasks_content.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))

FONTS = {
    "head": font.Font(family="Helvetica", size=14, weight=font.BOLD),
    "subhead": font.Font(family="Helvetica", size=12, weight=font.BOLD)
}

def toggle_show_completed():
    """
    Flip state of show_completed and re-render checklist to update view
    """
    STATE["show_completed"] = not STATE["show_completed"]
    refresh_tasklist()

def shutdown():
    """
    Confirm user exit and close both AneTask windows.
    """
    if mb.askokcancel("Exit", "Exit AneTask?\nThis will close both the control panel and tasklist."):
        tasks.destroy()
        master.destroy()

def task_line(task: Task):
    """
    Build string representations of root/leaf view table row for task.

    Note that all float values are rounded to two decimal places.
    """
    if task.weight == 0:
        return[f"{task.name}", f"{task.completion:.2f}/{task.weight}", f"-%"]
    else:
        return[f"{task.name}", f"{task.completion:.2f}/{task.weight}", f"{task.completion/task.weight*100:.2f}%"]

def clear_window(window):
    for w in window.winfo_children():
        w.destroy()
    #Force update to ensure all processes after this get updated information on layout (required height, no widgets, etc.)
    master.update_idletasks()

def render_tasklist_lr(mode: str):
    """
    Render list of all root/leaf tasks, depending on mode selected.

    mode L: render all leaf tasks (tasks with no children)
    mode R: render all root tasks (tasks with no parent)
    """
    clear_window(tasks_content)
    total_completion = sum([root.completion for root in fetch_roots()])
    total_weight = sum([root.weight for root in fetch_roots()])
    percent_complete = " (-%)" if total_weight == 0 else f" ({total_completion/total_weight*100:.2f}%)"
    if mode == "L":
        #If viewing leaf tasks, ensure mode is set to L for future calls to render_tasklist()
        STATE["render_mode"] = "L"
        #Get all leaf tasks
        tasks = fetch_leafs()
        #Print appropriate table heading
        Label(tasks_content,text="COMPONENT TASKS"+percent_complete,font=FONTS["head"]).pack(side="top")
    else:
        #If viewing root tasks, ensure mode is set to R for future calls to render_tasklist()
        STATE["render_mode"] = "R"
        #Get all root tasks
        tasks = fetch_roots()
        #Print appropriate table heading
        title = Label(tasks_content,text="ROOT TASKS"+percent_complete,font=FONTS["head"])
        title.pack(side="top")
    #Place tasklist in its own frame. This ensures the table heading rendered previously is centered
    task_table = Frame(tasks_content)
    task_table.pack(anchor="nw",side="top")
    #Render column headers
    Label(task_table, text="Task Name").grid(column = 0, row = 0, sticky = 'w')
    Label(task_table, text="Progress").grid(column = 1, row = 0, sticky = 'e', padx = 20)
    Label(task_table, text="Percent Completed").grid(column = 2, row = 0, sticky = 'e', padx = 20)
    #Render rows of task table from fetched tasks
    for index, task in enumerate(tasks,1):
        #Render subtask if show completed is on or task is incomplete
        if task.completion != task.weight or STATE["show_completed"]:
            task_pieces = task_line(task)
            Label(task_table, text=task_pieces[0]).grid(column = 0, row = index, sticky = 'w')
            Label(task_table, text=task_pieces[1]).grid(column = 1, row = index, sticky = 'e', padx = 20)
            Label(task_table, text=task_pieces[2]).grid(column = 2, row = index, sticky = 'e', padx = 20)

def render_tasklist_h(task: Task = SUPERTASK, depth: int = 0, row: int = 0, task_tree = None):
    """
    Render list of all tasks in hierarchy format.
    """
    #Initialize frame widgets in the first pass only.
    if depth == 0:
        #Change head task if this function was called from 'Change View' button.
        STATE["head_task"] = task
        clear_window(tasks_content)
        #If viewing task hierarchy, ensure mode is set to H for future calls to render_tasklist()
        STATE["render_mode"] = "H"
        #If None is passed as argument, render was called on invalid user input
        if task is None:
            Label(tasks_content,text="ERROR: Cannot render tree - invalid task name",font=FONTS["head"]).pack(anchor="center",side="top")
            return
        #Print appropriate table heading
        if task is SUPERTASK:
            total_completion = sum([root.completion for root in fetch_roots()])
            total_weight = sum([root.weight for root in fetch_roots()])
            percent_complete = " (-%)" if total_weight == 0 else f" ({total_completion/total_weight*100:.2f}%)"
            Label(tasks_content,text="ALL TASKS" + percent_complete,font=FONTS["head"]).pack(anchor="center",side="top")
        #If task does not exist, render 'task not found' message.
        elif not task:
            Label(tasks_content,text=f"Task '{task.name}' not found",font=FONTS["head"]).pack(anchor="center",side="top")
        #Else, user is attempting to view subtasks of a specific task.
        else:
            percent_complete = " (-%)" if task.weight == 0 else f" ({task.completion/task.weight*100:.2f}%)"
            Label(tasks_content,text=task.name.upper() + percent_complete,font=FONTS["head"]).pack(anchor="center", side="top")
            #If task has 100% completion, render special message.
            if task.weight == task.completion and not STATE["show_completed"]:
                Label(tasks_content,text="All subtasks completed. Congratulations!").pack(anchor="center", side="left")
                return
        task_tree = Frame(tasks_content)
        task_tree.pack(anchor="nw",side="top")
    #Get all children of current task
    for subtask in task.fetch_children():
        #Render subtask if show completed is on or task is incomplete
        if subtask.completion != subtask.weight or STATE["show_completed"]:
            #Add indent for every level of depth subtask sits at in tree
            Label(task_tree,text='● ' + str(subtask)).grid(column=0,row=row,padx=50*depth,pady=2,sticky="w")
        #Recursively call rendering from subtask. Increase depth by 1
        row = render_tasklist_h(subtask, depth+1, row+1, task_tree)
    return row

def render_tasklist(mode: str, task: Task = STATE["head_task"]):
    if mode == "L":
        render_tasklist_lr("L")
    elif mode == "R":
        render_tasklist_lr("R")
    else:
        STATE["head_task"] = task
        render_tasklist_h(task=STATE["head_task"])
    #Force update of window state to ensure required height is correct
    master.update_idletasks()
    #If the required height to render all content is less than the current window size, scrollbar is not needed
    if tasks_content.winfo_reqheight() < tasks.winfo_height():
        #If the scrollbar is removed, ensure content is at the top of the frame
        canvas.yview_moveto(0)
        scroll_controls.pack_forget()
    #Else, ensure it's properly rendered
    else:
        scroll_controls.pack(side="right",fill="y")

def refresh_tasklist():
    """
    Render tasklist again with current settings.
    """
    render_tasklist(STATE["render_mode"],STATE["head_task"])

def clear_tasklist():
    if mb.askokcancel("Clear all tasks?","This action will clear ALL tasks from the tasklist.\nAre you sure you want to do this?"):
        clear_list()
        refresh_tasklist()

#Options widgets
Label(master, text="Options", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

render_options = Frame(master)
render_options.grid(column=0,row=1,sticky="w")

#Tasklist quickview options
Label(render_options, text="Tasklist Quickview:").grid(column=0,row=0,sticky="w")
quickview_buttons = Frame(render_options)
Button(quickview_buttons, text="Leaf-Only Mode", command=lambda: render_tasklist("L")).pack(side="left",padx=3)
Button(quickview_buttons, text="Root-Only Mode", command=lambda: render_tasklist("R")).pack(side="left",padx=3)
Button(quickview_buttons, text="All Tasks", command=lambda: render_tasklist("H")).pack(side="left",padx=3)
quickview_buttons.grid(column=1,row=0,sticky="w")

#View subtasks option
Label(render_options, text="View Subtasks Of:").grid(column=0,row=1,sticky="w")
subview_row = Frame(render_options)
v_name = Entry(subview_row)
v_name.pack(side="left",padx=3)
Button(subview_row, text="Change View", command=lambda: render_tasklist("H",task= None if util.is_strint(v_name.get().strip()) or not v_name.get().strip() else Task(v_name.get().strip()))).pack(side="left",padx=3)
subview_row.grid(column=1,row=1,sticky="w")

#Clear all option
Label(render_options, text="Clear All:").grid(column=0,row=2,sticky="w")
Button(render_options, text="Clear", command=clear_tasklist).grid(column=1,row=2,sticky="w")

#Show completed option
show_completed = IntVar()
Label(render_options, text="Show Completed Tasks?").grid(column=0,row=3,sticky="w")
show_done = Checkbutton(render_options,var=show_completed,onvalue=1,offvalue=0,command=toggle_show_completed)
show_done.grid(column=1,row=3,sticky="w")
show_completed.set(1)


#Add task widgets
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
    #This flag (as opposed to return statements after a single condition fails) ensures all error messages render in the GUI
    valid_task = True

    #Check task name is non-empty
    if not name:
        a_invalid_name.config(text="Task name must be non-empty")
        valid_task = False

    #Check task name is not strint
    elif util.is_strint(name):
        a_invalid_name.config(text="Task name cannot be an integer")
        valid_task = False

    #If task name is valid, check it is not in use by an existing task
    else:
        task = Task(name)
        #Check that task name is not already in use
        if task:
            a_invalid_name.config(text="Task with this name already exists")
            valid_task = False

    #Check inputted weight is valid
    if not util.is_strint(weight) or int(weight) < 0:
        a_invalid_weight.config(text="Weight must be non-negative")
        valid_task = False
    else:
        weight = int(weight)

    #If parent name is empty, task has no parent (i.e. root task)
    if not parent:
        parent = SUPERTASK

    #Check task name is not strint
    elif util.is_strint(parent):
        a_invalid_name.config(text="Task name cannot be an integer")
        valid_task = False

    #If parent was inputted and is valid, check that it names an exiting task in the database.
    else:
        parent = Task(parent)
        if not parent:
            a_invalid_parent.config(text="Task with this name does not exist")
            valid_task = False

    if valid_task:
        #Add task
        task.add(weight, 0, parent)
        #Re-render the tasklist to see changes
        refresh_tasklist()

Button(add_task_options, text="Add Task", command=lambda: add_task(a_name.get(),a_weight.get(),a_parent.get())).grid(column=0, row=4, sticky= "w")

#Modify task widgets
modify_task_options = Frame(master)
modify_task_options.grid(column=0,row=3,pady=20,sticky='w')
Label(modify_task_options, text="Modify Task", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

Label(modify_task_options,text="Current Task Name:").grid(column=0,row=1,stick='w')
m_name_old = Entry(modify_task_options)
m_name_old.grid(column=1,row=1, sticky='w', padx=20)
m_invalid_name_old= Label(modify_task_options,text="")
m_invalid_name_old.grid(column=2,row=1, sticky='w', padx=20)

Label(modify_task_options,text="Change Name:").grid(column=0,row=2,stick='w')
m_name = Entry(modify_task_options)
m_name.grid(column=1,row=2, sticky='w', padx=20)
m_invalid_name = Label(modify_task_options,text="")
m_invalid_name.grid(column=2,row=2, sticky='w', padx=20)

Label(modify_task_options,text="Change Weight:").grid(column=0,row=3,stick='w')
m_weight = Entry(modify_task_options)
m_weight.grid(column=1,row=3, sticky='w', padx=20)
m_invalid_weight = Label(modify_task_options,text="")
m_invalid_weight.grid(column=2,row=3, sticky='w', padx=20)

Label(modify_task_options,text="Update Completion:").grid(column=0,row=4,stick='w')
m_comp = Entry(modify_task_options)
m_comp.grid(column=1,row=4, sticky='w', padx=20)
m_invalid_comp = Label(modify_task_options,text="")
m_invalid_comp.grid(column=2,row=4, sticky='w', padx=20)

Label(modify_task_options,text="Change Parent:").grid(column=0,row=5,stick='w')
m_parent = Entry(modify_task_options)
m_parent.grid(column=1,row=5, sticky='w', padx=20)
m_invalid_parent= Label(modify_task_options,text="")
m_invalid_parent.grid(column=2,row=5, sticky='w', padx=20)

m_task_errors = [m_invalid_name_old, m_invalid_name, m_invalid_weight, m_invalid_comp, m_invalid_parent]

def modify_name(task: Task, name: str):
    """
    Change name of task.
    """
    #Check that name is not a strint
    if util.is_strint(name):
        m_invalid_name.config(text="Task name should not be an integer")
        return
    #Check that new name is not used by any existing task
    if Task(name):
        if name == task.name:
            m_invalid_name.config(text="Task is already named this")
        else:
            m_invalid_name.config(text="Task with this name already exists")
        return
    task.rename(name)

def modify_weight(task: Task, weight: str):
    """
    Change weight of task.
    """
    #Check that inputted weight is valid
    if not util.is_strint(weight) or int(weight) < 0:
        m_invalid_weight.config(text="Weight must be a non-negative integer")
        return
    #Check if task has children. Tasks with children cannot have their weight modified
    if task.fetch_children():
        m_invalid_name_old.config(text="This task has children, which fix its weight")
        return
    #Change weights
    task.weight= int(weight)

def modify_completion(task: Task, completion: str):
    """
    Change completion of task.

    Note that completion may either be a float (less than task weight) or a fraction (less than or equal to 1)
    """
    #If completion is recognizable as a float, it should be an input in terms of task weight units completed
    if util.is_strfloat(completion):
        completion = float(completion)
    #If completion contains a '/', further check to confirm it represents a valid fraction
    elif '/' in completion:
        #Split into components separated by 'division' symbol
        numbers = completion.split('/')
        #If input is recognized as a fraction, it should be a proportion of the total task weight completed.
        if len(numbers) == 2 and util.is_strint(numbers[0]) and util.is_strint(numbers[1]):
            completion = int(numbers[0])/int(numbers[1]) * task.weight
        #Otherwise the input is invalid
        else:
            m_invalid_comp.config(text="This input is not recognizable as a fraction or float")
            return
    #A completion input recognized as neither format is invalid.
    else:
        m_invalid_comp.config(text="This input is not recognizable as a fraction or float")
        return
    #Check that completion is less than the task weight
    if completion > task.weight:
        m_invalid_comp.config(text="Completion should not exceed task weight")
        return
    if task.fetch_children():
        m_invalid_name_old.config(text="This task has children, which fix its completion")
        return
    #If all checks pass, update completion
    task.completion = completion

def modify_parent(task: Task, parent: str):
    """
    Change parent of task.

    Note that parent-children relations are NOT permitted to be cyclical
    """
    #Check that name is not a strint
    if util.is_strint(parent):
        m_invalid_name.config(text="Task name should not be an integer")
        return
    parent = Task(parent)
    #Check that parent exists
    if not parent:
        m_invalid_parent.config(text="Task with this name does not exist")
        return
    #Check that reassignment of parent does not form a closed cycle
    if task.in_cycle(parent):
        m_invalid_parent.config(text="This reassignment forms a cycle of parent-children relations")
        return
    task.parent = parent

def modify_task(task: str, name: str, weight: str, completion: str, parent: str):
    """
    Modify all fields of task with non-empty values provided.
    """
    #Reset relevant error flags
    reset_errors(m_task_errors)

    #Check that task name was inputted
    if not task:
        m_invalid_name_old.config(text="Current name of task to be modified is required")
        return

    #Check that task is not a strint
    if util.is_strint(task):
        m_invalid_name.config(text="Task name should not be an integer")
        return

    task = Task(task)
    #Check that named task exists
    if not task:
        m_invalid_name_old.config(text="Task with this name does not exist")
        return

    #Modify weight if new name was provided
    if weight:
        modify_weight(task, weight)

    #Modify completion if new completion was provided. This must happen after possible weight change
    if completion:
        modify_completion(task, completion)

    #Modify parent if new parent was provided
    if parent:
        modify_parent(task, parent)

    #Modify name if new name was provided. This happens last to avoid the question of whether we pass name or task as the first argument for all other functions
    if name:
        modify_name(task, name)
    
    #Reload tasklist to reflect changes
    refresh_tasklist()

Button(modify_task_options, text="Modify Task", command=lambda: modify_task(m_name_old.get().strip(), m_name.get().strip(), m_weight.get().strip(), m_comp.get().strip(), m_parent.get().strip())).grid(column=0, row=6, sticky= "w")

#Remove task widgets
remove_task_options = Frame(master)
remove_task_options.grid(column=0,row=4, pady=20, sticky='w')
Label(remove_task_options, text="Remove Task", font=FONTS["subhead"]).grid(column=0,row=0,sticky='w')

Label(remove_task_options, text="Task Name:").grid(column=0,row=1,sticky='w')
r_name = Entry(remove_task_options)
r_name.grid(column=1,row=1, sticky='w', padx=20)
r_invalid_name = Label(remove_task_options,text="")
r_invalid_name.grid(column=2,row=1, sticky='w', padx=20)

def remove_task(name: str):
    """
    Remove task with given name from the database
    """
    reset_errors([r_invalid_name])
    valid_task = True

    #Check that task name is given
    if not name:
        r_invalid_name.config(text="A task name is required")
        valid_task = False

    #Check that task name is valid (not strint)
    elif util.is_strint(name):
        r_invalid_name.config(text="Task name should not be an integer")
        valid_task = False

    #Given task name is valid, check that it exists in the database
    else:
        task = Task(name)
        if not task:
            r_invalid_name.config(text="Task with this name does not exist")
            valid_task = False

    #Given that the task exists, begin removal procedures
    if valid_task:
        #Children and parent are needed for removal message formatting
        children = [child.name for child in task.fetch_children()]
        parent = task.parent

        #Format removal message, which states that all of task's children will be assigned to task's parent (or root if it has no parent)
        removal_message = f"Remove {name}?"
        if len(children) > 1:
            removal_message += f"\n{len(children)} tasks ({', '.join(children)}) will be reassigned as " + ("root tasks." if parent is SUPERTASK else f"children of task {parent.name}.")
        elif len(children) == 1:
            removal_message += f"\n1 task ({children[0]}) will be reassigned as " + ("a root task." if parent is SUPERTASK else f"a child of task {parent.name}.")

        #Give user chance to cancel operation in case of an accidental click
        if mb.askokcancel(f"Remove {name}?", removal_message):
            task.remove()
            #After adding, we need to re-render the tasklist to see changes
            refresh_tasklist()

Button(remove_task_options, text="Remove Task", command=lambda: remove_task(r_name.get().strip())).grid(column=0, row=2, sticky= "w")

#Attempting to close either window should trigger both to close
master.protocol("WM_DELETE_WINDOW", shutdown)
tasks.protocol("WM_DELETE_WINDOW", shutdown)
