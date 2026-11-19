NUMERALS = '1234567890'

def is_strint(n: str):
    """
    Check whether a given string represents an integer.
    """
    return all(digit in NUMERALS for digit in n)

def is_stroat(n: str):
    """
    Check whether a given string represents a number (float or int).
    """
    try:
        float(n)
        return True
    except:
        return False
