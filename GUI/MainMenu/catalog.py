import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
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
        filter_Label.pack(pady=(20, 0), padx=100)

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
            self.filter_fabric_supplier_id_Label = tk.Label(self.filter_Frame, text="Fabric Supplier ID", font=("Arial", 14), bg="pink")
            self.filter_fabric_supplier_id_Label.pack(pady=(10, 0), anchor="w")
            self.filter_fabric_supplier_id_Entry = tk.Entry(self.filter_Frame, font=("Arial", 12))
            self.filter_fabric_supplier_id_Entry.pack(pady=0, padx=10, fill=tk.X)
            self.filter_fabric_supplier_id_Entry.bind("<Return>", lambda event: self.apply_filters())

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
            self.filter_fabric_price_per_meter_to_Entry.pack(pady=2, padx=10, fill=tk.X) 
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
        # Start loading process in background
        if self.is_loading or self.all_loaded: # If already loaded - return
            return

        self.is_loading = True

        self.set_buttons_state("disabled")
        
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)

        # Create label "Loading data..."
        self.loading_label = tk.Label(self.scrollable_frame, text="⏳ Loading data...", 
                                      font=("Arial", 12, "italic"), fg="gray", bg="white")
        self.loading_label.grid(row=self.grid_row + 1, column=0, columnspan=3, pady=20, sticky="ew")
        
        current_query = self.build_filter_query()
        current_sort = self.get_sort_order()


        # Forcefuly update interface so Loading label appeared first
        self.scrollable_frame.update_idletasks() 

        # Start thread
        threading.Thread(target=self._background_loader, args=(current_query, current_sort), daemon=True).start()

    def _background_loader(self, query_filter, sort_order):
        processed_items = []
        try:
            batch_size = 12
            
            # 1. Request to the DB
            if self.state == "model":
                collection = "models"
                field_name = "model_name"
                field_price = "price"
            else: # "fabric"
                collection = "fabrics"
                field_name = "fabric_name"
                field_price = "price_per_meter"

            projection = None

            raw_data = mongodb_functions.get_documents_paginated(
                collection_name=collection,
                query=query_filter,      
                sort=sort_order,
                skip=self.current_product_index,
                limit=batch_size,
                projection=projection
            )

            # 2. Processing images
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

                            if pil_img_raw.mode in ('RGBA', 'LA') or (pil_img_raw.mode == 'P' and 'transparency' in pil_img_raw.info):
                                
                                white_bg = Image.new("RGB", pil_img_raw.size, (255, 255, 255))
                                
                                pil_img_raw = pil_img_raw.convert("RGBA")
                                
                                white_bg.paste(pil_img_raw, mask=pil_img_raw.split()[3])
                                
                                pil_img_raw = white_bg
                            pil_img_raw = pil_img_raw.convert("L")
                        pil_image = pil_img_raw
                    except Exception as e:
                        print(f"Error occured while processing image for {item.get('model_name')}: {e}")

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
                    "fabric_supplier_id": item.get("fabric_supplier_id", ""),
                    "width_in_meters": item.get("width_in_meters", ""),
                    "width": f"{item.get('width_in_meters', '-')} m",
                    "original_image_binary": image_binary
                })
                

        except Exception as e:
            print(f"Critical error in thread: {e}")
        
        finally:
            # 3. Inform the Main thread that the work is done
            self.after(0, self._update_ui_on_main_thread, processed_items)

    def _update_ui_on_main_thread(self, new_items):
        # This method executes in the Main thread, draws widgets
        
        # Checks if user already closed Catalog tab during data loading
        if not self.winfo_exists():
            return
        
        if hasattr(self, 'loading_label') and self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None

        self.set_buttons_state("normal")

        if not new_items:
            self.show_end_of_list_message()
            self.all_loaded = True
            self.is_loading = False
            return

        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)

        # Create images
        for item in new_items:
            self.create_product_card(item)

        # Update index
        self.current_product_index += len(new_items)

        batch_size = 12
        if len(new_items) < batch_size:
            self.all_loaded = True
            self.show_end_of_list_message()
        
        self.is_loading = False

    def create_product_card(self, item_data):
        """Створення картки товару з урахуванням категорії"""
        card = tk.Frame(self.scrollable_frame, bg="#ffffff", bd=1, relief="ridge")
        card.grid(row=self.grid_row, column=self.grid_col, padx=10, pady=10, sticky="nsew")
        
        # --- Image ---
        if item_data["pil_image"]:
            photo = ImageTk.PhotoImage(item_data["pil_image"])
            self.image_refs.append(photo) 
            lbl_img = tk.Label(card, image=photo, bg="#ffffff")
            lbl_img.pack(pady=(10, 5))
        else:
            lbl_img = tk.Label(card, text="No Image", bg="#eee", width=20, height=10)
            lbl_img.pack(pady=(10, 5))

        # --- Title ---
        tk.Label(card, text=item_data["name"], font=("Arial", 12, "bold"), bg="#ffffff", wraplength=180).pack(padx=5)
        
        # --- Price ---
        price_color = "#ba86ba" if item_data["in_stock"] else "gray"
        price_suffix = "UAH" if self.state == "model" else "UAH/m"
        tk.Label(card, text=f"{item_data['price']} {price_suffix}", font=("Arial", 11), fg=price_color, bg="#ffffff").pack(pady=(0, 5))
        
        if not item_data["in_stock"]:
            tk.Label(card, text="Out of stock", font=("Arial", 10, "bold"), fg="#5e4152", bg="#ffffff").pack(pady=(0, 5))

        # --- Buttons Area (ОНОВЛЕНО) ---
        # Використовуємо фрейм для кнопки внизу, щоб вона прилипала до низу картки
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Логіка відображення кнопки Order
        if self.state == "model":
            # Якщо це модель, показуємо кнопку замовлення
            if item_data["in_stock"]:
                order_btn = tk.Button(btn_frame, text="Order Model", bg="#815d88", fg="white", font=("Arial", 10, "bold"),
                                      cursor="hand2", command=lambda: self.open_order_window(item_data))
                order_btn.pack(fill=tk.X)
            else:
                 tk.Label(btn_frame, text="Unavailable", fg="gray", bg="white").pack()
        else:
            # Якщо це тканина, просто інформаційний напис
            tk.Label(btn_frame, text="Material Only", fg="gray", font=("Arial", 9, "italic"), bg="white").pack()
            
        def on_card_click(event):
            from GUI.MainMenu.details_view_frame import DetailsView 
            DetailsView(self, item_data, self.state)
        
        card.bind("<Button-1>", on_card_click)

        for child in card.winfo_children():
            child.bind("<Button-1>", on_card_click)
        # ---------------------------

        # Grid logix
        self.grid_col += 1
        if self.grid_col > 2:
            self.grid_col = 0
            self.grid_row += 1

    def open_order_window(self, item_data):
        # Тут можна відкрити DetailsView або одразу створити замовлення
        from GUI.MainMenu.details_view_frame import DetailsView
        DetailsView(self, item_data, self.state)

    def show_end_of_list_message(self):
        # Shows that there's no more products to be loaded
        lbl_end = tk.Label(self.scrollable_frame, text="That's all at the moment", 
                           font=("Arial", 10, "italic"), fg="gray", bg="white")
        lbl_end.grid(row=self.grid_row + 1, column=0, columnspan=3, pady=20)

    def build_filter_query(self):
        # Reads all filter fields and creates query dictionary for MongoDB
        query = {}

        search_text = ""
        if hasattr(self, 'search_Entry') and self.search_Entry.get():
            search_text = self.search_Entry.get().strip()
        
        field_name = "model_name" if self.state == "model" else "fabric_name"
        
        if search_text:
            query[field_name] = {"$regex": search_text, "$options": "i"}

        if hasattr(self, 'filter_in_stock_var') and self.filter_in_stock_var.get() == 1:
            query["in_stock"] = True

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
                    pass 
            
            if hasattr(self, 'filter_model_price_to_Entry') and self.filter_model_price_to_Entry.get():
                try:
                    val = float(self.filter_model_price_to_Entry.get())
                    price_query["$lte"] = val
                except ValueError: 
                    pass

            if price_query:
                query["price"] = price_query 

        else: # Fabrics
            # Supplier ID
            if hasattr(self, 'filter_fabric_supplier_id_Entry') and self.filter_fabric_supplier_id_Entry.get():
                query["supplier_id"] = self.filter_fabric_supplier_id_Entry.get().strip()
            
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
        if not hasattr(self, 'sort_by_Combobox'):
            return None
            
        selection = self.sort_by_Combobox.get()
        field_price = "price" if self.state == "model" else "price_per_meter"
        field_name = "model_name" if self.state == "model" else "fabric_name"


        if selection == "Name A-Z":
            return [(field_name, 1)]
        elif selection == "Name Z-A":
            return [(field_name, -1)]
        elif selection == "Price Low-High":
            return [(field_price, 1)]
        elif selection == "Price High-Low":
            return [(field_price, -1)]
        
        return None
    
    def apply_filters(self, event=None):
        if (not self.price_range_validation()):
            return
        self.clear_catalog()
        self.load_more_products()
    
    def price_range_validation(self):
        """
        Перевіряє коректність вводу цін залежно від активної вкладки.
        """
        try:
            val_from = ""
            val_to = ""

            # [FIX] Перевіряємо стан перед тим, як чіпати віджети
            if self.state == "model":
                # Перевірка на існування віджета (додатковий захист)
                if hasattr(self, 'filter_model_price_from_Entry') and self.filter_model_price_from_Entry.winfo_exists():
                    val_from = self.filter_model_price_from_Entry.get()
                    val_to = self.filter_model_price_to_Entry.get()
            
            elif self.state == "fabric": # Або "fabrics", як у вас названо
                if hasattr(self, 'filter_fabric_price_from_Entry') and self.filter_fabric_price_from_Entry.winfo_exists():
                    val_from = self.filter_fabric_price_from_Entry.get()
                    val_to = self.filter_fabric_price_to_Entry.get()

            # Сама валідація (чи це числа)
            if val_from: 
                float(val_from)
            if val_to:  
                float(val_to)

            return True
            
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return False
        except Exception as e:
            print(f"Validation Error: {e}")
            return False

    def get_filter_query(self):
        """
        Збирає фільтри для запиту в БД.
        """
        query = {}
        
        # 1. Пошук за назвою
        search_text = ""
        if hasattr(self, 'search_Entry') and self.search_Entry.winfo_exists():
            search_text = self.search_Entry.get().strip()
        
        if search_text:
            field_name = "product_name" if self.state == "model" else "fabric_name" 
            # Для тканин може бути "name" або "fabric_name", перевірте вашу БД
            # У попередніх файлах ми бачили, що для тканин ви шукаєте по багатьох полях, 
            # але тут спростимо до основного.
            query[field_name] = {"$regex": search_text, "$options": "i"}

        # 2. Фільтр ціни
        price_query = {}
        val_from = ""
        val_to = ""

        # [FIX] Знову перевіряємо стан
        if self.state == "model":
            if hasattr(self, 'filter_model_price_from_Entry') and self.filter_model_price_from_Entry.winfo_exists():
                val_from = self.filter_model_price_from_Entry.get()
                val_to = self.filter_model_price_to_Entry.get()
            price_field = "base_price" # Або "price"
            
        else: # fabric
            if hasattr(self, 'filter_fabric_price_from_Entry') and self.filter_fabric_price_from_Entry.winfo_exists():
                val_from = self.filter_fabric_price_from_Entry.get()
                val_to = self.filter_fabric_price_to_Entry.get()
            price_field = "price_per_meter" # Або "price"

        # Формуємо запит ціни
        if val_from:
            price_query["$gte"] = float(val_from)
        if val_to:
            price_query["$lte"] = float(val_to)
        
        if price_query:
            query[price_field] = price_query

        return query






