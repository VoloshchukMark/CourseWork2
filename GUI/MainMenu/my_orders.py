import sys
import os
import io
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import threading
from bson.objectid import ObjectId
from datetime import datetime

# --- Імпорти твоїх модулів ---
from Utils import tkinter_general
from Utils import mongodb_functions, session
from GUI.MainMenu.fabric_selector_widget import FabricSelectorWidget # Переконайся, що шлях правильний

class MyOrdersView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")

        self.controller = controller
        self.is_loading = False
        self.all_loaded = False
        self.current_skip = 0
        self.grid_row = 0
        self.image_refs = [] 

        self.fabric_data_map = {}
        self.are_fabrics_loaded = False

        self.create_widgets()
        self.load_fabrics_data()

    def create_widgets(self):
        body_frame = tk.Frame(self, bg="white")
        body_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(body_frame, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(body_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.configure(yscrollcommand=self.on_scroll)

        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_frame_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
    
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        self.canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.canvas.bind('<Leave>', self._unbind_mouse_wheel)

    def on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_frame_window, width=event.width)

    # --- Scroll Logic ---
    def _bind_mouse_wheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse_wheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4: self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: self.canvas.yview_scroll(1, "units")
        elif event.delta: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.check_scroll_position()

    def on_scroll(self, *args):
        self.scrollbar.set(*args)
        self.check_scroll_position()

    def check_scroll_position(self):
        if not self.are_fabrics_loaded: return
        if self.is_loading or self.all_loaded: return
        if self.canvas.yview()[1] > 0.9:
            self.load_orders()

    def refresh_list(self):
        self.current_skip = 0
        self.grid_row = 0
        self.all_loaded = False
        self.image_refs.clear()
        self.are_fabrics_loaded = False
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.canvas.yview_moveto(0)
        self.load_fabrics_data() 

    # --- Data Loading ---
    def load_fabrics_data(self):
        self.are_fabrics_loaded = False 
        
        def fetch():
            try:
                fabrics_docs = mongodb_functions.get_all_documents("fabrics")
                result_map = {}
                
                for doc in fabrics_docs:
                    # 1. Перевіряємо наявність
                    in_stock = doc.get("in_stock", True)
                    width = float(doc.get("width_in_meters", 0) or 0)
                    
                    # [NEW] Фільтр: Додаємо тільки якщо In Stock і є хоча б 1 метр
                    if in_stock and width >= 1:
                        name = doc.get("fabric_name") or doc.get("name") or doc.get("title") or doc.get("material")
                        price = doc.get("price_per_meter") or doc.get("price") or 0
                        if name:
                            result_map[str(name).strip()] = float(price)
                
                return result_map
            except Exception as e:
                print(f"Error fetching fabrics: {e}")
                return {}

        def on_fetched(data_map):
            self.fabric_data_map = data_map
            print(f"DEBUG: Loaded {len(data_map)} AVAILABLE fabrics.")
            self.are_fabrics_loaded = True
            self.load_orders()

        threading.Thread(target=lambda: self.after(0, on_fetched, fetch()), daemon=True).start()

    def load_orders(self):
        if not self.are_fabrics_loaded: return
        if self.is_loading or self.all_loaded: return
        self.is_loading = True

        self.loading_label = tk.Label(self.scrollable_frame, text="Loading...", font=("Arial", 10), fg="gray", bg="white")
        self.loading_label.grid(row=self.grid_row + 1, column=0, pady=10)
        self.scrollable_frame.update_idletasks()

        current_login = getattr(session.current_user, 'login', None)
        if not current_login:
            self.is_loading = False
            return

        query = {
            "customer_login": current_login,
            "status": {"$nin": ["Delivered", "New"]}
            }
        sort_order = [("status", 1), ("_id", -1)] 

        threading.Thread(target=self._background_loader, args=(query, sort_order), daemon=True).start()

    def _background_loader(self, query, sort_order):
        processed_items = []
        try:
            raw_data = mongodb_functions.get_documents_paginated(
                collection_name="orders", query=query, sort=sort_order,
                skip=self.current_skip, limit=10
            )

            for item in raw_data:
                pil_image = None
                image_binary = item.get("image")
                if image_binary:
                    try:
                        img_data = io.BytesIO(image_binary)
                        pil_img_raw = Image.open(img_data)
                        pil_img_raw.thumbnail((150, 150))
                        pil_image = pil_img_raw
                    except Exception: pass

                processed_items.append({
                    "_id": str(item.get("_id")),
                    "product_name": item.get("product_name", "Unknown"),
                    "status": item.get("status", "Draft"),
                    "base_price": item.get("base_price", 0),
                    "total_estimated_price": item.get("total_estimated_price", 0),
                    "fabric_used": item.get("fabric_used", []),
                    "accessories_used": item.get("accessories_used", ""),
                    "quantity": item.get("quantity", 1),
                    "pil_image": pil_image
                })
        except Exception as e:
            print(f"DB Error: {e}")
        finally:
            self.after(0, self._update_ui, processed_items)

    def _update_ui(self, new_items):
        if hasattr(self, 'loading_label') and self.loading_label:
            self.loading_label.destroy()

        if not new_items:
            self.all_loaded = True
            if self.current_skip == 0:
                tk.Label(self.scrollable_frame, text="You have no orders.", bg="white", font=("Arial", 12)).pack(pady=20)
            return

        for item in new_items:
            self.create_order_card(item)
            self.grid_row += 1

        self.current_skip += len(new_items)
        self.is_loading = False
        if len(new_items) < 10: self.all_loaded = True

    # --- UI: Order Card ---
    def create_order_card(self, data):
        if not self.scrollable_frame.winfo_exists(): return

        is_draft = (data["status"] == "Draft")
        
        border_col = "#ff9800" if is_draft else "#ccc"
        bg_col = "white" if is_draft else "#f9f9f9"
        
        card = tk.Frame(self.scrollable_frame, bg=bg_col, bd=1, relief="solid", highlightbackground=border_col, highlightthickness=1)
        card.grid(row=self.grid_row, column=0, sticky="ew", padx=20, pady=10)
        card.columnconfigure(1, weight=1) 
        
        # 1. Image
        if data["pil_image"]:
            photo = ImageTk.PhotoImage(data["pil_image"])
            self.image_refs.append(photo)
            tk.Label(card, image=photo, bg=bg_col).grid(row=0, column=0, padx=15, pady=15, sticky="n")
        else:
            tk.Label(card, text="No Image", bg="#eee", width=15, height=8).grid(row=0, column=0, padx=15, pady=15, sticky="n")

        # 2. Info
        mid_frame = tk.Frame(card, bg=bg_col)
        mid_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=15)

        tk.Label(mid_frame, text=data["product_name"], font=("Arial", 18, "bold"), bg=bg_col, anchor="w").pack(fill=tk.X)
        
        status_color = "#9e3d5a" if is_draft else "#ac76c2"
        tk.Label(mid_frame, text=f"Status: {data['status']}", font=("Arial", 11, "bold"), fg=status_color, bg=bg_col, anchor="w").pack(fill=tk.X, pady=(5, 10))
        
        self._create_info_row(mid_frame, "Model Price:", f"{data['base_price']} UAH", bg_col)
        
        if not is_draft:
             raw_fabrics = data.get("fabric_used", "-")
             if isinstance(raw_fabrics, list):
                 display_fabrics = ", ".join(raw_fabrics)
             else:
                 display_fabrics = str(raw_fabrics)

             self._create_info_row(mid_frame, "Fabrics:", display_fabrics, bg_col) 
             self._create_info_row(mid_frame, "Accessories:", data.get("accessories_used", ""), bg_col)
             
             tk.Frame(mid_frame, height=1, bg="#ddd").pack(fill=tk.X, pady=10)
             tk.Label(mid_frame, text=f"Total: {data.get('total_estimated_price')} UAH", font=("Arial", 14, "bold"), bg=bg_col, anchor="w").pack()
        else:
             tk.Label(mid_frame, text="Configure details to confirm order ➤", font=("Arial", 10, "italic"), fg="gray", bg=bg_col).pack(pady=20, anchor="w")

        # 3. Inputs (Draft Mode)
        right_frame = tk.Frame(card, bg=bg_col, width=320)
        right_frame.grid(row=0, column=2, sticky="ns", padx=20, pady=15)

        if is_draft:
            tk.Label(right_frame, text="Customize Order", font=("Arial", 12, "bold"), bg=bg_col, fg="#555").pack(anchor="w", pady=(0, 10))
            
            lbl_total_price = tk.Label(right_frame, text=f"Total: {data['base_price']} UAH", font=("Arial", 14, "bold"), fg="#4a148c", bg=bg_col)
            
            def recalculate_total(event=None):
                try:
                    model_price = float(data.get("base_price", 0))
                    selected_fabrics = fabric_selector.get_selected_list()
                    fabrics_cost = 0
                    for fab_name in selected_fabrics:
                        fabrics_cost += self.fabric_data_map.get(fab_name, 0)
                    
                    qty = int(spin_qty.get())
                    unit_price = model_price + fabrics_cost
                    final_total = unit_price * qty
                    
                    lbl_total_price.config(text=f"Total: {final_total:.2f} UAH")
                    return final_total
                except ValueError:
                    return 0

            tk.Label(right_frame, text="Select Fabrics:", bg=bg_col, font=("Arial", 9, "bold")).pack(anchor="w")
            
            fabric_selector = FabricSelectorWidget(
                right_frame, 
                self.fabric_data_map, 
                preselected_str="", 
                bg=bg_col,
                on_change_callback=recalculate_total
            )
            fabric_selector.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(right_frame, text="Accessories (optional):", bg=bg_col, font=("Arial", 9)).pack(anchor="w")
            entry_access = tk.Entry(right_frame, font=("Arial", 10))
            entry_access.insert(0, data.get("accessories_used", ""))
            entry_access.pack(fill=tk.X, pady=(0, 10))

            tk.Label(right_frame, text="Quantity:", bg=bg_col, font=("Arial", 9)).pack(anchor="w")
            
            spin_qty = tk.Spinbox(right_frame, from_=1, to=100, font=("Arial", 10), command=recalculate_total)
            spin_qty.delete(0, "end")
            spin_qty.insert(0, str(data.get("quantity", 1)))
            spin_qty.bind("<KeyRelease>", recalculate_total)
            spin_qty.pack(fill=tk.X, pady=(0, 20))

            lbl_total_price.pack(side=tk.TOP, pady=(0, 10))

            btn_confirm = tk.Button(right_frame, text="CONFIRM ORDER", bg="#4CAF50", fg="white", 
                                    font=("Arial", 11, "bold"), cursor="hand2", height=2,
                                    command=lambda: self.confirm_order(data, fabric_selector, entry_access.get(), spin_qty.get(), recalculate_total()))
            btn_confirm.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
            
            recalculate_total()

        else:
             tk.Label(right_frame, text="Quantity:", font=("Arial", 10, "bold"), bg=bg_col, fg="gray").pack(anchor="ne")
             tk.Label(right_frame, text=str(data.get("quantity", 1)), font=("Arial", 16), bg=bg_col).pack(anchor="ne")
             tk.Label(right_frame, text="✔ Order Placed", font=("Arial", 12, "italic"), fg="green", bg=bg_col).pack(side=tk.BOTTOM, pady=10)

    def _create_info_row(self, parent, label, value, bg):
        f = tk.Frame(parent, bg=bg)
        f.pack(fill=tk.X, pady=4) 
        
        tk.Label(f, text=label, font=("Arial", 10, "bold"), fg="gray", bg=bg, anchor="n").pack(side=tk.LEFT, anchor="n")
        
        val_str = str(value)
        tk.Label(f, text=val_str, font=("Arial", 10), fg="#333", bg=bg,
                 wraplength=220, justify="left", anchor="w").pack(side=tk.RIGHT, anchor="ne")

    def confirm_order(self, order_data, fabric_selector_widget, access_val, qty_val, calculated_total):
        fabric_list = fabric_selector_widget.get_selected_list()

        try:
            qty = int(qty_val)
            if qty < 1: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive number.")
            return

        if not fabric_list:
            messagebox.showwarning("Warning", "Please select at least one fabric.")
            return

        try:
            order_id = ObjectId(order_data["_id"])
        except Exception:
            messagebox.showerror("Error", "Invalid Order ID format.")
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # [NEW] Списання тканини зі складу (обробляємо кожну тканину)
        # Припустимо, що на 1 виріб йде по 1 метру кожної обраної тканини (або розділена логіка)
        # Якщо в майбутньому треба буде вказувати метраж окремо, треба змінювати віджет.
        # Поки що списуємо: (Кількість виробів * 1) для кожної тканини.
        
        # Створюємо "плоский" список для списання. 
        # Якщо qty=3 і обрано [Шовк, Бавовна], то треба списати 3м Шовку і 3м Бавовни.
        # Функція process_fabric_usage приймає список імен і списує по 1 за кожне ім'я.
        
        fabrics_to_deduct = []
        for _ in range(qty):
            fabrics_to_deduct.extend(fabric_list)
            
        mongodb_functions.process_fabric_usage(fabrics_to_deduct)

        # Оновлення замовлення
        update_fields = {
            "status": "New", 
            "fabric_used": fabric_list, 
            "accessories_used": access_val,
            "quantity": qty,
            "total_estimated_price": float(calculated_total), 
            "order_date": current_time
        }

        success = mongodb_functions.update_document(
            collection_name="orders",          
            query={"_id": order_id},           
            update_data={"$set": update_fields} 
        )

        if success:
            messagebox.showinfo("Success", "Order confirmed successfully!")
            self.refresh_list() 
        else:
            messagebox.showerror("Error", "Failed to update order in database.")