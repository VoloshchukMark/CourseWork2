import tkinter as tk
from tkinter import ttk, messagebox
from Utils import mongodb_functions
import threading

class BaseInfoEditorView(tk.Frame):
    def __init__(self, parent, controller, collection_name, creator_class, headers, custom_loader=None):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.collection_name = collection_name
        self.creator_class = creator_class
        self.headers = headers
        self.custom_loader = custom_loader

        # --- Змінні для пагінації ---
        self.current_index = 0
        self.batch_size = 30
        self.is_loading = False
        self.all_loaded = False
        
        # [FIX 1] Додаємо ідентифікатор запиту, щоб відсіювати старі потоки
        self.request_id = 0 

        self.create_widgets()
        
        self.after(100, self.refresh_data)

    def create_widgets(self):
        # Заголовок
        tk.Label(self, text=f"Edit {self.collection_name.capitalize()}", 
                 font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        # Контейнер таблиці
        container = tk.Frame(self, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Canvas + Scrollbar
        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.on_scroll_handler)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.canvas.bind('<Leave>', self._unbind_mouse_wheel)

        # --- ШАПКА (HEADER) ---
        self.header_frame = tk.Frame(self.scrollable_frame, bg="#ddd")
        self.header_frame.pack(fill="x", pady=(0, 2))
        
        for i, (key, title) in enumerate(self.headers):
            width = self.get_column_width(key)
            cell = tk.Frame(self.header_frame, bg="#ddd", width=width*9, height=30)
            cell.pack_propagate(False)
            cell.grid(row=0, column=i, padx=1, pady=1)
            tk.Label(cell, text=title, font=("Arial", 11, "bold"), bg="#ddd").pack(fill="both", expand=True)
        
        cell = tk.Frame(self.header_frame, bg="#ddd", width=120, height=30)
        cell.pack_propagate(False)
        cell.grid(row=0, column=len(self.headers), padx=1, pady=1)
        tk.Label(cell, text="Actions", font=("Arial", 11, "bold"), bg="#ddd").pack(fill="both", expand=True)

        self.loading_label = tk.Label(self, text="Loading data...", 
                                      font=("Arial", 14, "italic"), fg="white", bg="gray50",
                                      padx=20, pady=10, relief="flat")

    def get_column_width(self, key):
        if key == "_id": return 5 
        if "name" in key: return 20
        if "price" in key: return 10
        if "width" in key: return 15
        if "number" in key: return 15 
        if "color" in key: return 20
        if "stock" in key: return 10
        if "supplier" in key: return 20
        if "fabric_supply_amount" in key: return 12
        if "_salary" in key: return 12
        if "address" in key: return 15
        return 25

    # --- ЛОГІКА ЗАВАНТАЖЕННЯ ---

    def refresh_data(self):
        """Повне перезавантаження (скидання таблиці)"""
        
        # [FIX 2] Збільшуємо ID запиту. Будь-які попередні потоки, що завершаться після цього, будуть ігноровані.
        self.request_id += 1 
        
        self.current_index = 0
        self.all_loaded = False
        self.is_loading = False # Скидаємо прапор, щоб дозволити новий запит

        self.show_loading(True)

        for widget in list(self.scrollable_frame.winfo_children()):
            if widget is not self.header_frame:
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
        
        self.canvas.yview_moveto(0)
        self.load_more_rows()

    def load_more_rows(self):
        if self.is_loading or self.all_loaded:
            return

        self.is_loading = True
        
        # [FIX 3] Фіксуємо поточний ID для цього конкретного запуску потоку
        current_req_id = self.request_id
        
        # Передаємо current_req_id у потік
        threading.Thread(target=self._background_loader, args=(current_req_id,), daemon=True).start()

    def _background_loader(self, req_id):
        try: 
            if self.custom_loader:
                data = self.custom_loader(skip=self.current_index, limit=self.batch_size)
            else:
                data = mongodb_functions.get_documents_paginated(
                    self.collection_name, 
                    skip=self.current_index, 
                    limit=self.batch_size, 
                    projection=None
                )
        except Exception as e:
            print(f"DB Error: {e}")
            data = []

        # [FIX 4] Передаємо req_id далі в UI потік
        self.after(0, self._update_ui, data, req_id)

    def _update_ui(self, new_items, req_id):
        # Перевірка, чи вікно ще існує
        if not self.winfo_exists():
            return

        # [FIX 5] ГОЛОВНА ПЕРЕВІРКА: Якщо ID цього запиту старіший за поточний self.request_id,
        # значить був викликаний refresh_data, і цей результат вже неактуальний.
        if req_id != self.request_id:
            return

        self.show_loading(False)
        self.is_loading = False # Звільняємо лок завантаження

        if not new_items:
            self.all_loaded = True
            return

        for item in new_items:
            self.create_row(item)

        self.current_index += len(new_items)
        
        if len(new_items) < self.batch_size:
            self.all_loaded = True

    def create_row(self, item_data):
        row_frame = tk.Frame(self.scrollable_frame, bg="white", bd=1, relief="solid")
        row_frame.pack(fill="x", pady=1)

        for i, (key, title) in enumerate(self.headers):
            width = self.get_column_width(key)
            cell = tk.Frame(row_frame, bg="white", width=width*9, height=35)
            cell.pack_propagate(False)
            cell.grid(row=0, column=i, padx=1)
            
            val = str(item_data.get(key, "-"))
            if len(val) > width - 2: 
                val = val[:width-5] + "..."
            
            tk.Label(cell, text=val, font=("Arial", 11), bg="white", anchor="w").pack(fill="both", expand=True, padx=5)

        action_cell = tk.Frame(row_frame, bg="white", width=120, height=35)
        action_cell.pack_propagate(False)
        action_cell.grid(row=0, column=len(self.headers), padx=1)
        
        btn_container = tk.Frame(action_cell, bg="white")
        btn_container.pack(expand=True)

        tk.Button(btn_container, text="Edit", bg="#df47d8", width=5,
                  command=lambda: self.open_edit_window(item_data)).pack(side="left", padx=2)

        tk.Button(btn_container, text="Del", bg="#a3306a", fg="white", width=5,
                  command=lambda: self.delete_item(item_data)).pack(side="left", padx=2)

    def show_loading(self, show):
        if show:
            self.loading_label.lift()
            self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
            # self.update_idletasks() # Прибрали, щоб не блокувати UI, tkinter сам оновить
        else:
            self.loading_label.place_forget()

    def on_scroll_handler(self, first, last):
        self.scrollbar.set(first, last)
        
        if self.is_loading or self.all_loaded:
            return
        
        if float(last) > 0.9:
            self.load_more_rows()

    def _bind_mouse_wheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse_wheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        elif event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def delete_item(self, item_data):
        if messagebox.askyesno("Confirm", f"Delete item {item_data.get('_id')}?"):
            if mongodb_functions.delete_document(self.collection_name, item_data["_id"]):
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to delete")

    def open_edit_window(self, item_data):
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Edit {self.collection_name}")
        
        editor = self.creator_class(edit_window, self.controller) 
        editor.pack(fill="both", expand=True)
        editor.fill_fields(item_data)
        
        editor.enter_Button.config(text="Accept Changes", 
                                   command=lambda: self.save_changes(editor, edit_window, item_data["_id"]))

    def save_changes(self, editor_frame, window, doc_id):
        new_data = editor_frame.get_data_dict()
        if new_data:
            if new_data.get("image") is None and hasattr(editor_frame, 'original_image_binary'):
                new_data["image"] = editor_frame.original_image_binary
            
            if "_id" in new_data:
                del new_data["_id"]

            success = mongodb_functions.update_document(
                self.collection_name, 
                {"_id": doc_id},       # Query (пошук)
                {"$set": new_data}     # Update (оновлення)
            )

            if success:
                messagebox.showinfo("Success", "Updated successfully")
                window.destroy()
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to update document")