import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np
def test():
    fig = Figure(figsize=(5, 4), dpi=100)
    t = np.arange(0, 3, .01)
    fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

    canvas = FigureCanvasTkAgg(fig, master=random)  # A tk.DrawingArea.
    canvas.draw()
    return canvas.get_tk_widget().grid()

root = tkinter.Tk()
root.wm_title("Embedding in Tk")

random = tkinter.Frame(root)
random.grid(row=0,column=0)
fig = test()




tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.