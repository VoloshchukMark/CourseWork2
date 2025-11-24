import sys
import os
import tkinter as tk
from tkinter import messagebox
import sys
import os
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class ModelInfoCreatorFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        self.current_file_path = None

        self.create_widgets()
        

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1) 

        picture_Frame = tk.Frame(self, bg="#ffffff")
        picture_Frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        self.btn_select = tk.Button(picture_Frame, text="📂 Choose the file", command=self.select_file, height=2)
        self.btn_select.pack(pady=10)

        self.lbl_path_text = tk.Label(picture_Frame, text="File is not selected", fg="blue")
        self.lbl_path_text.pack()

        self.lbl_preview = tk.Label(picture_Frame, text="Place for a preview", bg="#ddd", padx=5, pady=5)
        self.lbl_preview.pack()
        
        
        self.fields_Frame = tk.Frame(self, bg="#ffffff")
        self.fields_Frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        tk.Label(self.fields_Frame, text="Model's parameters", font=("Arial", 16), 
                bg="#FFFFFF", fg="black").pack(side=tk.TOP, padx=20, pady=5)
        self.entry_model_name = self.create_field(self.fields_Frame, "Model Name:", "entry")
        self.text_description = self.create_field(self.fields_Frame, "Description:", "text")
        self.text_entry_recomended_fabric = self.create_field(self.fields_Frame, "Recommended Fabric:", "text")
        self.text_recomended_accessories = self.create_field(self.fields_Frame, "Recommended Accessories:", "text")
        self.entry_model_price = self.create_field(self.fields_Frame, "Price:", "entry")
        self.check_var_in_stock = self.create_field(self.fields_Frame, "In Stock:", "checkbutton")



    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select your picture",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.current_file_path = file_path
            self.lbl_path_text.config(text=f"Selected: {os.path.basename(file_path)}")
            
            self.show_preview(self.lbl_preview, file_path)
    
    def show_preview(self, widget, path):
        try:
            img = Image.open(path)
            img.thumbnail((200, 200))
            
            tk_img = ImageTk.PhotoImage(img)
            widget.config(image=tk_img, text="")

            widget.image = tk_img
            
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити картинку: {e}")

    def create_field(self, parent, label_text, widget_type):
        frame = tk.Frame(parent, bg="#ffffff")
        frame.pack(pady=10, fill=tk.X)

        label = tk.Label(frame, text=label_text, bg="#ffffff", anchor="w")
        label.pack(side=tk.LEFT, padx=5)

        if widget_type == "entry":
            entry = tk.Entry(frame, width=10)
            entry.pack(side=tk.RIGHT, padx=5, fill="x", expand=True)
            return entry
        elif widget_type == "text":
            text = tk.Text(frame, height=4, width=10)
            text.pack(side=tk.RIGHT, padx=5, fill="x", expand=True)
            return text
        elif widget_type == "checkbutton":
            var = tk.IntVar()
            checkbox = tk.Checkbutton(frame, variable=var, bg="#ffffff")
            checkbox.pack(side=tk.RIGHT, padx=5)
            return var