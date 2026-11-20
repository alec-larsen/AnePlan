import core
import util

def add_task():
    """
    Interface for adding a task, accepting task name, weight, completed weight and optional parent task id.
    """
    #Get task name
    while True:
        name = input("Please give task name (all leading and trailing whitespaces will be removed): ").strip()
        #Check if task name is empty
        if not name:
            print("The task must have a name. Please input a different name.")
        #Check if task with the given name already exists
        elif core.task_exists(name):
            print("A task with this name already exists. Please input a different name.")
        #Task name cannot be the string representation of an integer.
        elif util.is_strint(name):
            print("The task name must have at least one non numeric character. Please input a different name.")
        #If all checks pass, name is accepted
        else:
            break
    #Get task weight
    while True:
        weight = input("How many units of weight is this task worth (must be integer)? ")
        #Check that inputted value is an integer.
        if not util.is_strint(weight):
            print("Non-integer weights are not supported. Please input an integer weight.")
            continue
        else:
            weight = int(weight)
        #Check that weight is positive
        if weight < 1:
            print("Weight must be a positive integer. Please input a new weight.")
        #If both checks pass, weight is accepted.
        else:
            break
    #Get completed weight
    while True:
        completed = input("How many units of weight for this task have already been completed (fractional weights are accepted)? ")
        #Check that inputted value is a number
        if not util.is_strfloat(completed):
            print("Input is not recognizable as a number. Please input an numerical completion value.")
            continue
        else:
            completed = float(completed)
        #Check that completion is non-negative.
        if completed < 0:
            print("Completion must be non-negative. Please input a new completion value.")
        #Completion should not be greater than the task weight
        elif completed > weight:
            print("Completion must not exceed assigned task weight. Please input a new completion value.")
        else:
            break
    while True:
        parent = input("What is the integer task id OR name of the parent task (type 0 for no parent)? ").strip()
        #If parent is the string representation of an integer, user is searching by integer id. Cast to int
        if util.is_strint(parent):
            parent = int(parent)
            if parent < 0:
                print("Integer task id must be positive (or 0 for no parent). Please input a positive integer task id or reference parent by task name.")
                continue
            elif parent == 0:
                parent  = None
        #Check that parent task referenced by id or name exists
        if not core.task_exists(parent) and parent is not None:
            print("No task with specified id or name exists. Try a different id or name or input 0 for no parent.")
        #If parent is found or 0 was inputted, parent is accepted.
        else:
            #If parent is a string, convert to integer task id
            if isinstance(parent, str):
                parent = core.fetch_task_id(parent)
            break
    core.add_task(name, weight, completed, parent)

def render_tasklist_h(task: int = None, depth: int = 0):
    """
    Print current tasklist in hierarchical format.

    task (int): Root task of tree to render. Default None renders all tasks.
    depth (int): Current depth of task being printed in tree. Recursion argument; should NOT be modifed.
    """
    for subtask in core.get_children(task):
        print(' '*4*depth + core.task_str(subtask))
        #Recursively call rendering from subtask. Increase depth by 1
        render_tasklist_h(subtask, depth+1)
    
def render_tasklist_l():
    """
    Print current tasklist in leaf-only format.
    """
    leaf_ids = core.get_leafs()
    for id in leaf_ids:
        print(core.task_str(id))

def render_tasklist_r():
    """
    Print current tasklist in root-only format.
    """
    root_ids = core.get_root_tasks()
    for id in root_ids:
        print(core.task_str(id))

def render_tasklist():
    """
    Print current tasklist. Accepts three primary formats:

    H: Hierarchical - All tasks outputted, subtasks indented past parent task
    L: Leaf only - Prints only leaf tasks (those without any subtasks/children)
    R: Root only - Prints only root tasks (those with no parent tasks)
    """
    while True:
        print("Render from the following formats:")
        print("H: Hierarchical - All tasks outputted, subtasks indented past parent task (default format)")
        print("L: Leaf only - Prints only leaf tasks (those without any subtasks/children)")
        print("R: Root only - Prints only root tasks (those with no parent tasks)")
        format = input("> ").strip().upper()
        if format in ['H','L','R']:
            break
        confirm = input("Invalid format entered - defaulting to 'H'. If this is OK, please type 'Y' (all other inputs will be marked as 'no'): ")
        if confirm.strip().upper() == 'Y':
            break
        print("Default option rejected. Returning to format selection...\n")

    if format == 'L':
        print("-"*50 + '\n' + "Leaf tasks" + '\n' + '-'*50)
        render_tasklist_l()
    elif format == 'R':
        print("-"*50 + '\n' + "Root tasks" + '\n' + '-'*50)
        render_tasklist_r()
    #Format is either 'H' or 'H' was accepted as the default format.
    else:
        print("-"*50 + '\n' + "Task Hierarchy" + '\n' + '-'*50)
        render_tasklist_h()