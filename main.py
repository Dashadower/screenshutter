import tkinter as tk, threading
from tkinter.colorchooser import askcolor
from pynput.mouse import Controller

APP_NAME = "pyscreenruler"

class TransparentWindow(tk.Toplevel):
    """
    This class is just a Toplevel window.
    """
    def __init__(self, background="white", opacity=0.7):
        super(TransparentWindow, self).__init__()
        #self.master = master
        self.configure(background=background)
        self.overrideredirect(True)
        self.wm_attributes("-alpha", opacity)
        self.wm_attributes("-topmost", True)

        self.lift()

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

        self.geometry("%dx%d+%d+%d"%(right-left, bottom-top, left, top))  # width,height,x_coords,y_coords
        self.update()
        self.lift()

        
class MainWindow(tk.Frame):
    def __init__(self, master, gapsize):
        super(MainWindow, self).__init__(master)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self.top_window = TransparentWindow()
        self.top_window.withdraw()

        self.bottom_window = TransparentWindow()
        self.bottom_window.withdraw()

        self.gapsize = tk.IntVar()
        self.gapsize.set(gapsize)

        self.mouse_controller = Controller()

        self.running = False
        self.stopEvent = None
        self.button_text = tk.StringVar()
        self.button_text.set("start")

        self.window_opacity = tk.IntVar()
        self.window_opacity.set(70)
        self.window_bg_hex = "#ffffff"

        self.draw_widgets()

    def draw_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Button(self, textvariable=self.button_text, command=self.onStart).grid(row=0, column=0)
        self.window_bg_btn = tk.Button(self, text="configure color", bg=self.window_bg_hex, command=self.onConfigureColor)
        self.window_bg_btn.grid(row=0, column=1)

        self.top_window_opacity_scale = tk.Scale(self, from_=10, to=100, label="opacity", orient=tk.HORIZONTAL,
                                                 length=200, resolution=10, showvalue=False, tickinterval=10,variable=self.window_opacity, command=self.onOpacityChange)

        self.top_window_opacity_scale.grid(row=1, column=0, columnspan=2)

        self.window_gap_scale = tk.Scale(self, from_=20, to=300, label="window gap", orient=tk.HORIZONTAL,
                                                 length=200, resolution=10,
                                                 variable=self.gapsize)
        self.window_gap_scale.grid(row=2, column=0, columnspan=2)

    def onOpacityChange(self, event):
        self.top_window.wm_attributes("-alpha", self.window_opacity.get()/100)
        self.bottom_window.wm_attributes("-alpha", self.window_opacity.get()/100)

    def onConfigureColor(self):
        _ , hex = askcolor(title=APP_NAME)
        self.window_bg_hex = hex
        self.top_window.configure(background=hex)
        self.bottom_window.configure(background = hex)
        self.draw_widgets()

    def update_windows(self, stop_event):
        while not stop_event.is_set():
            mouse_coords = self.mouse_controller.position
            self.top_window.update_size(mouse_coords[1], gapsize=self.gapsize.get())
            self.bottom_window.update_size(mouse_coords[1], position="bottom", gapsize=self.gapsize.get())
    
    def onStart(self):
        if self.running:
            self.stopEvent.set()
            self.running = False
            self.button_text.set("start")
            self.top_window.withdraw()
            self.bottom_window.withdraw()

        else:
            self.stopEvent = threading.Event()
            self.stopEvent.clear()
            self.button_text.set("stop")
            self.running = True
            self.top_window.deiconify()
            self.bottom_window.deiconify()
            self.top_window.lift()
            self.bottom_window.lift()
            thread = threading.Thread(target=self.update_windows, args=(self.stopEvent,))
            thread.start()


if __name__ == '__main__':
    root = tk.Tk()
    root.title(APP_NAME)
    root.wm_minsize(width=200, height=1)
    root.wm_attributes("-topmost", True)
    MainWindow(root, gapsize=100)
    root.mainloop()
