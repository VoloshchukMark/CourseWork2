import tkinter as tk
from tkinter import ttk

class FabricSelectorWidget(tk.Frame):
    def __init__(self, parent, all_fabrics_map, preselected_str="", bg="white", on_change_callback=None):
        super().__init__(parent, bg=bg)
        self.bg_color = bg
        
        # Беремо ключі зі словника {name: price} і сортуємо
        # Фільтруємо можливі None значення
        clean_keys = [str(k) for k in all_fabrics_map.keys() if k]
        self.all_fabrics_source = sorted(clean_keys)
        
        self.on_change_callback = on_change_callback
        self.selected_fabrics = []

        # -- UI --
        self.selected_container = tk.Frame(self, bg=bg)
        self.selected_container.pack(fill=tk.X, anchor="w")

        self.add_frame = tk.Frame(self, bg=bg)
        self.add_frame.pack(fill=tk.X, pady=(5, 0))

        self.combo_var = tk.StringVar()
        self.combo_add = ttk.Combobox(self.add_frame, textvariable=self.combo_var, state="readonly", font=("Arial", 10))
        self.combo_add.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_add.set("Select Fabric to Add...")
        
        self.combo_add.bind("<<ComboboxSelected>>", self._on_combo_select)

        # -- Ініціалізація даних --
        if preselected_str:
            # Обробляємо і старий формат (рядок), і новий (список), якщо раптом сюди прийде список
            if isinstance(preselected_str, list):
                initial_items = preselected_str
            else:
                initial_items = [x.strip() for x in preselected_str.split(',')]
            
            for item in initial_items:
                if item: self.add_fabric(item, skip_callback=True)
        
        self._update_dropdown_values()

    def _on_combo_select(self, event):
        val = self.combo_var.get()
        if val and val != "Select Fabric to Add..." and val != "No more fabrics available":
            self.add_fabric(val)
            self.combo_add.set("") 
            try: self.winfo_toplevel().focus()
            except: pass

    def add_fabric(self, fabric_name, skip_callback=False):
        if fabric_name in self.selected_fabrics:
            return

        self.selected_fabrics.append(fabric_name)
        
        row_frame = tk.Frame(self.selected_container, bg="#eef", pady=2, padx=5, bd=1, relief="solid")
        row_frame.pack(fill=tk.X, pady=2, anchor="w")

        lbl = tk.Label(row_frame, text=fabric_name, bg="#eef", font=("Arial", 10))
        lbl.pack(side=tk.LEFT)

        btn_del = tk.Button(row_frame, text="✖", font=("Arial", 8, "bold"), fg="red", bg="#eef",
                            borderwidth=0, cursor="hand2",
                            command=lambda f=row_frame, n=fabric_name: self.remove_fabric(f, n))
        btn_del.pack(side=tk.RIGHT)

        self._update_dropdown_values()
        
        if self.on_change_callback and not skip_callback:
            self.on_change_callback()

    def remove_fabric(self, frame_widget, fabric_name):
        if fabric_name in self.selected_fabrics:
            self.selected_fabrics.remove(fabric_name)
        frame_widget.destroy()
        self._update_dropdown_values()
        
        if self.on_change_callback:
            self.on_change_callback()

    def _update_dropdown_values(self):
        available = [f for f in self.all_fabrics_source if f not in self.selected_fabrics]
        if not available:
            self.combo_add['values'] = ["No more fabrics available"]
        else:
            self.combo_add['values'] = available

    # [ВАЖЛИВО] Цей метод повертає список (масив), а не рядок
    def get_selected_list(self):
        return self.selected_fabrics