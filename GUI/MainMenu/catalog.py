import sys
import os
import tkinter as tk
from tkinter import ttk
import io
from PIL import Image, ImageTk
import threading

from Utils import tkinter_general
from Utils import mongodb_functions

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)



class CatalogView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")

        self.is_loading = False  # Щоб не запускати завантаження двічі одночасно
        self.all_loaded = False # Чи завантажені всі товари
        self.state = "model"  # Поточний стан: "models" або "fabric"
        self.current_product_index = 0 # Лічильник товарів (для бази даних)
        self.grid_row = 0        # Поточний рядок сітки
        self.grid_col = 0        # Поточна колонка сітки

        self.image_refs = []

        self.create_widgets()
        self.create_filter_widgets()
        self.load_more_products()
    
    def create_widgets(self):
        #Category Buttons Frame
        category_Frame = tk.Frame(self, bg="lightgray")
        category_Frame.pack(side=tk.TOP, fill=tk.X)

        self.models_button = tk.Button(category_Frame, text="Models", font=("Arial", 18, "bold"), command=lambda: self.switch_category("model"))
        self.models_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fabrics_button = tk.Button(category_Frame, text="Fabrics", font=("Arial", 18, "bold"), command=lambda: self.switch_category("fabric"))
        self.fabrics_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Body Frame
        body_frame = tk.Frame(self, bg="white")
        body_frame.pack(fill=tk.BOTH, expand=True)

        #Search Frame
        self.search_Frame = tk.Frame(body_frame, bg="pink", width=250)
        self.search_Frame.pack(side=tk.LEFT, fill=tk.Y)
        self.search_Frame.pack_propagate(False)

        self.search_Label = tk.Label(self.search_Frame, text="Search", font=("Arial", 14), bg="pink")
        self.search_Label.pack(pady=(10, 0), anchor="w")
        self.search_Entry = tk.Entry(self.search_Frame, font=("Arial", 14))
        self.search_Entry.pack(pady=0, padx=10, fill=tk.X)
        self.search_Entry.bind("<Return>", lambda event: self.apply_filters())

        self.sort_by_Label = tk.Label(self.search_Frame, text="Sort by", font=("Arial", 14), bg="pink")
        self.sort_by_Label.pack(pady=(20, 0), anchor="w")
        self.sort_by_Combobox = ttk.Combobox(self.search_Frame, values=["Name A-Z", "Name Z-A", "Price Low-High", "Price High-Low"], font=("Artaial", 14))
        self.sort_by_Combobox.config(state="readonly")
        self.sort_by_Combobox.pack(pady=0, padx=10, fill=tk.X)
        self.sort_by_Combobox.current(0)
        self.sort_by_Combobox.bind("<<ComboboxSelected>>", lambda event: self.apply_filters())

        self.filter_Frame = tk.Frame(self.search_Frame, bg="pink")
        self.filter_Frame.pack(side=tk.LEFT, fill=tk.Y)
        self.create_filter_widgets()


        #Content Frame
        scroll_container = tk.Frame(body_frame, bg="white")
        scroll_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(scroll_container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=self.canvas.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.configure(yscrollcommand=self.on_scroll)

        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.canvas_frame_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
    
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.canvas.bind('<Leave>', self._unbind_mouse_wheel)

        def on_canvas_resize(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_frame_window, width=canvas_width)
        
        self.canvas.bind("<Configure>", on_canvas_resize)

    def create_filter_widgets(self):
        if hasattr(self, 'search_Frame'):
            for widget in self.filter_Frame.winfo_children():
                widget.destroy()
        filter_Label = tk.Label(self.filter_Frame, text="Filter", font=("Arial", 12), bg="pink")
        filter_Label.pack(pady=(20, 0))

        if self.state == "model":
            self.filter_recomended_fabric_Label = tk.Label(self.filter_Frame, text="Recommended Fabric", font=("Arial", 14), bg="pink")
            self.filter_recomended_fabric_Label.pack(pady=(10, 0), anchor="w")
            self.filter_recomended_fabric_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_recomended_fabric_Entry.pack(pady=0, padx=10, fill=tk.X) 
            self.filter_recomended_fabric_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_recomended_accessories_Label = tk.Label(self.filter_Frame, text="Recommended Accessories", font=("Arial", 14), bg="pink")
            self.filter_recomended_accessories_Label.pack(pady=(10, 0), anchor="w")
            self.filter_recomended_accessories_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_recomended_accessories_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_recomended_accessories_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_model_price_Label = tk.Label(self.filter_Frame, text="Price Range", font=("Arial", 14), bg="pink")
            self.filter_model_price_Label.pack(pady=(10, 0), anchor="w")

            self.filter_model_price_from_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_model_price_from_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_model_price_from_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_model_price_to_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_model_price_to_Entry.pack(pady=2, padx=10, fill=tk.X)
            self.filter_model_price_to_Entry.bind("<Return>", lambda event: self.apply_filters()) 

        else:
            self.filter_fabric_manufacturer_id_Label = tk.Label(self.filter_Frame, text="Fabric Manufacturer ID", font=("Arial", 14), bg="pink")
            self.filter_fabric_manufacturer_id_Label.pack(pady=(10, 0), anchor="w")
            self.filter_fabric_manufacturer_id_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_fabric_manufacturer_id_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_fabric_manufacturer_id_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_fabric_color_Label = tk.Label(self.filter_Frame, text="Fabric Color", font=("Arial", 14), bg="pink")
            self.filter_fabric_color_Label.pack(pady=(10, 0), anchor="w")
            self.filter_fabric_color_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_fabric_color_Entry.pack(pady=0, padx=10, fill=tk.X) 
            self.filter_fabric_color_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_fabric_texture_Label = tk.Label(self.filter_Frame, text="Fabric Texture", font=("Arial", 14), bg="pink")
            self.filter_fabric_texture_Label.pack(pady=(10, 0), anchor="w")
            self.filter_fabric_texture_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_fabric_texture_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_fabric_texture_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_fabric_price_per_meter_Label = tk.Label(self.filter_Frame, text="Price per Meter Range", font=("Arial", 14), bg="pink")
            self.filter_fabric_price_per_meter_Label.pack(pady=(10, 0), anchor="w")

            self.filter_fabric_price_per_meter_from_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_fabric_price_per_meter_from_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_fabric_price_per_meter_from_Entry.bind("<Return>", lambda event: self.apply_filters())

            self.filter_fabric_price_per_meter_to_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_fabric_price_per_meter_to_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_fabric_price_per_meter_to_Entry.bind("<Return>", lambda event: self.apply_filters())



        self.filter_in_stock_var = tk.IntVar()
        self.filter_in_stock_Checkbutton = tk.Checkbutton(self.filter_Frame, text="In Stock", variable=self.filter_in_stock_var, 
                                                        font=("Arial", 12), bg="pink",
                                                        command=self.apply_filters)
        self.filter_in_stock_Checkbutton.pack(pady=10, padx=10, anchor="w")

        self.apply_btn = tk.Button(self.filter_Frame, text="Apply Filters", command=self.apply_filters, bg="white")
        self.apply_btn.pack(pady=20, padx=10, fill=tk.X)

    def _bind_mouse_wheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse_wheel(self, event):
        self.canvas.bind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        # Linux: Button-4 = Вгору, Button-5 = Вниз
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        # Windows/MacOS: Використовує delta
        elif event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.check_scroll_position()

    def on_scroll(self, *args):
        # Цей метод викликається самим канвасом при будь-якому русі
        self.scrollbar.set(*args) # Оновлюємо візуально повзунок
        self.check_scroll_position()

    def check_scroll_position(self):
        if self.is_loading:
            return
        
        if self.current_product_index == 0:
            return

        # Ми ставимо поріг 0.9 (90%), щоб почати вантажити трохи заздалегідь
        current_position = self.canvas.yview()[1]

        top, bottom = self.canvas.yview()
        
        if top == 0.0 and bottom == 1.0:
            return

        if current_position > 0.9:
            self.load_more_products()  

    def set_buttons_state(self, state):
        """
        state: "normal" (активні) або "disabled" (заблоковані)
        """
        # 1. Блокуємо кнопки категорій
        if hasattr(self, 'models_button') and hasattr(self, 'fabrics_button'):
            self.models_button.config(state=state)
            self.fabrics_button.config(state=state)
            
            if state == "normal":
                default_bg = "#f0f0f0"
                if self.state == "model":
                    self.models_button.config(bg="#ebdff7", activebackground="#ebdff7") 
                    self.fabrics_button.config(bg="#c8b8d8", activebackground="#ebdff7")
                else:
                    self.fabrics_button.config(bg="#ebdff7", activebackground="#ebdff7")
                    self.models_button.config(bg="#c8b8d8", activebackground="#ebdff7")

        if hasattr(self, 'apply_btn'):
            self.apply_btn.config(state=state)

        
    def switch_category(self, category):
        if self.state == category:
            return
        self.state = category
        self.create_filter_widgets()
        self.clear_catalog()
        self.load_more_products()

    def clear_catalog(self):
        # 1. Видаляємо всі віджети з scrollable_frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 2. Скидаємо лічильники сітки та індексів
        self.current_product_index = 0
        self.grid_row = 0
        self.grid_col = 0
        
        # 3. Очищаємо список зображень (щоб звільнити пам'ять)
        self.image_refs.clear() 
        
        # 4. Скидаємо прапорці
        self.all_loaded = False
        self.is_loading = False
        
        # 5. Скидаємо прокрутку на самий верх
        self.canvas.yview_moveto(0)

    def load_more_products(self):
        """Запускає процес завантаження у фоновому режимі"""
        if self.is_loading or self.all_loaded: # Якщо вже вантажимось - виходимо
            return

        self.is_loading = True

        self.set_buttons_state("disabled")
        
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)

        # --- ДОДАНО: Створюємо Label "Завантаження..." ---
        # Ми ставимо його в наступний рядок (grid_row + 1) і розтягуємо на 3 колонки (columnspan=3)
        self.loading_label = tk.Label(self.scrollable_frame, text="⏳ Завантажуються дані...", 
                                      font=("Arial", 12, "italic"), fg="gray", bg="white")
        self.loading_label.grid(row=self.grid_row + 1, column=0, columnspan=3, pady=20, sticky="ew")
        
        current_query = self.build_filter_query()
        current_sort = self.get_sort_order()


        # Оновлюємо інтерфейс примусово, щоб напис з'явився миттєво до запуску потоку
        self.scrollable_frame.update_idletasks() 

        # Запускаємо потік
        threading.Thread(target=self._background_loader, args=(current_query, current_sort), daemon=True).start()

    def _background_loader(self, query_filter, sort_order):
        """Цей код виконується паралельно і не блокує вікно"""
        processed_items = []
        try:
            batch_size = 12
            
            # 1. Запит до бази даних
            if self.state == "model":
                collection = "models"
                field_name = "model_name"
                field_price = "price"
            else: # "fabric"
                collection = "fabrics"
                field_name = "fabric_name"
                field_price = "price_per_meter" # Перевірте, чи точно так названо в БД

            projection = None

            raw_data = mongodb_functions.get_documents_paginated(
                collection_name=collection,
                query=query_filter,      
                sort=sort_order,
                skip=self.current_product_index,
                limit=batch_size,
                projection=projection
            )

            # 2. Підготовка картинок
            for item in raw_data:
                pil_image = None
                image_binary = item.get("image")
                in_stock = item.get("in_stock", True)

                if image_binary:
                    try:
                        img_data = io.BytesIO(image_binary)
                        pil_img_raw = Image.open(img_data)
                        pil_img_raw.thumbnail((200, 200))
                        if not in_stock:
                            pil_img_raw = pil_img_raw.convert("L")
                        pil_image = pil_img_raw
                    except Exception as e:
                        print(f"Помилка обробки фото для {item.get('model_name')}: {e}")
                        # Не перериваємо цикл, просто цей товар буде без фото

                price = ""
                if self.state == "model":
                    price = "price"
                    processed_items.append({
                    "_id": str(item.get("_id", "Unknown")),
                    "name": item.get(f"{self.state}_name", "Unknown"),
                    "price": item.get(price, 0),
                    "pil_image": pil_image,
                    "in_stock": item.get("in_stock", False),
                    "description": item.get("description", ""),
                    "recommended_fabric": item.get("recommended_fabric", ""),
                    "recommended_accessories": item.get("recommended_accessories", ""),
                    "original_image_binary": image_binary
                })
                else:
                    price = "price_per_meter"
                    processed_items.append({
                    "_id": str(item.get("_id", "Unknown")),
                    "name": item.get(f"{self.state}_name", "Unknown"),
                    "price": item.get(price, 0),
                    "pil_image": pil_image,
                    "in_stock": item.get("in_stock", False),
                    "description": item.get("description", ""),
                    "fabric_color": item.get("fabric_color", ""),
                    "fabric_texture": item.get("fabric_texture", ""),
                    "fabric_manufacturer_id": item.get("fabric_manufacturer_id", ""),
                    "width_in_meters": item.get("width_in_meters", ""),
                    "width": f"{item.get('width_in_meters', '-')} m",
                    "original_image_binary": image_binary
                })
                

        except Exception as e:
            print(f"Критична помилка у потоці: {e}")
            # processed_items залишиться порожнім або частково заповненим
        
        finally:
            # 3. Цей блок виконається ЗАВЖДИ, навіть якщо була помилка.
            # Ми обов'язково повідомляємо головний потік, що роботу завершено.
            self.after(0, self._update_ui_on_main_thread, processed_items)

    def _update_ui_on_main_thread(self, new_items):
        """Цей метод виконується в головному потоці і малює віджети"""
        
        # Перевірка: якщо користувач вже закрив вкладку каталогу, поки вантажились дані
        if not self.winfo_exists():
            return
        
        if hasattr(self, 'loading_label') and self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None

        self.set_buttons_state("normal")

        if not new_items:
            self.show_end_of_list_message() # Ваша функція "На даний момент все"
            self.all_loaded = True
            self.is_loading = False
            return

        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)

        # Створення карток
        for item in new_items:
            self.create_product_card(item)

        # Оновлюємо лічильник
        self.current_product_index += len(new_items)

        batch_size = 12
        if len(new_items) < batch_size:
            self.all_loaded = True
            self.show_end_of_list_message()
        
        # Знімаємо прапорець завантаження
        self.is_loading = False

    def create_product_card(self, item_data):
        name = item_data["name"]
        price = item_data["price"]
        pil_image = item_data["pil_image"] # Це вже готовий PIL Image, підготовлений у потоці
        in_stock = item_data["in_stock"]

        card = tk.Frame(self.scrollable_frame, bg="#ffffff", bd=1, relief="ridge")
        card.grid(row=self.grid_row, column=self.grid_col, padx=10, pady=10, sticky="nsew")
        
        # Створення ImageTk (тільки в головному потоці!)
        if pil_image:
            photo = ImageTk.PhotoImage(pil_image)
            self.image_refs.append(photo) # Зберігаємо посилання
            tk.Label(card, image=photo, bg="#ffffff").pack(pady=(10, 5))
        else:
            tk.Label(card, text="No Image", bg="#eee", width=20, height=10).pack(pady=(10, 5))

        tk.Label(card, text=name, font=("Arial", 12, "bold"), bg="#ffffff").pack()
        
        price_color = "green" if in_stock else "gray"
        if self.state == "model":
            tk.Label(card, text=f"{price} грн", font=("Arial", 11), fg=price_color, bg="#ffffff").pack(pady=(0, 10))
        else:
            tk.Label(card, text=f"{price} грн/м", font=("Arial", 11), fg=price_color, bg="#ffffff").pack(pady=(0, 10))
        
        if not in_stock:
            tk.Label(card, text="Не в наявності", font=("Arial", 10, "bold"), fg="red", bg="#ffffff").pack(pady=(0, 10))
        else:
            # Можна додати порожній відступ, щоб картки були однієї висоти
            tk.Label(card, text="", font=("Arial", 10), bg="#ffffff").pack(pady=(0, 10))
        
        def on_card_click(event):
            from GUI.MainMenu.details_view_frame import DetailsView # Лінивий імпорт, щоб уникнути циклічності
            DetailsView(self, item_data, self.state)
        
        card.bind("<Button-1>", on_card_click)

        for child in card.winfo_children():
            child.bind("<Button-1>", on_card_click)
        # ---------------------------

        # Логіка сітки
        self.grid_col += 1
        if self.grid_col > 2:
            self.grid_col = 0
            self.grid_row += 1

    def show_end_of_list_message(self):
        """Показує повідомлення внизу, що товарів більше немає"""
        # Створюємо лейбл на всю ширину в наступному рядку
        lbl_end = tk.Label(self.scrollable_frame, text="На даний момент все", 
                           font=("Arial", 10, "italic"), fg="gray", bg="white")
        lbl_end.grid(row=self.grid_row + 1, column=0, columnspan=3, pady=20)

    def build_filter_query(self):
        """Зчитує всі поля вводу і формує словник query для MongoDB"""
        query = {}

        search_text = ""
        if hasattr(self, 'search_Entry') and self.search_Entry.get():
            search_text = self.search_Entry.get().strip()
        
        field_name = "model_name" if self.state == "model" else "fabric_name"
        
        if search_text:
            # $regex з опцією 'i' робить пошук нечутливим до регістру
            query[field_name] = {"$regex": search_text, "$options": "i"}

        # 2. Фільтр "В наявності" (In Stock)
        # Те саме, треба мати self.filter_in_stock_var
        if hasattr(self, 'filter_in_stock_var') and self.filter_in_stock_var.get() == 1:
            query["in_stock"] = True

        # 3. Специфічні фільтри (залежно від вкладки)
        if self.state == "model":
            if hasattr(self, 'filter_recomended_fabric_Entry') and self.filter_recomended_fabric_Entry.get():
                text = self.filter_recomended_fabric_Entry.get().strip()
                query["recommended_fabric"] = {"$regex": text, "$options": "i"}
            
            if hasattr(self, 'filter_recomended_accessories_Entry') and self.filter_recomended_accessories_Entry.get():
                text = self.filter_recomended_accessories_Entry.get().strip()
                query["recommended_accessories"] = {"$regex": text, "$options": "i"}
            
            price_query = {}
            if hasattr(self, 'filter_model_price_from_Entry') and self.filter_model_price_from_Entry.get():
                try:
                    val = float(self.filter_model_price_from_Entry.get())
                    price_query["$gte"] = val
                except ValueError: 
                    pass # Ігноруємо, якщо ввели букви
            
            # Обробка "До" (Less than or equal - $lte)
            if hasattr(self, 'filter_model_price_to_Entry') and self.filter_model_price_to_Entry.get():
                try:
                    val = float(self.filter_model_price_to_Entry.get())
                    price_query["$lte"] = val
                except ValueError: 
                    pass

            # Якщо хоч одне поле заповнене, додаємо в запит
            if price_query:
                query["price"] = price_query 
            # ---------------------------------------

        else: # Fabrics
            # Приклад: Manufacturer ID
            if hasattr(self, 'filter_fabric_manufacturer_id_Entry') and self.filter_fabric_manufacturer_id_Entry.get():
                query["manufacturer_id"] = self.filter_fabric_manufacturer_id_Entry.get().strip()
            
            if hasattr(self, 'filter_fabric_texture_Entry') and self.filter_fabric_texture_Entry.get():
                text = self.filter_fabric_texture_Entry.get().strip()
                query["fabric_texture"] = {"$regex": text, "$options": "i"} # Перевірте назву поля в БД!

            # Приклад: Color
            if hasattr(self, 'filter_fabric_color_Entry') and self.filter_fabric_color_Entry.get():
                text = self.filter_fabric_color_Entry.get().strip()
                query["color"] = {"$regex": text, "$options": "i"}

            # Приклад: Price Range (Ціна від і до)
            price_query = {}
            if hasattr(self, 'filter_fabric_price_per_meter_from_Entry'):
                try:
                    val = float(self.filter_fabric_price_per_meter_from_Entry.get())
                    price_query["$gte"] = val # Greater than or equal
                except ValueError: pass
            
            if hasattr(self, 'filter_fabric_price_per_meter_to_Entry'):
                try:
                    val = float(self.filter_fabric_price_per_meter_to_Entry.get())
                    price_query["$lte"] = val # Less than or equal
                except ValueError: pass
            
            if price_query:
                query["price_per_meter"] = price_query

        return query

    def get_sort_order(self):
        """Зчитує Combobox і повертає список сортування"""
        if not hasattr(self, 'sort_by_Combobox'):
            return None
            
        selection = self.sort_by_Combobox.get()
        field_price = "price" if self.state == "model" else "price_per_meter"
        field_name = "model_name" if self.state == "model" else "fabric_name"

        # 1 = Ascending (А-Я, 0-9), -1 = Descending (Я-А, 9-0)
        if selection == "Name A-Z":
            return [(field_name, 1)]
        elif selection == "Name Z-A":
            return [(field_name, -1)]
        elif selection == "Price Low-High":
            return [(field_price, 1)]
        elif selection == "Price High-Low":
            return [(field_price, -1)]
        
        return None # Сортування за замовчуванням (як у БД)
    
    def apply_filters(self, event=None):
        """Скидає каталог і завантажує заново з урахуванням фільтрів"""
        self.clear_catalog()
        self.load_more_products()

    





