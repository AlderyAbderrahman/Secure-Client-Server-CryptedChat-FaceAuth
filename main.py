import os
import sys
import subprocess
import platform

# ============================================================================
# MAIN MENU
# ============================================================================

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🔐 SECURE CRYPTOGRAPHY CHAT SYSTEM 🔐          ║
    ║                                                           ║
    ║              Complete Messaging Application               ║
    ║           with Authentication & Encryption                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Print main menu"""
    print("\n" + "="*60)
    print("MAIN MENU")
    print("="*60)
    print("1. 🖥️  Start Server")
    print("2. 💬 Start Chat Client")
    print("3. 🔓 Caesar Cipher Breaker")
    print("4. 🔐 Test All Ciphers")
    print("5. 👤 Test Authentication System")
    print("6. 👁️  Face Authentication System")
    print("7. 📚 View Documentation")
    print("8. ❌ Exit")
    print("="*60)


def start_server():
    """Start the chat server"""
    clear_screen()
    print("\n" + "="*60)
    print("STARTING SERVER")
    print("="*60)
    print("\nThe server will start in a new window...")
    print("Keep this window open while clients connect.")
    print("\nPress Ctrl+C in the server window to stop.")
    print("="*60)
    
    input("\nPress Enter to start the server...")
    
    try:
        import server
        server.main()
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Failed to start server: {e}")
        input("\nPress Enter to continue...")


def start_client():
    """Start a chat client"""
    clear_screen()
    print("\n" + "="*60)
    print("STARTING CHAT CLIENT")
    print("="*60)
    print("\nMake sure the server is running first!")
    print("You can start multiple clients to test messaging.")
    print("="*60)
    
    input("\nPress Enter to start the client...")
    
    try:
        import client
        client.main()
    except Exception as e:
        print(f"\n[ERROR] Failed to start client: {e}")
        input("\nPress Enter to continue...")


def run_caesar_breaker():
    """Run Caesar cipher breaker"""
    clear_screen()
    print("\n" + "="*60)
    print("CAESAR CIPHER BREAKER")
    print("="*60)
    print("\nAutomatic decryption without knowing the key!")
    print("="*60)
    
    input("\nPress Enter to start...")
    
    try:
        import caesar_breaker
        caesar_breaker.interactive_mode()
    except Exception as e:
        print(f"\n[ERROR] Failed to start Caesar breaker: {e}")
        input("\nPress Enter to continue...")


def test_ciphers():
    """Test all cipher implementations"""
    clear_screen()
    print("\n" + "="*60)
    print("TESTING ALL CIPHERS")
    print("="*60)
    print("\nRunning automated tests for all encryption methods...")
    print("="*60)
    
    input("\nPress Enter to start tests...")
    
    try:
        from ciphers import test_all
        test_all()
        
        print("\n\n" + "="*60)
        print("Do you want to try the interactive cipher menu?")
        choice = input("Enter 'y' for yes, any other key to return: ").lower()
        
        if choice == 'y':
            from ciphers import interactive_mode
            interactive_mode()
        
    except Exception as e:
        print(f"\n[ERROR] Failed to run cipher tests: {e}")
    
    input("\nPress Enter to continue...")


def test_authentication():
    """Test authentication system"""
    clear_screen()
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION SYSTEM")
    print("="*60)
    print("\nYou can test user registration and login.")
    print("="*60)
    
    input("\nPress Enter to start...")
    
    try:
        import test_auth
        test_auth.main()
    except Exception as e:
        print(f"\n[ERROR] Failed to start authentication test: {e}")
    
    input("\nPress Enter to continue...")


def face_authentication():
    """Face authentication system"""
    clear_screen()
    print("\n" + "="*60)
    print("FACE AUTHENTICATION SYSTEM")
    print("="*60)
    print("\nRegister and login using facial recognition!")
    print("Uses OpenCV + LBPH Face Recognizer")
    print("="*60)
    
    input("\nPress Enter to start...")
    
    try:
        import face_auth
        face_auth.interactive_mode()
    except ImportError as e:
        print("\n❌ ERROR: Face authentication requires opencv-contrib-python")
        print("\nInstall it with:")
        print("  pip install opencv-contrib-python")
        print("\nOR if you have opencv-python installed:")
        print("  pip uninstall opencv-python")
        print("  pip install opencv-contrib-python")
    except Exception as e:
        print(f"\n[ERROR] Failed to start face authentication: {e}")
    
    input("\nPress Enter to continue...")


def view_documentation():
    """Display documentation"""
    clear_screen()
    print("\n" + "="*60)
    print("DOCUMENTATION")
    print("="*60)
    
    doc = """
    
📚 PROJECT COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. AUTHENTICATION SYSTEM (auth.py)
   • User registration with password hashing (bcrypt)
   • Secure login system
   • JSON-based user database
   • Password validation

2. FACE AUTHENTICATION (face_auth.py) ⭐ NEW!
   • Face registration using camera
   • Face recognition login
   • LBPH (Local Binary Patterns Histograms) algorithm
   • Secure facial data storage

3. ENCRYPTION CIPHERS (ciphers.py)
   • Caesar Cipher - Simple shift cipher
   • Vigenère Cipher - Polyalphabetic substitution
   • Substitution Cipher - Random letter mapping
   • Transposition Cipher - Columnar rearrangement
   • RSA Cipher - Public key encryption (manually coded)

4. CAESAR BREAKER (caesar_breaker.py)
   • Automatic decryption without key
   • Frequency analysis
   • Dictionary word matching
   • Language detection (English/French)

