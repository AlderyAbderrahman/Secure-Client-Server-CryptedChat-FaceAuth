import random
import string
import math

# ============================================================================
# RSA CIPHER
# ============================================================================

def is_prime(n, k=5):
    """
    Miller-Rabin primality test to check if a number is prime.
    
    Args:
        n: Number to test
        k: Number of testing rounds (higher = more accurate)
    
    Returns:
        True if n is probably prime, False if composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def generate_prime(bits=512):
    """
    Generate a random prime number with specified bit length.
    
    Args:
        bits: Bit length of the prime number
    
    Returns:
        A prime number
    """
    while True:
        # Generate random odd number
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 1  # Set MSB and LSB to 1
        
        if is_prime(num):
            return num


def gcd(a, b):
    """
    Calculate Greatest Common Divisor using Euclidean algorithm.
    
    Args:
        a, b: Two integers
    
    Returns:
        GCD of a and b
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) where gcd = a*x + b*y
    
    Args:
        a, b: Two integers
    
    Returns:
        Tuple (gcd, x, y)
    """
    if a == 0:
        return b, 0, 1
    
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd_val, x, y


def mod_inverse(e, phi):
    """
    Calculate modular multiplicative inverse using Extended Euclidean Algorithm.
    Find d such that (e * d) % phi = 1
    
    Args:
        e: Public exponent
        phi: Euler's totient function result
    
    Returns:
        Modular inverse of e mod phi
    """
    gcd_val, x, _ = extended_gcd(e, phi)
    
    if gcd_val != 1:
        raise ValueError("Modular inverse does not exist")
    
    return x % phi


def rsa_generate_keypair(bits=512, verbose=False):
    """
    Generate RSA public and private key pair.
    
    Args:
        bits: Bit length for prime numbers (default 512)
        verbose: Print generation steps
    
    Returns:
        Tuple ((e, n), (d, n)) representing (public_key, private_key)
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"GENERATING RSA KEY PAIR ({bits}-bit)")
        print(f"{'='*60}")
    
    # Step 1: Generate two large prime numbers p and q
    if verbose:
        print("\n[1/5] Generating prime p...")
    p = generate_prime(bits)
    if verbose:
        print(f"      p generated ({p.bit_length()} bits)")
    
    if verbose:
        print("\n[2/5] Generating prime q...")
    q = generate_prime(bits)
    if verbose:
        print(f"      q generated ({q.bit_length()} bits)")
    
    # Step 2: Calculate n = p * q
    if verbose:
        print("\n[3/5] Calculating n = p * q...")
    n = p * q
    if verbose:
        print(f"      n has {n.bit_length()} bits")
    
    # Step 3: Calculate Euler's totient function φ(n) = (p-1)(q-1)
    if verbose:
        print("\n[4/5] Calculating φ(n) = (p-1)(q-1)...")
    phi = (p - 1) * (q - 1)
    
    # Step 4: Choose public exponent e (commonly 65537)
    e = 65537
    
    # Make sure e and phi are coprime
    if gcd(e, phi) != 1:
        if verbose:
            print("\n      e and φ(n) not coprime, finding suitable e...")
        e = 3
        while gcd(e, phi) != 1:
            e += 2
    
    if verbose:
        print(f"\n      Public exponent e = {e}")
    
    # Step 5: Calculate private exponent d
    if verbose:
        print("\n[5/5] Calculating private exponent d...")
    d = mod_inverse(e, phi)
    
    if verbose:
        print(f"\n{'='*60}")
        print("KEY GENERATION COMPLETE!")
        print(f"{'='*60}")
    
    # Public key: (e, n), Private key: (d, n)
    return ((e, n), (d, n))


def rsa_encrypt(message, public_key):
    """
    Encrypt a message using RSA public key.
    
    Args:
        message: String message to encrypt
        public_key: Tuple (e, n)
    
    Returns:
        List of encrypted integers
    """
    e, n = public_key
    
    # Convert message to bytes then to integers
    message_bytes = message.encode('utf-8')
    
    # Encrypt each byte
    encrypted = []
    for byte in message_bytes:
        # c = m^e mod n
        encrypted_byte = pow(byte, e, n)
        encrypted.append(encrypted_byte)
    
    return encrypted


def rsa_decrypt(encrypted_message, private_key):
    """
    Decrypt an encrypted message using RSA private key.
    
    Args:
        encrypted_message: List of encrypted integers
        private_key: Tuple (d, n)
    
    Returns:
        Decrypted string message
    """
    d, n = private_key
    
    # Decrypt each encrypted byte
    decrypted_bytes = []
    for encrypted_byte in encrypted_message:
        # m = c^d mod n
        decrypted_byte = pow(encrypted_byte, d, n)
        decrypted_bytes.append(decrypted_byte)
    
    # Convert bytes back to string
    message = bytes(decrypted_bytes).decode('utf-8')
    return message


