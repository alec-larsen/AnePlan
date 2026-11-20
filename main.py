import core
import interface
import struct

def run():
    """"
    Main runtime loop.
    """
    print("AneTask v0.0.0-a")
    while True:
        menu = "The following functionalities are available:\n"
        menu += "1. Add task\n"
        menu += "2. Exit\n"
        choice = input(menu + '> ')
        if choice == '1':
            interface.add_task()
        elif choice == '2':
            return
        else:
            print("Invalid item choice. Please input the number of the choice you would like to select.")

if __name__ == "__main__":
    core.setup()
    run()