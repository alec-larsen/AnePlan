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
