def is_strint(n: str):
    """
    Check whether a given string represents an integer.
    """
    try:
        int(n)
        return True
    except:
        return False

def is_strfloat(n: str):
    """
    Check whether a given string represents a number (float or int).
    """
    try:
        float(n)
        return True
    except:
        return False
