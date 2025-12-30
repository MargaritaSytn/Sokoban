from tkinter import Tk, Label, Entry, Button, messagebox, Toplevel
from database import login_user, register_user

class LoginWindow:
    # Вікно входу та реєстрації
    def __init__(self):
        self.result = None
        self.user_id = None
        self.username = None
        
    def show_login(self):
        # Показати вікно входу
        root = Tk()
        root.title("Вхід у Sokoban")
        root.geometry("300x200")
        root.resizable(False, False)
        
        Label(root, text="Логін:").pack(pady=5)
        entry_user = Entry(root)
        entry_user.pack(pady=5)
        
        Label(root, text="Пароль:").pack(pady=5)
        entry_pass = Entry(root, show="*")
        entry_pass.pack(pady=5)
        
        def on_login():
            username = entry_user.get()
            password = entry_pass.get()
            success, user_id = login_user(username, password)
            if success:
                self.result = True
                self.user_id = user_id
                self.username = username
                root.destroy()
            else:
                messagebox.showerror("Помилка", "Невірний логін або пароль!")
        
        def on_register():
            reg_window = Toplevel(root)
            reg_window.title("Реєстрація")
            reg_window.geometry("300x200")
            
            Label(reg_window, text="Логін:").pack(pady=5)
            reg_user = Entry(reg_window)
            reg_user.pack(pady=5)
            
            Label(reg_window, text="Пароль:").pack(pady=5)
            reg_pass = Entry(reg_window, show="*")
            reg_pass.pack(pady=5)
            
            def do_register():
                username = reg_user.get()
                password = reg_pass.get()
                if len(username) < 3 or len(password) < 3:
                    messagebox.showerror("Помилка", "Логін та пароль мають бути мінімум 3 символи!")
                    return
                success, message = register_user(username, password)
                if success:
                    messagebox.showinfo("Успіх", message)
                    reg_window.destroy()
                else:
                    messagebox.showerror("Помилка", message)
            
            Button(reg_window, text="Зареєструватися", command=do_register).pack(pady=10)
        
        Button(root, text="Увійти", command=on_login).pack(pady=5)
        Button(root, text="Реєстрація", command=on_register).pack(pady=5)
        
        root.mainloop()
        return self.result, self.user_id, self.username