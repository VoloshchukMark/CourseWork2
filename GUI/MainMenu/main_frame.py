import sys
import os
import tkinter as tk

from Utils import tkinter_general
from GUI.MainMenu.catalog import CatalogView
from GUI.MainMenu.account import AccountView

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


# --- Фрейми-заглушки для прикладу (Створіть окремі файли для них пізніше) ---

class InfoView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        tk.Label(self, text="Інформація про ательє", font=("Arial", 20)).pack(pady=50)

# --- Головний клас ---
class MainFrameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6ccff")
        self.controller = controller


        self.controller.title("Atelier")
        tkinter_general.center_window(self.controller, 1200, 800) 

        # 1. Створюємо загальний контейнер
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        self.editor_window = None

        # 2. Створюємо статичний Хедер (він створюється лише 1 раз)
        self.create_header()

        # 3. Створюємо контейнер для динамічного контенту (туди будемо пхати Catalog, Info...)
        self.content_area = tk.Frame(self.container, bg="white")
        self.content_area.pack(fill="both", expand=True)

        # 4. Завантажуємо стартову сторінку (наприклад, Каталог)
        self.switch_content(CatalogView)

    def create_header(self):
        header_frame = tk.Frame(self.container, bg="#e6ccff", height=100)
        header_frame.pack(fill=tk.X, pady=0) # pady прибрали, щоб було щільно, або залиште за смаком

        # Логотип
        tk.Label(header_frame, text="Atelier", font=("Arial", 24, "bold"), bg="#e6ccff", fg="purple").pack(side=tk.LEFT, padx=20, pady=5)

        # Кнопки навігації (Зверніть увагу на command)
        self.create_nav_button(header_frame, "Catalog", lambda: self.switch_content(CatalogView), side=tk.LEFT)
        self.create_nav_button(header_frame, "Info", lambda: self.switch_content(InfoView), side=tk.LEFT)
        self.create_nav_button(header_frame, "Editor", command=self.open_editor, side=tk.LEFT)
        
        self.create_nav_button(header_frame, "Account", lambda: self.switch_content(AccountView), side=tk.RIGHT)
        self.create_nav_button(header_frame, "My Orders", lambda: print("Orders clicked"), side=tk.RIGHT)

    def create_nav_button(self, parent, text, command, side):
        """Допоміжний метод для створення кнопок, щоб не дублювати код"""
        btn = tk.Button(parent, text=text, font=("Arial", 14), bg="white", fg="black",
                        activebackground="#d1b3ff", activeforeground="black",
                        borderwidth=0, cursor="hand2",
                        command=command)
        btn.pack(side=side, padx=10, pady=10)

    def switch_content(self, frame_class):
        """
        Метод для заміни контенту в центральній частині.
        """
        # 1. Видаляємо все, що зараз є в content_area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # 2. Створюємо новий фрейм
        # Передаємо self.content_area як parent, щоб він вклався в правильне місце
        new_frame = frame_class(self.content_area, self.controller)
        new_frame.pack(fill="both", expand=True)
        
        # Зберігаємо посилання на поточний фрейм, якщо треба
        self.current_content_frame = new_frame
    
    def open_editor(self):
        """Відкриває вікно редактора"""
        from GUI.Editor.editor_frame import EditorFrameView

        if self.editor_window is None or not self.editor_window.winfo_exists():
            self.editor_window = EditorFrameView() # Зберігаємо в self!
        else:
            self.editor_window.lift() # Піднімаємо наверх, якщо вже відкрито
            self.editor_window.focus_set()

