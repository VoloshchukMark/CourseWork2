import tkinter as tk

from GUI.Authentication.login import LoginView
from GUI.MainMenu.main_frame import MainFrameView
import base64

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

    """
def image_to_code(filepath):
    with open(filepath, "rb") as image_file:
        # 1. Читаємо файл у бінарному режимі
        binary_data = image_file.read()
        # 2. Кодуємо в base64
        base64_encoded = base64.b64encode(binary_data)
        # 3. Перетворюємо байти в звичайний рядок (utf-8)
        base64_string = base64_encoded.decode('utf-8')
        print("Image successfully converted to Base64 string.")
        
    with open("Data/Images/user_icon", "w") as text_file:
        text_file.write(base64_string)
        print("Image converted to Base64 and saved to user_icon file.")
        


image_to_code("user.png")
"""
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

