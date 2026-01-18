import tkinter as tk
from tkinter import ttk, messagebox
from Utils import mongodb_functions, session
from datetime import datetime

class OrdersHistoryWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title("My Orders History")
        self.geometry("950x600")
        self.configure(bg="white")
        
        self.center_window(950, 600)

        self.headers = [
            ("Model", 130),
            ("Fabric", 130),
            ("Date", 140),
            ("Price", 80),
            ("Status", 100),
            ("Actions", 160)
        ]

        self.create_widgets()
        self.refresh_data()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        title_frame = tk.Frame(self, bg="white")
        title_frame.pack(fill="x", pady=15, padx=20)
        tk.Label(title_frame, text="Orders History", font=("Arial", 20, "bold"), bg="white").pack(side="left")
        
        tk.Button(title_frame, text="Refresh", bg="#f0f0f0", command=self.refresh_data).pack(side="right")

        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.create_table_header()

    def create_table_header(self):
        header_frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0")
        header_frame.pack(fill="x", pady=(0, 2))

        for idx, (title, width) in enumerate(self.headers):
            cell = tk.Frame(header_frame, bg="#e0e0e0", width=width, height=35)
            cell.pack_propagate(False)
            cell.grid(row=0, column=idx, padx=1, pady=1)
            tk.Label(cell, text=title, font=("Arial", 10, "bold"), bg="#e0e0e0").pack(fill="both", expand=True)

    def refresh_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.create_table_header()

        if session.current_user:
            user_login = session.current_user.login
            orders = mongodb_functions.get_orders_by_login(user_login)
            
            if not orders:
                tk.Label(self.scrollable_frame, text="No orders found.", bg="white", font=("Arial", 12)).pack(pady=20)
                return

            for order in orders:
                self.create_row(order)
        else:
            messagebox.showerror("Error", "No user logged in")
            self.destroy()

    def create_row(self, order_data):
        row_frame = tk.Frame(self.scrollable_frame, bg="white", bd=1, relief="solid")
        row_frame.pack(fill="x", pady=2, padx=2)

        model_name = order_data.get("product_name", "Unknown Model")
        
        # [NEW] Обробка: список чи рядок?
        fabric_raw = order_data.get("fabric_used", "-")
        if isinstance(fabric_raw, list):
            fabric_str = ", ".join([str(f) for f in fabric_raw])
        else:
            fabric_str = str(fabric_raw)
            
        price = f"${order_data.get('total_estimated_price', 0)}"
        status = order_data.get("status", "Processing")
        order_id = order_data.get("_id")

        order_date = order_data.get("order_date", "-")
        delivery_date = order_data.get("delivery_date", None)
        
        if status == "Delivered" and delivery_date:
            display_date = f"Del: {delivery_date}"
        elif order_date != "-":
            display_date = f"Ord: {order_date}"
        else:
            display_date = "-"

        row_values = [model_name, fabric_str, display_date, price, status]

        for idx, val in enumerate(row_values):
            width = self.headers[idx][1]
            cell = tk.Frame(row_frame, bg="white", width=width, height=40)
            cell.pack_propagate(False)
            cell.grid(row=0, column=idx, padx=1)
            
            fg_color = "black"
            if idx == 4: # Status
                if val == "Delivered": fg_color = "#ac76c2"
                elif val == "New": fg_color = "#8b7ec4"
                elif val == "Canceled": fg_color = "red"

            lbl = tk.Label(cell, text=str(val), font=("Arial", 10), bg="white", fg=fg_color, 
                           anchor="w", wraplength=width-5, justify="left")
            lbl.pack(fill="both", expand=True, padx=5)

        action_width = self.headers[-1][1]
        action_cell = tk.Frame(row_frame, bg="white", width=action_width, height=40)
        action_cell.pack_propagate(False)
        action_cell.grid(row=0, column=len(self.headers)-1, padx=1)
        
        btn_container = tk.Frame(action_cell, bg="white")
        btn_container.pack(expand=True)

        if status == "Delivered":
            tk.Button(btn_container, text="Delete History", bg="#91394C", fg="white", font=("Arial", 8),
                      command=lambda: self.delete_order(order_id)).pack()
        else:
            tk.Button(btn_container, text="Confirm Receipt", bg="#815d88", fg="white", font=("Arial", 8),
                      command=lambda: self.confirm_receipt(order_id)).pack()

    def confirm_receipt(self, order_id):
        if messagebox.askyesno("Confirm", "Did you receive this order? Status will change to 'Delivered'."):
            delivery_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            success = mongodb_functions.update_document(
                "orders",
                {"_id": order_id},
                {
                    "$set": {
                        "status": "Delivered",
                        "delivery_date": delivery_time
                    }
                }
            )
            if success:
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to update status")

    def delete_order(self, order_id):
        if messagebox.askyesno("Delete", "Remove this order from your history permanently?"):
            success = mongodb_functions.delete_document("orders", order_id)
            if success:
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to delete order")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")