5. SERVER (server.py)
   • Multi-client connection handling
   • Message routing between users
   • User authentication
   • Broadcast support

6. CLIENT (client.py)
   • GUI chat interface (Tkinter)
   • Login/Registration screen
   • Real-time messaging
   • Cipher selection
   • Encryption/Decryption display

7. PROTOCOL (protocol.py)
   • Message formatting (JSON)
   • Encryption/Decryption helpers
   • Key formatting and parsing


🚀 HOW TO USE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Start the Server
   • Run option 1 from main menu
   • Keep server running in background
   • Server listens on localhost:5555

STEP 2: Start Clients
   • Run option 2 from main menu (multiple times)
   • Each client opens in new window
   • Register new users or login

STEP 3: Send Encrypted Messages
   • Select recipient from user list
   • Choose encryption cipher
   • Enter encryption key
   • Type message and send
   • Recipient sees encrypted + decrypted versions

STEP 4: Face Authentication (Optional)
   • Run option 6 from main menu
   • Register your face (30 samples)
   • Use face recognition to login
   • Alternative to password authentication


💡 TESTING FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Option 3: Test Caesar breaker with encrypted messages
- Option 4: Test all ciphers individually
- Option 5: Test registration and login
- Option 6: Test face authentication system


📂 FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

project/
├── main.py              # Main entry point
├── server.py            # Chat server
├── client.py            # GUI chat client
├── protocol.py          # Message protocol
├── auth.py              # Authentication system
├── face_auth.py         # Face authentication ⭐ NEW!
├── ciphers.py           # All encryption methods
├── caesar_breaker.py    # Automatic Caesar decryption
├── test_auth.py         # Authentication testing
├── test_face_auth.py    # Face auth testing ⭐ NEW!
└── database/            # User data storage
    ├── users.json       # User credentials
    ├── face_data.json   # Face metadata ⭐ NEW!
    └── faces/           # Face image samples ⭐ NEW!


🔐 SECURITY FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Passwords hashed with bcrypt (never stored as plain text)
✓ Face authentication with LBPH algorithm
✓ End-to-end encryption (messages encrypted before sending)
✓ Multiple cipher options for different security levels
✓ RSA public-key cryptography support
✓ Secure key exchange protocols


⚠️  REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required Python libraries:
- bcrypt
- tkinter (usually included with Python)
- opencv-contrib-python (for face authentication)

Install with: 
  pip install bcrypt opencv-contrib-python


📝 PROJECT EVALUATION CRITERIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Messaging functionality - Real-time chat
✓ Cipher methods - 5 different encryption algorithms
✓ Authentication - Secure login/registration
✓ Face recognition - LBPH facial authentication ⭐
✓ Identification - User management
✓ Code quality - Clean, documented, working
✓ User guide - Screenshots and instructions


📅 DEMONSTRATION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ All features implemented
✓ Face authentication added
✓ Ready for December 16, 2025 demonstration

    """
    
    print(doc)
    input("\nPress Enter to return to main menu...")


def check_dependencies():
    """Check if required libraries are installed"""
    missing = []
    optional_missing = []
    
    try:
        import bcrypt
    except ImportError:
        missing.append("bcrypt")
    
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    
    try:
        import cv2
        # Check if cv2.face is available (opencv-contrib)
        try:
            cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            optional_missing.append("opencv-contrib-python (face authentication won't work)")
    except ImportError:
        optional_missing.append("opencv-contrib-python (for face authentication)")
    
    if missing:
        print("\n⚠️  WARNING: Missing required libraries!")
        print("\nMissing libraries:", ", ".join(missing))
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing)}")
        input("\nPress Enter to continue anyway...")
        return False
    
    if optional_missing:
        print("\n💡 INFO: Optional features unavailable")
        print("\nMissing:", ", ".join(optional_missing))
        print("\nTo enable face authentication:")
        print("  pip install opencv-contrib-python")
        input("\nPress Enter to continue...")
    
    return True


def check_files():
    """Check if all required files exist"""
    required_files = [
        'server.py',
        'client.py',
        'protocol.py',
        'auth.py',
        'ciphers.py',
        'caesar_breaker.py',
        'test_auth.py'
    ]
    
    optional_files = [
        'face_auth.py',
        'test_face_auth.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("\n❌ ERROR: Missing required files!")
        print("\nMissing files:", ", ".join(missing))
        print("\nPlease make sure all project files are in the same directory.")
        input("\nPress Enter to exit...")
        return False
    
    missing_optional = []
    for file in optional_files:
        if not os.path.exists(file):
            missing_optional.append(file)
    
    if missing_optional:
        print("\n💡 INFO: Some optional files are missing")
        print("Missing:", ", ".join(missing_optional))
        print("Face authentication features may not be available.")
        input("\nPress Enter to continue...")
    
    return True


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program loop"""
    
    # Check dependencies and files
    if not check_files():
        sys.exit(1)
    
    check_dependencies()
    
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            start_server()
        
        elif choice == '2':
            start_client()
        
        elif choice == '3':
            run_caesar_breaker()
        
        elif choice == '4':
            test_ciphers()
        
        elif choice == '5':
            test_authentication()
        
        elif choice == '6':
            face_authentication()
        
        elif choice == '7':
            view_documentation()
        
        elif choice == '8':
            clear_screen()
            print("\n" + "="*60)
            print("Thank you for using Secure Cryptography Chat System!")
            print("="*60)
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 8.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n" + "="*60)
        print("Program interrupted by user")
        print("="*60)
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)