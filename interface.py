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
