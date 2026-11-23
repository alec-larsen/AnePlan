import core
import gui
import struct

if __name__ == "__main__":
    #Render the tasklist at runtime
    core.setup()
    gui.render_tasklist()
    gui.master.mainloop()
