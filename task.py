class Task():
    def __init__(self, name: str, parent: str, weight: int, completion: float):
        self._name = name
        self._parent = parent
        self._weight = weight
        self._completion = completion
