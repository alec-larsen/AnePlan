from core import conn

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
class Task():
    """
    Contains all relevant information on a given task.

    NOTE (for developers): The existence of a Task object does NOT imply that a task with its name exists in the database (tasks.db).
    """
    def __init__(self, name: str):
        self.name = name
        self._loaded = False

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
            return f"{self.name} - {self.completion:.2f}/{self.weight}" + ( "(-%)" if self.weight == 0 else f" {self.completion/self.weight*100:.2f}%")
        return f"{self.name} - NOT IN TASK DATABASE"

    def load(self):
        """
        Load all data for task if not already in local memory.
        """
        #Check that task exists the the database
        if not self:
            raise KeyError(f"Task with name '{self.name}' does not exist.")
        #Load only if task data was not previously loaded into local memory
        if not self._loaded:
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

    @property
    def weight(self):
        """
        Fetch the weight of the task from the database

        If the given task does not exist in the database, return -1
        """
        self.load()
        return self._weight
    
    @property
    def parent(self):
        """
        Fetch the parent of a task from the database
        """
        self.load()
        return self._parent

    @property
    def completion(self):
        """
        Fetch the completion of a task from the database.
        """
        self.load()
        return self._completion

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
        print(results)
        return [Task(res[0]) for res in results]

#This is, for practical purposes, the parent of all root tasks.
SUPERTASK = Task(None)
