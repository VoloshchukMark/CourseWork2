import tkinter as tk

from GUI.Authentication.login import LoginView
from GUI.MainMenu.main_frame import MainFrameView

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Atelier")
        self.geometry("500x700")
        self.resizable(False, False)

        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        self.current_frame = None

        self.switch_frame(LoginView)

    def switch_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_class(self.container, self)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
