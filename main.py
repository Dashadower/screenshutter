import tkinter as tk, threading
from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


class TransparentWindow(tk.Toplevel):
    """
    This class is just a Toplevel window.
    """
    def __init__(self, master, *args, **kwargs):
        super(TransparentWindow, self).__init__(master, *args, **kwargs)
        self.master = master
        self.overrideredirect(True)
        self.wm_attributes("-alpha", 0.7)
        self.wm_attributes("-topmost", True)

    def update_size(self, mouse_ycoords, position="top", gapsize=40):
        if position == "top":
            left = 0
            top = 0
            right = self.winfo_screenwidth()
            bottom = max(mouse_ycoords-int(gapsize/2), 1)

        elif position == "bottom":
            left = 0
            top = min(mouse_ycoords+int(gapsize/2), root.winfo_screenheight())
            right = self.winfo_screenwidth()
            bottom = self.winfo_screenheight()

        self.geometry("%dx%d+%d+%d"%(right-left, bottom-top, left, top))  # width,height,x_coords,y_coors
        self.lift()

class MainWindow(tk.Frame):
    def __init__(self, master, gapsize):
        super(MainWindow, self).__init__(master)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self.top_window = TransparentWindow(self)
        self.top_window.withdraw()

        self.bottom_window = TransparentWindow(self)
        self.bottom_window.withdraw()

        self.gapsize = gapsize

        self.running = False
        self.stopEvent = threading.Event()
        self.button_text = tk.StringVar()
        self.button_text.set("start")

        tk.Button(self, textvariable=self.button_text, command=self.onClick).pack()

    def update_windows(self):
        while not self.stopEvent.is_set():
            mouse_coords = queryMousePosition()
            self.top_window.update_size(mouse_coords[1], gapsize=self.gapsize)
            self.bottom_window.update_size(mouse_coords[1], position="bottom", gapsize=self.gapsize)

    def onClick(self):
        if self.running:
            self.stopEvent.set()
            self.running = False
            self.button_text.set("start")
            self.top_window.withdraw()
            self.bottom_window.withdraw()

        else:
            self.stopEvent.clear()
            self.button_text.set("stop")
            self.running = True
            self.top_window.deiconify()
            self.bottom_window.deiconify()
            thread = threading.Thread(target=self.update_windows, args=())
            thread.start()


if __name__ == '__main__':
    root = tk.Tk()
    root.wm_minsize(width=200, height=1)
    root.wm_attributes("-topmost", True)
    MainWindow(root, gapsize=100)
    root.mainloop()
