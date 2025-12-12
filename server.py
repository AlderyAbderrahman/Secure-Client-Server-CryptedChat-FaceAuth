import socket
import threading
import json
from protocol import MessageType, create_message, parse_message, send_message, receive_message
from auth import AuthSystem

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

HOST = 'localhost'
PORT = 5555

# ============================================================================
# SERVER CLASS
# ============================================================================

class ChatServer:
    def handle_face_login(self, client_socket, data):
        username = data.get("username")
        
        print(f"[FACE LOGIN] Attempting face login: {username}")
        
        # Use face-specific login method
        success, message = self.auth.login_with_face(username)
        
        if success:
            # Check if user already logged in
            if username in self.clients.values():
                send_message(client_socket, MessageType.ERROR, 
                           {"message": "User already logged in"})
                print(f"[FACE LOGIN] Failed: {username} already logged in")
                return None
            
            # Add to clients list
            self.clients[client_socket] = username
            send_message(client_socket, MessageType.SUCCESS, {"message": message})
            print(f"[FACE LOGIN] Success: {username}")
            
            # Send user list to new user
            self.send_user_list(client_socket)
            
            # Broadcast updated user list to all
            self.broadcast_user_list()
            
            return username
        else:
            send_message(client_socket, MessageType.ERROR, {"message": message})
            print(f"[FACE LOGIN] Failed: {message}")
            return None
    
    def __init__(self, host=HOST, port=PORT):
        """Initialize the chat server"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {socket: username}
        self.auth = AuthSystem()
        self.running = False
        
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print("=" * 60)
            print("CHAT SERVER STARTED")
            print("=" * 60)
            print(f"Host: {self.host}")
            print(f"Port: {self.port}")
            print("Waiting for connections...")
            print("=" * 60)
            
            self.accept_connections()
            
        except Exception as e:
            print(f"Error starting server: {e}")
            self.running = False
    
    def accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"\n[NEW CONNECTION] {address[0]}:{address[1]}")
                
                # Start a new thread to handle this client
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                thread.daemon = True
                thread.start()
                
                print(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        username = None
        
        try:
            while self.running:
                # Receive message from client
                message = receive_message(client_socket)
                
                if not message:
                    break
                
                msg_type = message.get("type")
                data = message.get("data", {})
                
                # Handle different message types
                if msg_type == MessageType.REGISTER:
                    self.handle_register(client_socket, data)
                
                elif msg_type == MessageType.LOGIN:
                    username = self.handle_login(client_socket, data)
                
                elif msg_type == MessageType.MESSAGE:
                    if username:
                        self.handle_message(client_socket, username, data)
                    else:
                        send_message(client_socket, MessageType.ERROR, 
                                   {"message": "Not logged in"})
                
                elif msg_type == MessageType.BROADCAST:
                    if username:
                        self.handle_broadcast(client_socket, username, data)
                
                elif msg_type == MessageType.USER_LIST:
                    self.send_user_list(client_socket)

                elif msg_type == MessageType.LOGIN_FACE:
                     username = self.handle_face_login(client_socket, data)

                
                elif msg_type == MessageType.DISCONNECT:
                    break
        
        except Exception as e:
            print(f"[ERROR] {address}: {e}")
        
        finally:
            # Clean up
            if username and client_socket in self.clients:
                del self.clients[client_socket]
                print(f"[DISCONNECTED] {username} ({address[0]}:{address[1]})")
                print(f"[ACTIVE CONNECTIONS] {len(self.clients)}")
                
                # Notify others
                self.broadcast_user_list()
            
            try:
                client_socket.close()
            except:
                pass
    
    def handle_register(self, client_socket, data):
        """Handle user registration"""
        username = data.get("username")
        password = data.get("password")
        
        print(f"[REGISTER] Attempting to register: {username}")
        
        success, message = self.auth.register(username, password)
        
        if success:
            send_message(client_socket, MessageType.SUCCESS, {"message": message})
            print(f"[REGISTER] Success: {username}")
        else:
            send_message(client_socket, MessageType.ERROR, {"message": message})
            print(f"[REGISTER] Failed: {message}")
    
    def handle_login(self, client_socket, data):
        """Handle user login"""
        username = data.get("username")
        password = data.get("password")
        
        print(f"[LOGIN] Attempting login: {username}")
        
        success, message = self.auth.login(username, password)
        
        if success:
            # Check if user already logged in
            if username in self.clients.values():
                send_message(client_socket, MessageType.ERROR, 
                           {"message": "User already logged in"})
                print(f"[LOGIN] Failed: {username} already logged in")
                return None
            
            # Add to clients list FIRST
            self.clients[client_socket] = username
            
            # Send success message
            send_message(client_socket, MessageType.SUCCESS, {"message": message})
            print(f"[LOGIN] Success: {username}")
            
            # Now broadcast updated user list to ALL clients (including the new one)
            self.broadcast_user_list()
            
            return username
        else:
            send_message(client_socket, MessageType.ERROR, {"message": message})
            print(f"[LOGIN] Failed: {message}")
            return None
    
    def handle_message(self, sender_socket, sender_username, data):
        """Handle private message between users"""
        recipient = data.get("to")
        cipher_type = data.get("cipher")
        cipher_key = data.get("key")
        encrypted_content = data.get("content")
        
        print(f"[MESSAGE] {sender_username} → {recipient} (cipher: {cipher_type})")
        
        # Find recipient socket
        recipient_socket = None
        for sock, username in self.clients.items():
            if username == recipient:
                recipient_socket = sock
                break
        
        if recipient_socket:
            # Forward the encrypted message
            message_data = {
                "from": sender_username,
                "cipher": cipher_type,
                "key": cipher_key,
                "content": encrypted_content
            }
            send_message(recipient_socket, MessageType.MESSAGE, message_data)
            print(f"[MESSAGE] Delivered to {recipient}")
        else:
            # Recipient not found
            send_message(sender_socket, MessageType.ERROR, 
                       {"message": f"User {recipient} not found or offline"})
            print(f"[MESSAGE] Failed: {recipient} not found")
    
    def handle_broadcast(self, sender_socket, sender_username, data):
        """Handle broadcast message to all users"""
        cipher_type = data.get("cipher")
        cipher_key = data.get("key")
        encrypted_content = data.get("content")
        
        print(f"[BROADCAST] {sender_username} → ALL (cipher: {cipher_type})")
        
        # Send to all clients except sender
        message_data = {
            "from": sender_username,
            "cipher": cipher_type,
            "key": cipher_key,
            "content": encrypted_content
        }
        
        for client_socket, username in self.clients.items():
            if client_socket != sender_socket:
                send_message(client_socket, MessageType.BROADCAST, message_data)
        
        print(f"[BROADCAST] Sent to {len(self.clients) - 1} users")
    
    def send_user_list(self, client_socket):
        """Send list of online users to a client"""
        users = list(self.clients.values())
        send_message(client_socket, MessageType.USER_LIST, {"users": users})
    
    def broadcast_user_list(self):
        """Broadcast updated user list to all clients"""
        users = list(self.clients.values())
        for client_socket in self.clients.keys():
            send_message(client_socket, MessageType.USER_LIST, {"users": users})
    
    def stop(self):
        """Stop the server"""
        print("\n[SHUTDOWN] Stopping server...")
        self.running = False
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[SHUTDOWN] Server stopped")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main server program"""
    server = ChatServer(HOST, PORT)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Keyboard interrupt received")
        server.stop()
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        server.stop()


if __name__ == "__main__":
    main()