import tkinter as tk
from tkinter import messagebox
import test

def handle_click():
    # 1. Дістаємо дані з полів
    name = name_Entry.get()
    number = number_Entry.get()
    done = done_var.get()

    if not name or not number:
        messagebox.showwarning("Увага", "Заповніть всі поля!")
        return

    # 2. Викликаємо функцію з сусіднього файлу
    success = test.add_user_to_db(name, number, done)

    # 3. Якщо запис пройшов успішно - очищаємо поля ТУТ
    if success:
        name_Entry.delete(0, tk.END)
        number_Entry.delete(0, tk.END)
        done_Checkbutton.deselect()
        messagebox.showinfo("Успіх", "Дані збережено!")
        refresh_user_list()

def summarise_data():
    users = test.get_all_users()
    if not users:
        messagebox.showinfo("Інформація", "Немає даних для підсумовування.")
        return
    sumT = 0
    sumF = 0
    for user in users:
        if user['done']:
            sumT +=1
        else:
            sumF +=1
    messagebox.showinfo("Успіх", "В сумі: \nDone людей: " + str(sumT) + "\nНе Done людей: " + str(sumF))
    return


mainWindow = tk.Tk()  
mainWindow.title("MongoDB Data Viewer")
mainWindow.geometry("1000x800")

tk.Label(mainWindow, text="Введіть Ім'я:").pack()
name_Entry = tk.Entry(mainWindow)
name_Entry.pack()

tk.Label(mainWindow, text="Введіть Номер:").pack()
number_Entry = tk.Entry(mainWindow)
number_Entry.pack()

done_var = tk.BooleanVar() 
done_Checkbutton = tk.Checkbutton(mainWindow, text="Done", variable=done_var)
done_Checkbutton.pack()

proceed_Button = tk.Button(mainWindow, text="Proceed", command=handle_click)
proceed_Button.pack(pady=10)

list_Text = tk.Text(mainWindow, height=30, width=100)
list_Text.pack()

summarise_Button = tk.Button(mainWindow, text="Summarise", command=summarise_data)
summarise_Button.pack(pady=10)


def refresh_user_list():
    users = test.get_all_users()
    list_Text.delete(1.0, tk.END)  # Очищаємо текстове поле
    for user in users:
        list_Text.insert(tk.END, f"Name: {user['name']}, Number: {user['number']}, Done: {user['done']}\n")

refresh_user_list()


mainWindow.mainloop()