def format_rsa_key(key):
    """Format RSA key for display."""
    exp, mod = key
    return f"Exponent: {exp}\nModulus: {mod}"


# ============================================================================
# CAESAR CIPHER
# ============================================================================

def caesar_encrypt(text, shift):
    """
    Encrypt text using Caesar cipher.
    
    Args:
        text: Plain text to encrypt
        shift: Number of positions to shift (0-25)
    
    Returns:
        Encrypted text
    """
    result = ""
    
    for char in text:
        if char.isupper():
            # Shift uppercase letters
            result += chr((ord(char) + shift - 65) % 26 + 65)
        elif char.islower():
            # Shift lowercase letters
            result += chr((ord(char) + shift - 97) % 26 + 97)
        else:
            # Keep non-alphabetic characters unchanged
            result += char
    
    return result


def caesar_decrypt(text, shift):
    """
    Decrypt Caesar cipher text.
    
    Args:
        text: Encrypted text
        shift: Number of positions that were shifted
    
    Returns:
        Decrypted text
    """
    # Decryption is just encryption with negative shift
    return caesar_encrypt(text, -shift)


# ============================================================================
# VIGENÈRE CIPHER
# ============================================================================

def vigenere_encrypt(text, key):
    """
    Encrypt text using Vigenère cipher.
    
    Args:
        text: Plain text to encrypt
        key: Keyword for encryption
    
    Returns:
        Encrypted text
    """
    result = ""
    key = key.upper()
    key_index = 0
    
    for char in text:
        if char.isalpha():
            # Get the shift value from the key
            shift = ord(key[key_index % len(key)]) - 65
            
            if char.isupper():
                result += chr((ord(char) + shift - 65) % 26 + 65)
            else:
                result += chr((ord(char) + shift - 97) % 26 + 97)
            
            key_index += 1
        else:
            # Keep non-alphabetic characters unchanged
            result += char
    
    return result


def vigenere_decrypt(text, key):
    """
    Decrypt Vigenère cipher text.
    
    Args:
        text: Encrypted text
        key: Keyword used for encryption
    
    Returns:
        Decrypted text
    """
    result = ""
    key = key.upper()
    key_index = 0
    
    for char in text:
        if char.isalpha():
            # Get the shift value from the key (negative for decryption)
            shift = ord(key[key_index % len(key)]) - 65
            
            if char.isupper():
                result += chr((ord(char) - shift - 65) % 26 + 65)
            else:
                result += chr((ord(char) - shift - 97) % 26 + 97)
            
            key_index += 1
        else:
            result += char
    
    return result


# ============================================================================
# SUBSTITUTION CIPHER
# ============================================================================

def generate_substitution_key():
    """
    Generate a random substitution key.
    
    Returns:
        Dictionary mapping each letter to another letter
    """
    alphabet = list(string.ascii_uppercase)
    shuffled = alphabet.copy()
    random.shuffle(shuffled)
    
    # Create mapping dictionary
    key = {}
    for i in range(26):
        key[alphabet[i]] = shuffled[i]
        key[alphabet[i].lower()] = shuffled[i].lower()
    
    return key


def substitution_encrypt(text, key):
    """
    Encrypt text using substitution cipher.
    
    Args:
        text: Plain text to encrypt
        key: Substitution mapping dictionary
    
    Returns:
        Encrypted text
    """
    result = ""
    
    for char in text:
        if char.isalpha():
            result += key[char]
        else:
            result += char
    
    return result


def substitution_decrypt(text, key):
    """
    Decrypt substitution cipher text.
    
    Args:
        text: Encrypted text
        key: Substitution mapping dictionary used for encryption
    
    Returns:
        Decrypted text
    """
    # Create reverse mapping
    reverse_key = {v: k for k, v in key.items()}
    
    result = ""
    for char in text:
        if char.isalpha():
            result += reverse_key[char]
        else:
            result += char
    
    return result


def format_substitution_key(key):
    """Format substitution key for display."""
    result = "Substitution Key:\n"
    result += "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z\n"
    result += " ".join([key[chr(65 + i)] for i in range(26)])
    return result


# ============================================================================
# TRANSPOSITION CIPHER (Columnar Transposition)
# ============================================================================

