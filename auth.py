import bcrypt
import json
import os
from datetime import datetime

class AuthSystem:
    def __init__(self, db_file='database/users.json'):
        """Initialize the authentication system"""
        self.db_file = db_file
        
        # Create database folder if it doesn't exist
        os.makedirs('database', exist_ok=True)
        
        # Create users.json file if it doesn't exist
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({}, f)
    
    def load_users(self):
        """Load all users from the JSON file"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users):
        """Save users to the JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(users, f, indent=4)
    
    def register(self, username, password):
        """
        Register a new user
        Returns: (success: bool, message: str)
        """
        # Validation checks
        if not username or not password:
            return False, "Username and password cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Load existing users
        users = self.load_users()
        
        # Check if username already exists
        if username in users:
            return False, "Username already exists"
        
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Store user data
        users[username] = {
            'password': hashed_password.decode('utf-8'),  # Convert bytes to string for JSON
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'face_registered': False
        }
        
        # Save to file
        self.save_users(users)
        
        return True, "Registration successful!"
    
    def login(self, username, password):
        """
        Login a user with password
        Returns: (success: bool, message: str)
        """
        # Validation
        if not username or not password:
            return False, "Username and password cannot be empty"
        
        # Load users
        users = self.load_users()
        
        # Check if user exists
        if username not in users:
            return False, "Username does not exist"
        
        # Get stored hashed password
        stored_hash = users[username]['password'].encode('utf-8')
        
        # Compare passwords using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True, f"Welcome back, {username}!"
        else:
            return False, "Incorrect password"
    
    def login_with_face(self, username):
        """
        Login a user using only face verification (no password needed).
        This is called AFTER face recognition has already verified the user's identity.
        
        Args:
            username: Username verified by face recognition system
        
        Returns:
            Tuple (success: bool, message: str)
        """
        # Validation
        if not username:
            return False, "Username cannot be empty"
        
        # Load users
        users = self.load_users()
        
        # Check if user exists
        if username not in users:
            return False, "Username does not exist in database"
        
        # Face was already verified by face_auth system
        # So we allow login without password verification
        return True, f"Welcome back, {username}! (Face authenticated)"
    
    def user_exists(self, username):
        """Check if a username exists"""
        users = self.load_users()
        return username in users
    
    def get_user_info(self, username):
        """Get information about a user"""
        users = self.load_users()
        return users.get(username, None)
    
    def update_user(self, username, updates):
        """Update user information"""
        users = self.load_users()
        if username in users:
            users[username].update(updates)
            self.save_users(users)
            return True
        return False
    
    def mark_face_registered(self, username):
        """Mark that a user has registered their face"""
        return self.update_user(username, {'face_registered': True})
    
    def is_face_registered(self, username):
        """Check if a user has registered their face"""
        info = self.get_user_info(username)
        if info:
            return info.get('face_registered', False)
        return False


# Testing the authentication system
if __name__ == "__main__":
    # Create auth system instance
    auth = AuthSystem()
    
    print("=" * 50)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Register a new user
    print("\n[TEST 1] Registering user 'alice'...")
    success, message = auth.register('alice', 'password123')
    print(f"Result: {message}")
    
    # Test 2: Try to register same user again
    print("\n[TEST 2] Trying to register 'alice' again...")
    success, message = auth.register('alice', 'password123')
    print(f"Result: {message}")
    
    # Test 3: Register another user
    print("\n[TEST 3] Registering user 'bob'...")
    success, message = auth.register('bob', 'secure456')
    print(f"Result: {message}")
    
    # Test 4: Login with correct password
    print("\n[TEST 4] Login 'alice' with correct password...")
    success, message = auth.login('alice', 'password123')
    print(f"Result: {message}")
    
    # Test 5: Login with wrong password
    print("\n[TEST 5] Login 'alice' with wrong password...")
    success, message = auth.login('alice', 'wrongpassword')
    print(f"Result: {message}")
    
    # Test 6: Login non-existent user
    print("\n[TEST 6] Login non-existent user 'charlie'...")
    success, message = auth.login('charlie', 'anypassword')
    print(f"Result: {message}")
    
    # Test 7: Check user info
    print("\n[TEST 7] Getting info for 'alice'...")
    info = auth.get_user_info('alice')
    print(f"User info: {info}")
    
    # Test 8: Face login (NEW!)
    print("\n[TEST 8] Face login for 'alice'...")
    success, message = auth.login_with_face('alice')
    print(f"Result: {message}")
    
    # Test 9: Mark face registered
    print("\n[TEST 9] Marking face as registered for 'alice'...")
    auth.mark_face_registered('alice')
    print(f"Face registered status: {auth.is_face_registered('alice')}")
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED!")
    print("=" * 50)