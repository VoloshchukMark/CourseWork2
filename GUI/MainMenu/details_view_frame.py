import os
import sys
import tkinter as tk
from tkinter import messagebox
import io
from PIL import Image, ImageTk
from datetime import datetime 

# --- Імпорти утиліт ---
from Utils import mongodb_functions, session

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class DetailsView(tk.Toplevel):
    def __init__(self, parent, item_data, item_type):
        super().__init__(parent)
        
        self.item_data = item_data
        self.item_type = item_type
        
        self.title(f"Details: {item_data.get('name', 'Unknown')}")
        self.geometry("900x600")
        self.configure(bg="white")
        
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()        
        self.focus_set()       
        
        # --- 2. ГОЛОВНИЙ КОНТЕЙНЕР ---
        self.grid_columnconfigure(0, weight=1, uniform="group1") 
        self.grid_columnconfigure(1, weight=1, uniform="group1") 
        self.grid_rowconfigure(0, weight=1)

        # --- ЛІВА ЧАСТИНА (Фото, Назва, Опис) ---
        self.left_frame = tk.Frame(self, bg="white", padx=20, pady=20)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        btn_back = tk.Button(self.left_frame, text="⬅ Back", font=("Arial", 12), 
                             command=self.destroy, bg="#f0f0f0", cursor="hand2")
        btn_back.pack(anchor="w", pady=(0, 20))

        self.image_label = tk.Label(self.left_frame, bg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Завантажуємо зображення з виправленою обробкою
        self.load_large_image()

        name_id_frame = tk.Frame(self.left_frame, bg="white")
        name_id_frame.pack(pady=(20, 10), anchor="w", fill="x")

        tk.Label(name_id_frame, text=self.item_data.get('name', 'Unknown'), 
                 font=("Arial", 24, "bold"), bg="white").pack(side="left")

        item_id = self.item_data.get('_id', '')
        if item_id:
            tk.Label(name_id_frame, text=f"#{item_id}", 
                     font=("Arial", 16), fg="gray", bg="white").pack(side="left", padx=10, anchor="sw", pady=5)

        desc_text = item_data.get('description', 'No description available.')
        desc_lbl = tk.Label(self.left_frame, text=desc_text, font=("Arial", 12), 
                            bg="white", justify="left", wraplength=400, anchor="w")
        desc_lbl.pack(fill=tk.X, anchor="w")


        # --- ПРАВА ЧАСТИНА (Деталі + Кнопка Order) ---
        self.right_frame = tk.Frame(self, bg="#f9f9f9", padx=30, pady=50)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Інформаційні поля
        price_suffix = "UAH" if self.item_type == "model" else "UAH/m"
        self.create_detail_row("Price:", f"{item_data.get('price', 0)} {price_suffix}")
        
        in_stock = item_data.get('in_stock', False)
        stock_text = "In Stock" if in_stock else "Out of Stock"
        stock_color = "#ba86ba" if in_stock else "#502f40"
        self.create_detail_row("Availability:", stock_text, value_color=stock_color)

        tk.Frame(self.right_frame, height=2, bg="#ddd").pack(fill=tk.X, pady=20) 

        if self.item_type == "model":
            self.create_detail_row("Recommended Fabric:", item_data.get('recommended_fabric', '-'))
            self.create_detail_row("Recommended Accessories:", item_data.get('recommended_accessories', '-'))
        else: 
            self.create_detail_row("Supplier ID:", item_data.get('fabric_supplier_id', '-'))
            self.create_detail_row("Color:", item_data.get('fabric_color', '-'))
            self.create_detail_row("Texture:", item_data.get('fabric_texture', '-'))
            self.create_detail_row("Width:", item_data.get('width', '-'))

        # --- КНОПКА ORDER ---
        btn_container = tk.Frame(self.right_frame, bg="#f9f9f9")
        btn_container.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        if self.item_type == "model":
            self.btn_order = tk.Button(btn_container, text="ADD TO ORDER LIST", 
                                       font=("Arial", 14, "bold"), 
                                       bg="#dda0dd", fg="white", activebackground="#ba86ba",
                                       cursor="hand2", height=2,
                                       command=self.create_draft_order)
            self.btn_order.pack(fill=tk.X)

            if not in_stock:
                 self.btn_order.config(state="disabled", bg="#e0e0e0", cursor="arrow")
        else:
            tk.Label(btn_container, text="Material Only (Cannot be ordered directly)", 
                     font=("Arial", 10, "italic"), fg="gray", bg="#f9f9f9").pack()

    def create_detail_row(self, label, value, value_color="black"):
        frame = tk.Frame(self.right_frame, bg="#f9f9f9")
        frame.pack(fill=tk.X, pady=10)
        
        tk.Label(frame, text=label, font=("Arial", 12, "bold"), fg="gray", bg="#f9f9f9").pack(side=tk.LEFT)
        tk.Label(frame, text=value, font=("Arial", 14), fg=value_color, bg="#f9f9f9").pack(side=tk.RIGHT)

    def load_large_image(self):
        image_binary = self.item_data.get('original_image_binary')
        
        if image_binary:
            try:
                img_data = io.BytesIO(image_binary)
                pil_img = Image.open(img_data)
                pil_img.thumbnail((400, 400))
                
                # === ВИПРАВЛЕНА ЛОГІКА ОБРОБКИ ===
                if not self.item_data.get('in_stock', True):
                    # 1. Перевіряємо прозорість
                    if pil_img.mode in ('RGBA', 'LA') or (pil_img.mode == 'P' and 'transparency' in pil_img.info):
                        # Створюємо білий фон
                        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                        # Конвертуємо в RGBA для маски
                        pil_img = pil_img.convert("RGBA")
                        # Накладаємо картинку на білий фон
                        bg.paste(pil_img, mask=pil_img.split()[3])
                        pil_img = bg
                    
                    # 2. Робимо чорно-білим
                    pil_img = pil_img.convert("L")
                # =================================

                self.photo = ImageTk.PhotoImage(pil_img)
                self.image_label.config(image=self.photo)
            except Exception as e:
                print(f"Details Image Error: {e}")
                self.image_label.config(text="Image Error")
        else:
            self.image_label.config(text="No Image", bg="#eee")

    def create_draft_order(self):
        if not hasattr(session, 'current_user') or not session.current_user:
            messagebox.showerror("Error", "You must be logged in to make an order.")
            return

        user_login = session.current_user.login

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        order_doc = {
            "customer_login": user_login,
            "product_id": str(self.item_data.get("_id")),
            "product_name": self.item_data.get("name"),
            "product_type": self.item_type,
            "base_price": self.item_data.get("price", 0),
            "fabric_used": self.item_data.get("recommended_fabric", ""),
            "accessories_used": self.item_data.get("recommended_accessories", ""),
            "quantity": 1,
            "image": self.item_data.get("original_image_binary"),
            "status": "Draft",
            "created_at": current_time
        }

        try:
            print(f"Creating order for user: {user_login}, Product: {order_doc['product_name']}")
            mongodb_functions.upload_to_db("orders", order_doc)
            messagebox.showinfo("Success", "Item added to your Order List!\nGo to 'My Orders' to finalize details.")
            self.destroy() 
            
        except Exception as e:
            print(f"Database Error: {e}")
            messagebox.showerror("Error", f"Failed to create order: {e}")