from core import conn

class Task():
    def __init__(self, name: str):
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

    def fetch_weight(self):
        """
        Fetch the weight of the task from the database

        If the given task does not exist in the database, return -1
        """
        if not self:
            raise KeyError(f"Task with name '{self.name}' does not exist.")

        return conn.execute("""
        SELECT weight
        FROM tasks
        WHERE name = ?
        """, (self.name,)).fetchone()[0]
