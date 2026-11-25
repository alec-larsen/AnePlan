from core import conn
import util

def fetch_roots():
    """
    Fetch list of all root tasks (tasks with no parents) from database
    """
    results = conn.execute("""
    SELECT name
    FROM tasks
    WHERE parent is NULL
    """).fetchall()
    return [Task(res[0]) for res in results]

def fetch_leafs():
    """
    Fetch list of all leaf tasks (tasks with no children)
    """
    #Fetch the parents of each task in the database
    parents = conn.execute("""
        SELECT parent
        FROM tasks
        """).fetchall()
    #Fetch the names of all tasks
    tasks = conn.execute("""
        SELECT name
        FROM tasks
    """).fetchall()
    #Childless tasks are those whose name shows up in tasks but not in parents
    return [Task(name[0]) for name in tasks if name[0] not in [par[0] for par in parents]]

def clear_list():
    """
    Removes all tasks from tasklist.
    """
    #Remove task from database
    conn.execute("""DELETE FROM tasks""")
    conn.commit()

class Task():
    """
    Contains all relevant information on a given task.

    NOTE (for developers):
    The existence of a Task object does NOT imply that a task with its name exists in the database (tasks.db).
    This is why initializing a task does not check for existence.
    """
    def __init__(self, name: str|None):
        #Name should be string value (None only for SUPERTASK)
        if not isinstance(name, str) and name is not None:
            raise TypeError(f"Task name should of of type str; provided argument of type {type(name)}")
        #Remove and leading/trailing whitespace (provided name is not None) and verifiy name validity
        elif name is not None:
            name = name.strip()
            #Check that task name is not empty
            if not name:
                raise ValueError("Task name should not be empty")
            #Name should not be a strint
            if util.is_strint(name):
                raise ValueError("Task name should not be a strint")
        self.name = name

    def __bool__(self):
        """
        A task is considered 'truthy' if it already exists in the database, and 'falsy' otherwise.
        """
        cursor = conn.cursor()
        return cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE name = ?
        """, (self.name,)).fetchone()[0] > 0

    def __eq__(self, task):
        """
        Define equivalence between two tasks, both present in the database
        """
        #Two tasks should never have the same name if both are in the database
        return self.name == task.name

    def __str__(self):
        #If task exists in database, print task details.
        if self:
            return f"{self.name} - {self.completion:.2f}/{self.weight}" + ( " (-%)" if self.weight == 0 else f" ({self.completion/self.weight*100:.2f}%)")
        return f"{self.name} - NOT IN TASK DATABASE"

    def force_load(self):
            """
            Load all data for task from database, regardless of whether locally loaded.
            """
            #Check that task exists the the database
            if not self:
                raise KeyError(f"Task with name '{self.name}' does not exist in the tasklist.")

            #Fetch all task details from database
            parent_name, weight, completion = conn.execute("""
            SELECT *
            FROM tasks
            WHERE name = ?
            """, (self.name,)).fetchone()[1:]
            #Build Task object from name of parent
            parent = Task(parent_name) if parent_name is not None else SUPERTASK
            #Assign loaded values
            self._weight = weight
            self._completion = completion
            self._parent = parent
            #Mark that task is now loaded
            self._loaded = True

    def rename(self, new_name):
        """
        Assign task a new name.
        """
        #Add new taskwith new name
        renamed_task = Task(new_name)
        #Assign all other properties of previous task to new task
        renamed_task.add(self.weight, self.completion, self.parent)
        #Update parent field of all children with new name
        for child in self.fetch_children():
            child.parent = renamed_task
        #Delete outdated task
        self.remove()

    @property
    def weight(self):
        """
        Fetch the weight of the task from the database
        """
        self.force_load()
        return self._weight

    @weight.setter
    def weight(self, weight: int):
        """
        Set task weight.

        NOTE: Only leaf tasks keep their weight. All higher-level tasks have a weight equal to the sum of their children.
        """
        #Changing the weight of a task will change the weights of all its direct ancestors
        while self is not SUPERTASK:
            children = self.fetch_children()
            #Any weight of a non-leaf task is the sum of its children's weights; if task has no children, it's a leaf and should be assigned the set weight
            agg_weight = sum([child.weight for child in children]) if children else weight
            #Update weight in database
            conn.execute("""
            UPDATE tasks
            SET weight = ?
            WHERE name = ?
            """, (agg_weight,self.name))
            self = self.parent
        #Commit operations to database
        conn.commit()
    
    @property
    def parent(self):
        """
        Fetch the parent of a task from the database
        """
        self.force_load()
        return self._parent

    @property
    def completion(self):
        """
        Fetch the completion of a task from the database.
        """
        self.force_load()
        return self._completion
    
    @parent.setter
    def parent(self, parent: Task):
        """
        Set task parent.

        Note that parents should not be set in such a way that a loop of parent-child relationships forms. Input handlers in gui protect from these cases.
        """
        old_parent = self.parent
        conn.execute("""
        UPDATE tasks
        SET parent = ?
        WHERE name = ?
        """, (parent.name,self.name))
        conn.commit()
        #This parent reassignment changes the weight and completion of both the old and new parent
        parent.weight = 0
        old_parent.weight = 0
        parent.completion = 0
        old_parent.completion = 0

    @completion.setter
    def completion(self, completion: float):
        """
        Set task completion.

        NOTE: Only leaf tasks keep their completion. All higher-level tasks have a completion equal to the sum of their children.
        """
        #Changing the completion of a task will change the completions of all its direct ancestors
        while self is not SUPERTASK:
            children = self.fetch_children()
            #Any completion of a non-leaf task is the sum of its children's completions; if task has no children, it's a leaf and should be assigned the set completion
            agg_comp = sum([child.completion for child in children]) if children else completion
            #Update completion in database
            conn.execute("""
            UPDATE tasks
            SET completion = ?
            WHERE name = ?
            """, (agg_comp,self.name))
            self = self.parent
        #Commit operations to database
        conn.commit()

    def fetch_children(self):
        """
        Fetch a list of all tasks with a given parent
        """
        #Confirm if SUPERTASK has explicitly been passed into fetch_children to trigger fetch_roots
        if self is SUPERTASK:
            return fetch_roots()
        #If SUPERTASK was not explicitly passed, treat Task argument as being from a normal parent
        results = conn.execute("""
            SELECT name
            FROM tasks
            WHERE parent = ?
            """, (self.name,)).fetchall()
        return [Task(res[0]) for res in results]

    def in_cycle(self, parent: Task):
        """
        Check whether assigning new parent to task forms a cycle.
        """
        #Traverse up task tree looking for a root task (parent is None)
        while parent is not SUPERTASK:
            #If parent is the original task, we have found a cycle.
            if parent == self:
                return True
            #Move up a step on the task tree
            parent = parent.parent

        return False

    def update_weight(self):
        """
        Update weight of task and, by consequence, all of its direct ancestors.

        This function is intended to be called on parent tasks only and exists purely for code readability
        """
        self.weight = 0

    def add(self, weight: int = 1, completion: float = 0, parent: Task = None):
        """
        Add task to database.
        """
        if self:
            raise KeyError(f"Task with name '{self.name}' already exists")
        if not isinstance(weight, int):
            raise ValueError("Task could not be added. Assigned weight must be an integer.")
        if not isinstance(completion, (int, float)):
            raise ValueError("Task could not be added. Completion must be an integer or float.")
        if completion > weight:
            raise ValueError("Task could not be added. Completion cannot exceed assigned task weight.")
        conn.execute("""
        INSERT INTO tasks (name, parent, weight, completion)
        VALUES (?,?,?,?)
        """, (self.name, parent.name, weight, completion))
        conn.commit()
        #Addition of task affects parent's weight
        parent.update_weight()

    def remove(self):
        """
        Remove task from database.

        All children of task become children of deleted task's parent.
        """
        #Get parent of task to be deleted.
        parent = self.parent

        #Any children of task become children of parent.
        children = self.fetch_children()
        for child in children:
            child.parent = parent

        #Remove task from database
        conn.execute("""
        DELETE
        FROM tasks
        WHERE name = ?
        """, (self.name,))
        conn.commit()
        #Removal of task affects parent's weight
        parent.update_weight()

#This is, for practical purposes, the parent of all root tasks.
SUPERTASK = Task(None)