def transposition_encrypt(text, key):
    """
    Encrypt text using columnar transposition cipher.
    
    Args:
        text: Plain text to encrypt
        key: Numeric key (e.g., "3142" or "SECRET")
    
    Returns:
        Encrypted text
    """
    # Convert text key to numeric if necessary
    if isinstance(key, str) and not key.isdigit():
        # Convert word key to numeric (alphabetical order)
        key_order = sorted(list(key))
        key = ''.join([str(key_order.index(char) + 1) for char in key])
    
    key = str(key)
    num_cols = len(key)
    num_rows = math.ceil(len(text) / num_cols)
    
    # Pad text with 'X' if needed
    text = text + 'X' * (num_cols * num_rows - len(text))
    
    # Create grid
    grid = []
    for i in range(num_rows):
        row = []
        for j in range(num_cols):
            row.append(text[i * num_cols + j])
        grid.append(row)
    
    # Read columns in key order
    result = ""
    key_order = sorted(enumerate(key), key=lambda x: x[1])
    
    for col_index, _ in key_order:
        for row in grid:
            result += row[col_index]
    
    return result


def transposition_decrypt(text, key):
    """
    Decrypt columnar transposition cipher text.
    
    Args:
        text: Encrypted text
        key: Numeric key used for encryption
    
    Returns:
        Decrypted text
    """
    # Convert text key to numeric if necessary
    if isinstance(key, str) and not key.isdigit():
        key_order = sorted(list(key))
        key = ''.join([str(key_order.index(char) + 1) for char in key])
    
    key = str(key)
    num_cols = len(key)
    num_rows = math.ceil(len(text) / num_cols)
    
    # Create empty grid
    grid = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    
    # Fill grid column by column in key order
    key_order = sorted(enumerate(key), key=lambda x: x[1])
    text_index = 0
    
    for col_index, _ in key_order:
        for row in range(num_rows):
            grid[row][col_index] = text[text_index]
            text_index += 1
    
    # Read row by row
    result = ""
    for row in grid:
        result += ''.join(row)
    
    # Remove padding 'X' from the end
    return result.rstrip('X')


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_rsa():
    """Test RSA cipher."""
    print("\n" + "="*60)
    print("TESTING RSA CIPHER")
    print("="*60)
    
    print("\nGenerating RSA keys (this may take a moment)...")
    public_key, private_key = rsa_generate_keypair(bits=512, verbose=False)
    
    text = "HELLO WORLD"
    
    print(f"\nOriginal text: {text}")
    print(f"Public key exponent: {public_key[0]}")
    print(f"Modulus bit length: {public_key[1].bit_length()}")
    
    encrypted = rsa_encrypt(text, public_key)
    print(f"\nEncrypted (first 3 blocks): {encrypted[:3]}...")
    print(f"Total encrypted blocks: {len(encrypted)}")
    
    decrypted = rsa_decrypt(encrypted, private_key)
    print(f"\nDecrypted: {decrypted}")
    
    print(f"Match: {'✓ SUCCESS' if text == decrypted else '✗ FAILED'}")


def test_caesar():
    """Test Caesar cipher."""
    print("\n" + "="*60)
    print("TESTING CAESAR CIPHER")
    print("="*60)
    
    text = "HELLO WORLD"
    shift = 3
    
    print(f"\nOriginal text: {text}")
    print(f"Shift: {shift}")
    
    encrypted = caesar_encrypt(text, shift)
    print(f"Encrypted: {encrypted}")
    
    decrypted = caesar_decrypt(encrypted, shift)
    print(f"Decrypted: {decrypted}")
    
    print(f"Match: {'✓ SUCCESS' if text == decrypted else '✗ FAILED'}")


