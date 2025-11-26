import sys
import os
import tkinter as tk

from Utils import tkinter_general
from GUI.Editor.model_info_creator import ModelInfoCreatorFrame
from GUI.Editor.fabric_info_creator import FabricInfoCreatorFrame
from GUI.Editor.tailor_info_creator import TailorInfoCreatorFrame

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


# --- Головний клас ---
class EditorFrameView(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        self.title("Atelier Editor")
        tkinter_general.center_window(self, 800, 800) 
        self.configure()

        # 1. Створюємо загальний контейнер
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        self.create_sidebar()

        self.content_area = tk.Frame(self.container, bg="white")
        self.content_area.pack(fill="both", expand=True)

        #self.switch_content()

    def create_sidebar(self):
        sidebar_frame = tk.Frame(self.container, bg="#e6ccff", width=100)
        sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, pady=0)

        tk.Label(sidebar_frame, text="Atelier Editor", font=("Arial", 20, "bold"), 
                bg="#e6ccff", fg="purple").pack(side=tk.TOP, padx=20, pady=5)

        # Кнопки навігації (Зверніть увагу на command)
        self.create_nav_button(sidebar_frame, "Model Info Creator", lambda: self.switch_content(ModelInfoCreatorFrame), side=tk.TOP)
        self.create_nav_button(sidebar_frame, "Model Info Editor", lambda: self.switch_content(FabricInfoCreatorFrame), side=tk.TOP)
        self.create_nav_button(sidebar_frame, "Model Info Editor", lambda: self.switch_content(TailorInfoCreatorFrame), side=tk.TOP)

    def create_nav_button(self, parent, text, command, side):
        btn = tk.Button(parent, text=text, font=("Arial", 12), bg="#e6ccff", fg="black",
                        activebackground="#e6ccff", activeforeground="#b15d9c",
                        borderwidth=0,  highlightthickness=0, cursor="hand2", anchor="w",
                        command=command)
        btn.pack(side=side, fill=tk.X, padx=10, pady=0)

    def switch_content(self, frame_class):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        new_frame = frame_class(self.content_area, self)
        new_frame.pack(fill="both", expand=True)
        
        self.current_content_frame = new_frame

if __name__ == "__main__":
    app = EditorFrameView()
    app.mainloop()
