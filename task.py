from core import conn

class Task():
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
            parent = Task(parent_name)
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
