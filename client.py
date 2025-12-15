import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, simpledialog
from protocol import (
    MessageType, send_message, receive_message,
    encrypt_message, decrypt_message, format_cipher_key
)
from ciphers import generate_substitution_key, rsa_generate_keypair

# ============================================================================
# FACE AUTHENTICATION IMPORT
# ============================================================================
try:
    from face_auth import FaceAuthSystem
    FACE_AUTH_AVAILABLE = True
except ImportError:
    FACE_AUTH_AVAILABLE = False
    print("⚠️  Face authentication not available. Install opencv-contrib-python to enable.")

# ============================================================================
# CLIENT CONFIGURATION
# ============================================================================

HOST = 'localhost'
PORT = 5555

# ============================================================================
# CLIENT CLASS
# ============================================================================

class ChatClient:
    def __init__(self, root):
        """Initialize the chat client"""
        self.root = root
        self.root.title("Secure Chat Client")
        self.root.geometry("800x600")
        
        self.socket = None
        self.username = None
        self.connected = False
        self.online_users = []
        
        # Cipher keys storage (LOCAL ONLY - never transmitted)
        self.substitution_key = None
        self.rsa_public_key = None
        self.rsa_private_key = None
        
        # Pending encrypted messages waiting for decryption
        self.pending_messages = []  # List of (sender, cipher, ciphertext)
        
        # Face authentication system
        if FACE_AUTH_AVAILABLE:
            self.face_auth = FaceAuthSystem()
        else:
            self.face_auth = None
        
        # Show login screen
        self.show_login_screen()
    
    # ========================================================================
    # LOGIN/REGISTER SCREEN WITH FACE AUTH
    # ========================================================================
    
    def show_login_screen(self):
        """Display login/register screen with face authentication option"""
        self.login_frame = tk.Frame(self.root, bg="#2c3e50")
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(self.login_frame, text="🔐 Secure Chat System",
                        font=("Arial", 24, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=30)
        
        # Login form
        form_frame = tk.Frame(self.login_frame, bg="#34495e", padx=40, pady=40)
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Username:", font=("Arial", 12),
                bg="#34495e", fg="white").grid(row=0, column=0, sticky="w", pady=10)
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Password:", font=("Arial", 12),
                bg="#34495e", fg="white").grid(row=1, column=0, sticky="w", pady=10)
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Buttons Frame 1: Password Authentication
        button_frame1 = tk.Frame(form_frame, bg="#34495e")
        button_frame1.grid(row=2, column=0, columnspan=2, pady=10)
        
        login_btn = tk.Button(button_frame1, text="🔑 Login with Password", 
                             font=("Arial", 11, "bold"),
                             bg="#27ae60", fg="white", width=20, 
                             command=self.login)
        login_btn.grid(row=0, column=0, padx=5)
        
        register_btn = tk.Button(button_frame1, text="📝 Register Account", 
                                font=("Arial", 11, "bold"),
                                bg="#3498db", fg="white", width=20, 
                                command=self.register)
        register_btn.grid(row=0, column=1, padx=5)
        
        # Separator and Face Authentication (if available)
        if FACE_AUTH_AVAILABLE:
            separator = tk.Label(form_frame, text="— OR —", font=("Arial", 10, "bold"),
                               bg="#34495e", fg="#95a5a6")
            separator.grid(row=3, column=0, columnspan=2, pady=15)
            
            # Buttons Frame 2: Face Authentication
            button_frame2 = tk.Frame(form_frame, bg="#34495e")
            button_frame2.grid(row=4, column=0, columnspan=2, pady=10)
            
            face_login_btn = tk.Button(button_frame2, text="👤 Login with Face", 
                                      font=("Arial", 11, "bold"),
                                      bg="#9b59b6", fg="white", width=20,
                                      command=self.login_with_face)
            face_login_btn.grid(row=0, column=0, padx=5)
            
            register_face_btn = tk.Button(button_frame2, text="📸 Register Face", 
                                         font=("Arial", 11, "bold"),
                                         bg="#e67e22", fg="white", width=20,
                                         command=self.register_face)
            register_face_btn.grid(row=0, column=1, padx=5)
            
            # Info label
            info_label = tk.Label(form_frame, 
                                 text="💡 Face authentication: Login instantly without password!",
                                 font=("Arial", 9), bg="#34495e", fg="#95a5a6",
                                 wraplength=400)
            info_label.grid(row=5, column=0, columnspan=2, pady=10)
        else:
            # Show message if face auth not available
            warning_label = tk.Label(form_frame,
                                    text="⚠️  Face authentication unavailable\nInstall: pip install opencv-contrib-python",
                                    font=("Arial", 9), bg="#34495e", fg="#e74c3c",
                                    wraplength=400)
            warning_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def connect_to_server(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.connected = True
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
            return False
    
    # ========================================================================
    # PASSWORD AUTHENTICATION
    # ========================================================================
    
    def register(self):
        """Register a new user with password"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Invalid Input", "Please enter username and password")
            return
        
        if not self.connected:
            if not self.connect_to_server():
                return
        
        # Send register request
        send_message(self.socket, MessageType.REGISTER, {
            "username": username,
            "password": password
        })
    
    def login(self):
        """Login user with password"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Invalid Input", "Please enter username and password")
            return
        
        if not self.connected:
            if not self.connect_to_server():
                return
        
        self.username = username
        
        # Send login request
        send_message(self.socket, MessageType.LOGIN, {
            "username": username,
            "password": password
        })
    
    # ========================================================================
    # FACE AUTHENTICATION METHODS
    # ========================================================================
    
    def register_face(self):
        """Register face for a user"""
        if not FACE_AUTH_AVAILABLE:
            messagebox.showerror("Not Available", 
                               "Face authentication requires opencv-contrib-python.\n\n"
                               "Install it with:\npip install opencv-contrib-python")
            return
        
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showwarning("Username Required", 
                                 "Please enter your username in the field above")
            return
        
        # Show consent dialog
        result = messagebox.askyesno("Face Registration",
                                     f"Register facial biometric data for '{username}'?\n\n"
                                     "This will:\n"
                                     "• Capture 30 face samples from your camera\n"
                                     "• Store face data securely\n"
                                     "• Allow password-free biometric login\n\n"
                                     "Make sure you're in a well-lit area.\n\n"
                                     "Do you consent to facial data collection?")
        
        if not result:
            messagebox.showinfo("Cancelled", "Face registration cancelled")
            return
        
        # Minimize window while capturing
        self.root.iconify()
        
        try:
            # Capture face samples
            success, message = self.face_auth.capture_face_samples(username, num_samples=30)
            
            # Restore window
            self.root.deiconify()
            
            if success:
                messagebox.showinfo("Success", 
                                  f"Face registered successfully!\n\n{message}\n\n"
                                  "You can now use 'Login with Face' for instant access!")
            else:
                messagebox.showerror("Registration Failed", 
                                   f"Failed to register face:\n{message}")
        
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Face registration error:\n{e}")
    
    def login_with_face(self):
        """Login using face recognition - NO PASSWORD REQUIRED!"""
        if not FACE_AUTH_AVAILABLE:
            messagebox.showerror("Not Available", 
                               "Face authentication requires opencv-contrib-python.\n\n"
                               "Install it with:\npip install opencv-contrib-python")
            return
        
        # Check if any faces are registered
        registered_faces = self.face_auth.list_registered_faces()
        if not registered_faces:
            messagebox.showwarning("No Faces Registered",
                                 "No facial data found.\n\n"
                                 "Please register your face first using the 'Register Face' button.")
            return
        
        messagebox.showinfo("Face Recognition",
                          "Camera will open for face recognition.\n\n"
                          "Position your face clearly in frame.\n"
                          "Press 'q' to cancel.")
        
        # Minimize window while recognizing
        self.root.iconify()
        
        try:
            # Recognize face
            success, result = self.face_auth.recognize_face(confidence_threshold=70)
            
            # Restore window
            self.root.deiconify()
            
            if success:
                # Face recognized - set username and login DIRECTLY (no password!)
                self.username = result
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, result)
                
                # Connect to server if not already connected
                if not self.connected:
                    if not self.connect_to_server():
                        return
                
                # Send face login request - NO PASSWORD NEEDED!
                print(f"[CLIENT] Sending face login for: {result}")
                send_message(self.socket, MessageType.LOGIN_FACE, {
                    "username": result
                })
                
                # Show success message
                messagebox.showinfo("Face Recognized", 
                                  f"Welcome back, {result}!\n\n"
                                  "Logging you in with face authentication...\n"
                                  "No password required! 🎉")
                
            else:
                messagebox.showerror("Recognition Failed", 
                                   f"Face not recognized:\n{result}\n\n"
                                   "Make sure:\n"
                                   "• You have registered your face\n"
                                   "• You're in good lighting\n"
                                   "• Your face is clearly visible")
        
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Face recognition error:\n{e}")
    
    # ========================================================================
    # CHAT SCREEN
    # ========================================================================
    
    def show_chat_screen(self):
        """Display main chat screen"""
        # Destroy login frame
        self.login_frame.destroy()
        
        # Update window title
        self.root.title(f"Secure Chat - {self.username}")
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== LEFT PANEL: Users List =====
        left_panel = tk.Frame(main_frame, bg="#34495e", width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH)
        
        tk.Label(left_panel, text="👥 Online Users", font=("Arial", 12, "bold"),
                bg="#34495e", fg="white").pack(pady=10)
        
        self.users_listbox = tk.Listbox(left_panel, font=("Arial", 11),
                                        bg="#2c3e50", fg="white",
                                        selectbackground="#3498db")
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== RIGHT PANEL: Chat =====
        right_panel = tk.Frame(main_frame, bg="#ecf0f1")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(right_panel, font=("Arial", 10),
                                                      bg="white", fg="black",
                                                      wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for colors
        self.chat_display.tag_config("sent", foreground="#27ae60")
        self.chat_display.tag_config("received", foreground="#3498db")
        self.chat_display.tag_config("system", foreground="#95a5a6", font=("Arial", 9, "italic"))
        self.chat_display.tag_config("encrypted", foreground="#e74c3c")
        self.chat_display.tag_config("pending", foreground="#e67e22", font=("Arial", 9, "italic"))
        
        # ===== BOTTOM PANEL: Message Input =====
        bottom_panel = tk.Frame(right_panel, bg="#ecf0f1")
        bottom_panel.pack(fill=tk.X, padx=10, pady=10)
        
        # Cipher selection
        cipher_frame = tk.Frame(bottom_panel, bg="#ecf0f1")
        cipher_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cipher_frame, text="Cipher:", font=("Arial", 10),
                bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        self.cipher_var = tk.StringVar(value="caesar")
        cipher_menu = ttk.Combobox(cipher_frame, textvariable=self.cipher_var,
                                   values=["caesar", "vigenere", "substitution", 
                                          "transposition", "rsa"],
                                   state="readonly", width=15)
        cipher_menu.pack(side=tk.LEFT, padx=5)
        cipher_menu.bind("<<ComboboxSelected>>", self.on_cipher_change)
        
        tk.Label(cipher_frame, text="Key:", font=("Arial", 10),
                bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        self.key_entry = tk.Entry(cipher_frame, font=("Arial", 10), width=15)
        self.key_entry.pack(side=tk.LEFT, padx=5)
        self.key_entry.insert(0, "3")  # Default Caesar shift
        
        # Decrypt pending messages button
        decrypt_btn = tk.Button(cipher_frame, text="🔓 Decrypt Messages", 
                               font=("Arial", 9),
                               bg="#9b59b6", fg="white",
                               command=self.decrypt_pending_messages)
        decrypt_btn.pack(side=tk.RIGHT, padx=5)
        
        # Recipient selection
        recipient_frame = tk.Frame(bottom_panel, bg="#ecf0f1")
        recipient_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(recipient_frame, text="To:", font=("Arial", 10),
                bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        self.recipient_var = tk.StringVar(value="ALL")
        self.recipient_menu = ttk.Combobox(recipient_frame, textvariable=self.recipient_var,
                                          values=["ALL"], state="readonly", width=20)
        self.recipient_menu.pack(side=tk.LEFT, padx=5)
        
        # Message input
        input_frame = tk.Frame(bottom_panel, bg="#ecf0f1")
        input_frame.pack(fill=tk.X, pady=5)
        
        self.message_entry = tk.Entry(input_frame, font=("Arial", 11))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        send_btn = tk.Button(input_frame, text="📤 Send", font=("Arial", 11, "bold"),
                           bg="#27ae60", fg="white", command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add welcome message
        self.add_system_message(f"Welcome, {self.username}! 🎉")
        self.add_system_message("🔐 END-TO-END ENCRYPTION ENABLED")
        self.add_system_message("⚠️  Share encryption keys with recipients in person!")
        self.add_system_message("💡 Recipients must click '🔓 Decrypt Messages' and enter the key you share")
        if FACE_AUTH_AVAILABLE and self.username in self.face_auth.list_registered_faces():
            self.add_system_message("👤 Face authentication is registered for your account")
    
    def on_cipher_change(self, event=None):
        """Handle cipher selection change"""
        cipher = self.cipher_var.get()
        
        if cipher == "caesar":
            self.key_entry.config(state=tk.NORMAL)
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "3")
            self.add_system_message("💡 Caesar cipher: Enter shift value (0-25)")
        
        elif cipher == "vigenere":
            self.key_entry.config(state=tk.NORMAL)
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "KEY")
            self.add_system_message("💡 Vigenère cipher: Enter keyword")
        
        elif cipher == "substitution":
            if not self.substitution_key:
                self.substitution_key = generate_substitution_key()
                self.add_system_message("💡 Substitution cipher: New random key generated")
                self.add_system_message(f"🔑 Key (first 5): {format_cipher_key('substitution', self.substitution_key)}")
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "AUTO")
            self.key_entry.config(state=tk.DISABLED)
        
        elif cipher == "transposition":
            self.key_entry.config(state=tk.NORMAL)
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "4312")
            self.add_system_message("💡 Transposition cipher: Enter numeric key")
        
        elif cipher == "rsa":
            if not self.rsa_public_key:
                self.add_system_message("🔐 Generating RSA keys... (this may take a moment)")
                self.root.update()
                self.rsa_public_key, self.rsa_private_key = rsa_generate_keypair(bits=512)
                self.add_system_message("✓ RSA keys generated successfully!")
                self.add_system_message(f"🔑 Public key: {format_cipher_key('rsa', self.rsa_public_key)}")
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "AUTO")
            self.key_entry.config(state=tk.DISABLED)
    
    def add_system_message(self, message):
        """Add system message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[SYSTEM] {message}\n", "system")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def add_sent_message(self, recipient, plaintext, ciphertext, cipher):
        """Add sent message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You → {recipient} ({cipher}):\n", "sent")
        self.chat_display.insert(tk.END, f"  Plain: {plaintext}\n", "sent")
        
        # Format ciphertext display
        if isinstance(ciphertext, list):
            display_cipher = str(ciphertext[:3]) + "..." if len(ciphertext) > 3 else str(ciphertext)
        else:
            display_cipher = ciphertext
        
        self.chat_display.insert(tk.END, f"  Encrypted: {display_cipher}\n\n", "encrypted")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def add_pending_encrypted_message(self, sender, cipher, ciphertext):
        """Add encrypted message that needs decryption"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"🔒 ENCRYPTED from {sender} ({cipher}):\n", "pending")
        
        # Format ciphertext display
        if isinstance(ciphertext, list):
            display_cipher = str(ciphertext[:3]) + "..." if len(ciphertext) > 3 else str(ciphertext)
        else:
            display_cipher = ciphertext
        
        self.chat_display.insert(tk.END, f"  {display_cipher}\n", "encrypted")
        self.chat_display.insert(tk.END, f"  ⚠️  Click '🔓 Decrypt Messages' and enter the key from {sender}\n\n", "pending")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def add_decrypted_message(self, sender, plaintext, cipher):
        """Add successfully decrypted message"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"✓ {sender} → You ({cipher}):\n", "received")
        self.chat_display.insert(tk.END, f"  {plaintext}\n\n", "received")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send encrypted message WITHOUT KEY"""
        plaintext = self.message_entry.get().strip()
        
        if not plaintext:
            return
        
        recipient = self.recipient_var.get()
        cipher_type = self.cipher_var.get()
        
        # Get the appropriate key (LOCAL ONLY)
        if cipher_type == "substitution":
            key = self.substitution_key
        elif cipher_type == "rsa":
            key = self.rsa_public_key
        else:
            key = self.key_entry.get().strip()
            if not key:
                messagebox.showwarning("No Key", "Please enter an encryption key")
                return
        
        try:
            # Encrypt the message
            ciphertext = encrypt_message(plaintext, cipher_type, key)
            
            # Send to server WITHOUT KEY - only encrypted content
            if recipient == "ALL":
                send_message(self.socket, MessageType.BROADCAST, {
                    "cipher": cipher_type,
                    "content": ciphertext
                })
            else:
                send_message(self.socket, MessageType.MESSAGE, {
                    "to": recipient,
                    "cipher": cipher_type,
                    "content": ciphertext
                })
            
            # Display in chat
            self.add_sent_message(recipient, plaintext, ciphertext, cipher_type)
            self.add_system_message(f"💡 Tell {recipient} the key: {key if cipher_type not in ['substitution', 'rsa'] else 'Share securely!'}")
            
            # Clear input
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to encrypt message:\n{e}")
    
    def decrypt_pending_messages(self):
        """Prompt user to enter key and decrypt pending messages"""
        if not self.pending_messages:
            messagebox.showinfo("No Messages", "No encrypted messages waiting for decryption")
            return
        
        # Show dialog to enter decryption key
        key_dialog = tk.Toplevel(self.root)
        key_dialog.title("Decrypt Messages")
        key_dialog.geometry("400x300")
        key_dialog.configure(bg="#34495e")
        
        tk.Label(key_dialog, text="Enter Decryption Key", font=("Arial", 14, "bold"),
                bg="#34495e", fg="white").pack(pady=20)
        
        tk.Label(key_dialog, text=f"{len(self.pending_messages)} encrypted message(s) waiting",
                font=("Arial", 10), bg="#34495e", fg="#95a5a6").pack(pady=5)
        
        tk.Label(key_dialog, text="Key:", font=("Arial", 11),
                bg="#34495e", fg="white").pack(pady=10)
        
        key_entry = tk.Entry(key_dialog, font=("Arial", 12), width=25)
        key_entry.pack(pady=10)
        key_entry.focus()
        
        result_label = tk.Label(key_dialog, text="", font=("Arial", 9),
                               bg="#34495e", fg="#e74c3c", wraplength=350)
        result_label.pack(pady=10)
        
        def try_decrypt():
            key = key_entry.get().strip()
            if not key:
                result_label.config(text="Please enter a key", fg="#e74c3c")
                return
            
            decrypted_count = 0
            failed_count = 0
            remaining = []
            
            for sender, cipher_type, ciphertext in self.pending_messages:
                try:
                    plaintext = decrypt_message(ciphertext, cipher_type, key)
                    self.add_decrypted_message(sender, plaintext, cipher_type)
                    decrypted_count += 1
                except:
                    remaining.append((sender, cipher_type, ciphertext))
                    failed_count += 1
            
            self.pending_messages = remaining
            
            if decrypted_count > 0:
                result_label.config(text=f"✓ Decrypted {decrypted_count} message(s)!", fg="#27ae60")
                if failed_count == 0:
                    key_dialog.after(1500, key_dialog.destroy)
            else:
                result_label.config(text="❌ Wrong key or incompatible cipher", fg="#e74c3c")
        
        tk.Button(key_dialog, text="🔓 Decrypt", font=("Arial", 11, "bold"),
                 bg="#27ae60", fg="white", command=try_decrypt).pack(pady=10)
        
        tk.Button(key_dialog, text="Cancel", font=("Arial", 10),
                 bg="#95a5a6", fg="white", command=key_dialog.destroy).pack(pady=5)
        
        key_entry.bind('<Return>', lambda e: try_decrypt())
    
    # ========================================================================
    # RECEIVE MESSAGES
    # ========================================================================
    
    def receive_messages(self):
        """Receive messages from server"""
        while self.connected:
            try:
                message = receive_message(self.socket)
                
                if not message:
                    break
                
                msg_type = message.get("type")
                data = message.get("data", {})
                
                if msg_type == MessageType.SUCCESS:
                    self.handle_success(data)
                
                elif msg_type == MessageType.ERROR:
                    self.handle_error(data)
                
                elif msg_type == MessageType.MESSAGE:
                    self.handle_incoming_message(data)
                
                elif msg_type == MessageType.BROADCAST:
                    self.handle_incoming_broadcast(data)
                
                elif msg_type == MessageType.USER_LIST:
                    self.handle_user_list(data)
            
            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
                break
        
        self.connected = False
    
    def handle_success(self, data):
        """Handle success message from server"""
        message_text = data.get("message", "Success")
        
        if "Registration successful" in message_text:
            messagebox.showinfo("Success", "Registration successful! Please login.")
        
        elif "Welcome back" in message_text or "Face authenticated" in message_text:
            # Login successful - show chat screen
            self.root.after(0, self.show_chat_screen)
    
    def handle_error(self, data):
        """Handle error message from server"""
        error_message = data.get("message", "Unknown error")
        messagebox.showerror("Error", error_message)
    
    def handle_incoming_message(self, data):
        """Handle incoming private message - NO KEY, JUST ENCRYPTED CONTENT"""
        sender = data.get("from")
        cipher_type = data.get("cipher")
        ciphertext = data.get("content")
        
        # Store as pending (waiting for user to enter key)
        self.pending_messages.append((sender, cipher_type, ciphertext))
        
        # Show in chat as encrypted
        self.root.after(0, lambda: self.add_pending_encrypted_message(
            sender, cipher_type, ciphertext
        ))
    
    def handle_incoming_broadcast(self, data):
        """Handle incoming broadcast message"""
        # Same as private message
        self.handle_incoming_message(data)
    
    def handle_user_list(self, data):
        """Handle updated user list"""
        users = data.get("users", [])
        self.online_users = [u for u in users if u != self.username]
        
        # Update UI
        self.root.after(0, self.update_user_list)
    
    def update_user_list(self):
        """Update the users listbox"""
        if hasattr(self, 'users_listbox'):
            self.users_listbox.delete(0, tk.END)
            
            for user in self.online_users:
                self.users_listbox.insert(tk.END, f"🟢 {user}")
            
            # Update recipient dropdown
            recipients = ["ALL"] + self.online_users
            self.recipient_menu['values'] = recipients
    
    def disconnect(self):
        """Disconnect from server"""
        if self.connected:
            send_message(self.socket, MessageType.DISCONNECT, {})
            self.socket.close()
            self.connected = False


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to start the client"""
    root = tk.Tk()
    client = ChatClient(root)
    
    # Handle window close
    def on_closing():
        client.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()