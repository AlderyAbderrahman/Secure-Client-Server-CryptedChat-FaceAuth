import json
from ciphers import (
    caesar_encrypt, caesar_decrypt,
    vigenere_encrypt, vigenere_decrypt,
    substitution_encrypt, substitution_decrypt, generate_substitution_key,
    transposition_encrypt, transposition_decrypt,
    rsa_encrypt, rsa_decrypt, rsa_generate_keypair
)

# ============================================================================
# MESSAGE PROTOCOL
# ============================================================================

class MessageType:
    """Message type constants"""
    LOGIN = "login"
    LOGIN_FACE = "login_face"  # ← ADD THIS
    REGISTER = "register"
    MESSAGE = "message"
    BROADCAST = "broadcast"
    USER_LIST = "user_list"
    DISCONNECT = "disconnect"
    ERROR = "error"
    SUCCESS = "success"


def create_message(msg_type, data):
    """
    Create a standardized message.
    
    Args:
        msg_type: Type of message (from MessageType class)
        data: Dictionary with message data
    
    Returns:
        JSON string
    """
    message = {
        "type": msg_type,
        "data": data
    }
    return json.dumps(message)


def parse_message(json_string):
    """
    Parse a JSON message.
    
    Args:
        json_string: JSON formatted string
    
    Returns:
        Dictionary with 'type' and 'data' keys
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return None


# ============================================================================
# CIPHER PROTOCOL
# ============================================================================

def encrypt_message(plaintext, cipher_type, key):
    """
    Encrypt a message using specified cipher.
    
    Args:
        plaintext: Message to encrypt
        cipher_type: Type of cipher ('caesar', 'vigenere', 'substitution', 'transposition', 'rsa')
        key: Encryption key (format depends on cipher type)
    
    Returns:
        Encrypted message (string or list for RSA)
    """
    if cipher_type == "caesar":
        return caesar_encrypt(plaintext, int(key))
    
    elif cipher_type == "vigenere":
        return vigenere_encrypt(plaintext, key)
    
    elif cipher_type == "substitution":
        # Key should be a dictionary
        return substitution_encrypt(plaintext, key)
    
    elif cipher_type == "transposition":
        return transposition_encrypt(plaintext, key)
    
    elif cipher_type == "rsa":
        # Key should be tuple (e, n)
        encrypted = rsa_encrypt(plaintext, key)
        return encrypted  # List of integers
    
    else:
        return plaintext


def decrypt_message(ciphertext, cipher_type, key):
    """
    Decrypt a message using specified cipher.
    
    Args:
        ciphertext: Encrypted message
        cipher_type: Type of cipher
        key: Decryption key
    
    Returns:
        Decrypted message
    """
    if cipher_type == "caesar":
        return caesar_decrypt(ciphertext, int(key))
    
    elif cipher_type == "vigenere":
        return vigenere_decrypt(ciphertext, key)
    
    elif cipher_type == "substitution":
        return substitution_decrypt(ciphertext, key)
    
    elif cipher_type == "transposition":
        return transposition_decrypt(ciphertext, key)
    
    elif cipher_type == "rsa":
        # Key should be tuple (d, n)
        return rsa_decrypt(ciphertext, key)
    
    else:
        return ciphertext


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_cipher_key(cipher_type, key):
    """
    Format cipher key for transmission.
    
    Args:
        cipher_type: Type of cipher
        key: The key object
    
    Returns:
        JSON-serializable key
    """
    if cipher_type == "substitution":
        # Convert dictionary to list of tuples
        return [[k, v] for k, v in key.items()]
    
    elif cipher_type == "rsa":
        # Convert tuple to list
        return list(key)
    
    else:
        return key


def parse_cipher_key(cipher_type, key_data):
    """
    Parse received cipher key.
    
    Args:
        cipher_type: Type of cipher
        key_data: Received key data
    
    Returns:
        Properly formatted key
    """
    if cipher_type == "substitution":
        # Convert list of tuples back to dictionary
        return {k: v for k, v in key_data}
    
    elif cipher_type == "rsa":
        # Convert list back to tuple
        return tuple(key_data)
    
    else:
        return key_data


def send_message(socket, msg_type, data):
    """
    Send a message through socket.
    
    Args:
        socket: Socket object
        msg_type: Message type
        data: Data dictionary
    """
    try:
        message = create_message(msg_type, data)
        # Add message delimiter for proper parsing
        message_with_delimiter = message + "\n"
        socket.send(message_with_delimiter.encode('utf-8'))
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def receive_message(socket, buffer_size=65536):
    """
    Receive and parse a message from socket.
    Handles larger messages (especially for RSA).
    
    Args:
        socket: Socket object
        buffer_size: Buffer size for receiving (increased for RSA)
    
    Returns:
        Parsed message dictionary or None
    """
    try:
        # Receive data with larger buffer for RSA messages
        data = socket.recv(buffer_size).decode('utf-8')
        if not data:
            return None
        
        # Handle multiple messages or partial messages
        # Split by newline delimiter
        messages = data.strip().split('\n')
        
        # Parse the first complete message
        if messages:
            return parse_message(messages[0])
        
        return None
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None