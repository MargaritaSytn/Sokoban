from tkinter import Tk, Label, Entry, Button, messagebox, Toplevel
from database import login_user, register_user

class LoginWindow:
    """Окно входа и регистрации"""
    def __init__(self):
        self.result = None
        self.user_id = None
        self.username = None
        
    def show_login(self):
        """Показать окно входа"""
        root = Tk()
        root.title("Вход в Sokoban")
        root.geometry("300x200")
        root.resizable(False, False)
        
        Label(root, text="Логин:").pack(pady=5)
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
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
        
        def on_register():
            reg_window = Toplevel(root)
            reg_window.title("Регистрация")
            reg_window.geometry("300x200")
            
            Label(reg_window, text="Логин:").pack(pady=5)
            reg_user = Entry(reg_window)
            reg_user.pack(pady=5)
            
            Label(reg_window, text="Пароль:").pack(pady=5)
            reg_pass = Entry(reg_window, show="*")
            reg_pass.pack(pady=5)
            
            def do_register():
                username = reg_user.get()
                password = reg_pass.get()
                if len(username) < 3 or len(password) < 3:
                    messagebox.showerror("Ошибка", "Логин и пароль должны быть минимум 3 символа!")
                    return
                success, message = register_user(username, password)
                if success:
                    messagebox.showinfo("Успех", message)
                    reg_window.destroy()
                else:
                    messagebox.showerror("Ошибка", message)
            
            Button(reg_window, text="Зарегистрироваться", command=do_register).pack(pady=10)
        
        Button(root, text="Войти", command=on_login).pack(pady=5)
        Button(root, text="Регистрация", command=on_register).pack(pady=5)
        
        root.mainloop()
        return self.result, self.user_id, self.username