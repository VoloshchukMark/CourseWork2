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
        self.current_product_index = 0 # Лічильник товарів (для бази даних)
        self.grid_row = 0        # Поточний рядок сітки
        self.grid_col = 0        # Поточна колонка сітки

        self.image_refs = []

        self.create_widgets()
        self.load_more_products()
    
    def create_widgets(self):
        #Category Buttons Frame
        category_Frame = tk.Frame(self, bg="lightgray")
        category_Frame.pack(side=tk.TOP, fill=tk.X)

        models_button = tk.Button(category_Frame, text="Models", font=("Arial", 18, "bold"))
        models_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fabrics_button = tk.Button(category_Frame, text="Fabrics", font=("Arial", 18, "bold"))
        fabrics_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Body Frame
        body_frame = tk.Frame(self, bg="white")
        body_frame.pack(fill=tk.BOTH, expand=True)

        #Search Frame
        search_Frame = tk.Frame(body_frame, bg="pink", width=250)
        search_Frame.pack(side=tk.LEFT, fill=tk.Y)
        search_Frame.pack_propagate(False)


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

        # yview() повертає (top, bottom). bottom — це число від 0.0 до 1.0
        # 1.0 означає самий низ. 
        # Ми ставимо поріг 0.9 (90%), щоб почати вантажити трохи заздалегідь
        current_position = self.canvas.yview()[1]
        
        if current_position > 0.9:
            self.load_more_products()

    def load_more_products(self):
        """Запускає процес завантаження у фоновому режимі"""
        if self.is_loading or self.all_loaded: # Якщо вже вантажимось - виходимо
            return

        self.is_loading = True
        
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)

        # --- ДОДАНО: Створюємо Label "Завантаження..." ---
        # Ми ставимо його в наступний рядок (grid_row + 1) і розтягуємо на 3 колонки (columnspan=3)
        self.loading_label = tk.Label(self.scrollable_frame, text="⏳ Завантажуються дані...", 
                                      font=("Arial", 12, "italic"), fg="gray", bg="white")
        self.loading_label.grid(row=self.grid_row + 1, column=0, columnspan=3, pady=20, sticky="ew")
        
        # Оновлюємо інтерфейс примусово, щоб напис з'явився миттєво до запуску потоку
        self.scrollable_frame.update_idletasks() 

        # Запускаємо потік
        threading.Thread(target=self._background_loader, daemon=True).start()

    def _background_loader(self):
        """Цей код виконується паралельно і не блокує вікно"""
        processed_items = []
        try:
            batch_size = 12
            
            # 1. Запит до бази даних
            raw_data = mongodb_functions.get_documents_paginated(
                collection_name="models",
                skip=self.current_product_index,
                limit=batch_size,
                projection={"model_name": 1, "price": 1, "image": 1}
            )

            # 2. Підготовка картинок
            for item in raw_data:
                pil_image = None
                image_binary = item.get("image")
                
                if image_binary:
                    try:
                        img_data = io.BytesIO(image_binary)
                        pil_img_raw = Image.open(img_data)
                        pil_img_raw.thumbnail((200, 200))
                        pil_image = pil_img_raw
                    except Exception as e:
                        print(f"Помилка обробки фото для {item.get('model_name')}: {e}")
                        # Не перериваємо цикл, просто цей товар буде без фото
                
                processed_items.append({
                    "name": item.get("model_name", "Unknown"),
                    "price": item.get("price", 0),
                    "pil_image": pil_image
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

        if not new_items:
            self.show_end_of_list_message() # Ваша функція "На даний момент все"
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
        tk.Label(card, text=f"{price} грн", font=("Arial", 11), fg="green", bg="#ffffff").pack(pady=(0, 10))

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