def test_vigenere():
    """Test Vigenère cipher."""
    print("\n" + "="*60)
    print("TESTING VIGENÈRE CIPHER")
    print("="*60)
    
    text = "HELLO WORLD"
    key = "KEY"
    
    print(f"\nOriginal text: {text}")
    print(f"Key: {key}")
    
    encrypted = vigenere_encrypt(text, key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = vigenere_decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
    
    print(f"Match: {'✓ SUCCESS' if text == decrypted else '✗ FAILED'}")


def test_substitution():
    """Test Substitution cipher."""
    print("\n" + "="*60)
    print("TESTING SUBSTITUTION CIPHER")
    print("="*60)
    
    text = "HELLO WORLD"
    key = generate_substitution_key()
    
    print(f"\nOriginal text: {text}")
    print(f"\n{format_substitution_key(key)}")
    
    encrypted = substitution_encrypt(text, key)
    print(f"\nEncrypted: {encrypted}")
    
    decrypted = substitution_decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
    
    print(f"Match: {'✓ SUCCESS' if text == decrypted else '✗ FAILED'}")


def test_transposition():
    """Test Transposition cipher."""
    print("\n" + "="*60)
    print("TESTING TRANSPOSITION CIPHER")
    print("="*60)
    
    text = "HELLO WORLD"
    key = "4312"
    
    print(f"\nOriginal text: {text}")
    print(f"Key: {key}")
    
    encrypted = transposition_encrypt(text, key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = transposition_decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
    
    print(f"Match: {'✓ SUCCESS' if text == decrypted else '✗ FAILED'}")


def test_all():
    """Run all cipher tests."""
    test_caesar()
    test_vigenere()
    test_substitution()
    test_transposition()
    test_rsa()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    """Interactive menu for testing ciphers."""
    substitution_key = None
    rsa_public_key = None
    rsa_private_key = None
    
    while True:
        print("\n" + "="*60)
        print("CIPHER TESTING MENU")
        print("="*60)
        print("1. Caesar Cipher")
        print("2. Vigenère Cipher")
        print("3. Substitution Cipher")
        print("4. Transposition Cipher")
        print("5. RSA Cipher")
        print("6. Run All Tests")
        print("7. Exit")
        print("="*60)
        
        choice = input("\nChoose an option (1-7): ").strip()
        
        if choice == "1":
            print("\n--- CAESAR CIPHER ---")
            text = input("Enter text: ").upper()
            shift = int(input("Enter shift (0-25): "))
            
            encrypted = caesar_encrypt(text, shift)
            print(f"\nEncrypted: {encrypted}")
            
            decrypted = caesar_decrypt(encrypted, shift)
            print(f"Decrypted: {decrypted}")
        
        elif choice == "2":
            print("\n--- VIGENÈRE CIPHER ---")
            text = input("Enter text: ").upper()
            key = input("Enter key: ").upper()
            
            encrypted = vigenere_encrypt(text, key)
            print(f"\nEncrypted: {encrypted}")
            
            decrypted = vigenere_decrypt(encrypted, key)
            print(f"Decrypted: {decrypted}")
        
        elif choice == "3":
            print("\n--- SUBSTITUTION CIPHER ---")
            
            if substitution_key is None:
                print("Generating new substitution key...")
                substitution_key = generate_substitution_key()
            
            print(f"\n{format_substitution_key(substitution_key)}")
            
            text = input("\nEnter text: ").upper()
            
            encrypted = substitution_encrypt(text, substitution_key)
            print(f"\nEncrypted: {encrypted}")
            
            decrypted = substitution_decrypt(encrypted, substitution_key)
            print(f"Decrypted: {decrypted}")
            
            regenerate = input("\nGenerate new key for next time? (y/n): ").lower()
            if regenerate == 'y':
                substitution_key = None
        
        elif choice == "4":
            print("\n--- TRANSPOSITION CIPHER ---")
            text = input("Enter text: ").upper().replace(" ", "")
            key = input("Enter numeric key (e.g., 4312): ")
            
            encrypted = transposition_encrypt(text, key)
            print(f"\nEncrypted: {encrypted}")
            
            decrypted = transposition_decrypt(encrypted, key)
            print(f"Decrypted: {decrypted}")
        
        elif choice == "5":
            print("\n--- RSA CIPHER ---")
            
            if rsa_public_key is None or rsa_private_key is None:
                print("Generating RSA keys (this may take a moment)...")
                rsa_public_key, rsa_private_key = rsa_generate_keypair(bits=512, verbose=True)
            else:
                print(f"\nUsing existing keys:")
                print(f"Public exponent: {rsa_public_key[0]}")
                print(f"Modulus: {rsa_public_key[1].bit_length()} bits")
            
            text = input("\nEnter text to encrypt: ")
            
            encrypted = rsa_encrypt(text, rsa_public_key)
            print(f"\nEncrypted (first 5 blocks): {encrypted[:5]}...")
            print(f"Total blocks: {len(encrypted)}")
            
            verify = input("\nDecrypt to verify? (y/n): ").lower()
            if verify == 'y':
                decrypted = rsa_decrypt(encrypted, rsa_private_key)
                print(f"Decrypted: {decrypted}")
                print(f"Match: {'✓ SUCCESS' if text == decrypted else '✗ FAILED'}")
            
            regenerate = input("\nGenerate new RSA keys for next time? (y/n): ").lower()
            if regenerate == 'y':
                rsa_public_key = None
                rsa_private_key = None
        
        elif choice == "6":
            test_all()
        
        elif choice == "7":
            print("\nGoodbye! 🔐")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("CRYPTOGRAPHY IMPLEMENTATIONS")
    print("="*60)
    print("\nAvailable Ciphers:")
    print("1. Caesar Cipher - Shift cipher")
    print("2. Vigenère Cipher - Polyalphabetic substitution")
    print("3. Substitution Cipher - Letter mapping")
    print("4. Transposition Cipher - Columnar transposition")
    print("5. RSA Cipher - Public key encryption")
    
    interactive_mode()