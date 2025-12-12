from auth import AuthSystem

def main():
    """Simple command-line interface for testing authentication"""
    auth = AuthSystem()
    
    while True:
        print("\n" + "=" * 50)
        print("AUTHENTICATION SYSTEM")
        print("=" * 50)
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        print("=" * 50)
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == '1':
            # Registration
            print("\n--- REGISTRATION ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            
            success, message = auth.register(username, password)
            print(f"\n{message}")
            
        elif choice == '2':
            # Login
            print("\n--- LOGIN ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            
            success, message = auth.login(username, password)
            print(f"\n{message}")
            
            if success:
                print(f"\nYou are now logged in as: {username}")
                input("Press Enter to continue...")
            
        elif choice == '3':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()