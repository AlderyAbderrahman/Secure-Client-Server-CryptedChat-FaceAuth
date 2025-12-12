import tkinter as tk
from tkinter import messagebox
from auth import AuthSystem

class AuthGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Authentication System")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.auth = AuthSystem()
        
        # Title
        title = tk.Label(root, text="Authentication System", 
                        font=("Arial", 20, "bold"), fg="blue")
        title.pack(pady=20)
        
        # Username
        tk.Label(root, text="Username:", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(root, text="Password:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(root, font=("Arial", 12), width=30, show="*")
        self.password_entry.pack(pady=5)
        
        # Buttons Frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        # Register Button
        register_btn = tk.Button(button_frame, text="Register", 
                                font=("Arial", 12, "bold"),
                                bg="green", fg="white",
                                width=10, command=self.register)
        register_btn.grid(row=0, column=0, padx=10)
        
        # Login Button
        login_btn = tk.Button(button_frame, text="Login", 
                             font=("Arial", 12, "bold"),
                             bg="blue", fg="white",
                             width=10, command=self.login)
        login_btn.grid(row=0, column=1, padx=10)
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        success, message = self.auth.register(username, password)
        
        if success:
            messagebox.showinfo("Success", message)
            self.clear_fields()
        else:
            messagebox.showerror("Error", message)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        success, message = self.auth.login(username, password)
        
        if success:
            messagebox.showinfo("Success", message)
            self.clear_fields()
        else:
            messagebox.showerror("Error", message)
    
    def clear_fields(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthGUI(root)
    root.mainloop()