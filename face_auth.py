import cv2
import os
import numpy as np
import json
from datetime import datetime

# ============================================================================
# FACE AUTHENTICATION SYSTEM
# ============================================================================

class FaceAuthSystem:
    def __init__(self, database_dir="database"):
        """
        Initialize the face authentication system.
        
        Args:
            database_dir: Directory to store face data
        """
        self.database_dir = database_dir
        self.faces_dir = os.path.join(database_dir, "faces")
        self.face_data_file = os.path.join(database_dir, "face_data.json")
        
        # Create directories if they don't exist
        os.makedirs(self.faces_dir, exist_ok=True)
        
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize LBPH Face Recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Load existing face data
        self.face_data = self.load_face_data()
        
        # Train recognizer if faces exist
        if self.face_data:
            self.train_recognizer()
    
    def load_face_data(self):
        """Load face data from JSON file."""
        if os.path.exists(self.face_data_file):
            try:
                with open(self.face_data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_face_data(self):
        """Save face data to JSON file."""
        with open(self.face_data_file, 'w') as f:
            json.dump(self.face_data, f, indent=4)
    
    def detect_face(self, frame):
        """
        Detect face in a frame.
        
        Args:
            frame: Input image frame
        
        Returns:
            Tuple (face_region, face_coords) or (None, None)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        if len(faces) > 0:
            # Return the largest face
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, w, h = faces[0]
            face_region = gray[y:y+h, x:x+w]
            return face_region, (x, y, w, h)
        
        return None, None
    
    def capture_face_samples(self, username, num_samples=30):
        """
        Capture multiple face samples for training.
        
        Args:
            username: Username to associate with face
            num_samples: Number of samples to capture
        
        Returns:
            Tuple (success, message)
        """
        if username in self.face_data:
            return False, "Face already registered for this user. Use update instead."
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return False, "Could not access camera"
        
        print("\n" + "="*60)
        print("FACE REGISTRATION")
        print("="*60)
        print(f"Capturing {num_samples} face samples for: {username}")
        print("\nInstructions:")
        print("- Look directly at the camera")
        print("- Move your head slightly for different angles")
        print("- Keep good lighting on your face")
        print("- Press 'q' to cancel")
        print("="*60)
        
        samples = []
        count = 0
        
        while count < num_samples:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect face
            face_region, face_coords = self.detect_face(frame)
            
            # Draw rectangle and info on frame
            display_frame = frame.copy()
            
            if face_region is not None:
                x, y, w, h = face_coords
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Resize face for consistency
                face_resized = cv2.resize(face_region, (200, 200))
                samples.append(face_resized)
                count += 1
                
                # Display progress
                cv2.putText(display_frame, f"Sample {count}/{num_samples}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(display_frame, "Face Detected!", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "No face detected", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(display_frame, "Please position your face in frame", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Face Registration - Press Q to cancel', display_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return False, "Registration cancelled by user"
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(samples) < num_samples:
            return False, f"Only captured {len(samples)} samples. Need {num_samples}."
        
        # Generate unique user ID
        user_id = len(self.face_data) + 1
        
        # Save face samples
        user_face_dir = os.path.join(self.faces_dir, username)
        os.makedirs(user_face_dir, exist_ok=True)
        
        for i, sample in enumerate(samples):
            filename = os.path.join(user_face_dir, f"face_{i}.jpg")
            cv2.imwrite(filename, sample)
        
        # Update face data
        self.face_data[username] = {
            "user_id": user_id,
            "num_samples": len(samples),
            "registered_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_face_data()
        
        # Retrain recognizer
        self.train_recognizer()
        
        print(f"\n✓ Successfully registered {len(samples)} face samples for {username}")
        return True, f"Face registered successfully with {len(samples)} samples"
    
    def train_recognizer(self):
        """Train the face recognizer with all registered faces."""
        if not self.face_data:
            return False, "No face data to train"
        
        faces = []
        labels = []
        
        for username, data in self.face_data.items():
            user_id = data["user_id"]
            user_face_dir = os.path.join(self.faces_dir, username)
            
            if not os.path.exists(user_face_dir):
                continue
            
            for filename in os.listdir(user_face_dir):
                if filename.endswith('.jpg'):
                    filepath = os.path.join(user_face_dir, filename)
                    face_img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                    
                    if face_img is not None:
                        faces.append(face_img)
                        labels.append(user_id)
        
        if len(faces) > 0:
            self.recognizer.train(faces, np.array(labels))
            print(f"✓ Recognizer trained with {len(faces)} face samples")
            return True, f"Trained with {len(faces)} samples"
        
        return False, "No faces to train"
    
    def recognize_face(self, confidence_threshold=70):
        """
        Recognize a face from camera.
        
        Args:
            confidence_threshold: Maximum distance for recognition (lower is more confident)
        
        Returns:
            Tuple (success, username_or_message)
        """
        if not self.face_data:
            return False, "No registered faces in database"
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return False, "Could not access camera"
        
        print("\n" + "="*60)
        print("FACE RECOGNITION LOGIN")
        print("="*60)
        print("Position your face in front of the camera")
        print("Press 'q' to cancel")
        print("="*60)
        
        recognized_user = None
        best_confidence = float('inf')
        frames_checked = 0
        max_frames = 30  # Check for 30 frames
        
        while frames_checked < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect face
            face_region, face_coords = self.detect_face(frame)
            
            display_frame = frame.copy()
            
            if face_region is not None:
                x, y, w, h = face_coords
                
                # Resize for recognition
                face_resized = cv2.resize(face_region, (200, 200))
                
                # Recognize face
                try:
                    user_id, confidence = self.recognizer.predict(face_resized)
                    
                    # Find username from user_id
                    username = None
                    for uname, data in self.face_data.items():
                        if data["user_id"] == user_id:
                            username = uname
                            break
                    
                    if confidence < confidence_threshold:
                        # Face recognized
                        if confidence < best_confidence:
                            best_confidence = confidence
                            recognized_user = username
                        
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(display_frame, f"{username}", 
                                   (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Confidence: {int(100-confidence)}%", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        # Face not recognized
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(display_frame, "Unknown", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
                except Exception as e:
                    print(f"Recognition error: {e}")
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            else:
                cv2.putText(display_frame, "No face detected", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('Face Recognition - Press Q to cancel', display_frame)
            
            frames_checked += 1
            
            # Check for quit
            if cv2.waitKey(100) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return False, "Recognition cancelled by user"
        
        cap.release()
        cv2.destroyAllWindows()
        
        if recognized_user:
            print(f"\n✓ Face recognized: {recognized_user} (confidence: {int(100-best_confidence)}%)")
            return True, recognized_user
        else:
            print("\n✗ Face not recognized")
            return False, "Face not recognized or confidence too low"
    
    def update_face(self, username, num_samples=30):
        """
        Update face samples for existing user.
        
        Args:
            username: Username to update
            num_samples: Number of new samples to capture
        
        Returns:
            Tuple (success, message)
        """
        if username not in self.face_data:
            return False, "User not registered. Use register instead."
        
        # Delete old face samples
        user_face_dir = os.path.join(self.faces_dir, username)
        if os.path.exists(user_face_dir):
            for filename in os.listdir(user_face_dir):
                os.remove(os.path.join(user_face_dir, filename))
        
        # Remove from face data temporarily
        user_id = self.face_data[username]["user_id"]
        del self.face_data[username]
        
        # Capture new samples
        success, message = self.capture_face_samples(username, num_samples)
        
        if success:
            # Restore user_id
            self.face_data[username]["user_id"] = user_id
            self.save_face_data()
            return True, "Face updated successfully"
        else:
            return False, f"Failed to update face: {message}"
    
    def delete_face(self, username):
        """
        Delete face data for a user.
        
        Args:
            username: Username to delete
        
        Returns:
            Tuple (success, message)
        """
        if username not in self.face_data:
            return False, "User not found"
        
        # Delete face samples
        user_face_dir = os.path.join(self.faces_dir, username)
        if os.path.exists(user_face_dir):
            for filename in os.listdir(user_face_dir):
                os.remove(os.path.join(user_face_dir, filename))
            os.rmdir(user_face_dir)
        
        # Remove from face data
        del self.face_data[username]
        self.save_face_data()
        
        # Retrain recognizer
        if self.face_data:
            self.train_recognizer()
        
        return True, f"Face data deleted for {username}"
    
    def list_registered_faces(self):
        """List all registered faces."""
        return list(self.face_data.keys())


# ============================================================================
# TESTING AND INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    """Interactive menu for testing face authentication."""
    face_auth = FaceAuthSystem()
    
    while True:
        print("\n" + "="*60)
        print("FACE AUTHENTICATION SYSTEM")
        print("="*60)
        print("1. Register New Face")
        print("2. Recognize Face (Login)")
        print("3. Update Existing Face")
        print("4. Delete Face")
        print("5. List Registered Faces")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == "1":
            username = input("\nEnter username: ").strip()
            if not username:
                print("❌ Username cannot be empty")
                continue
            
            num_samples = input("Number of samples to capture (default 30): ").strip()
            num_samples = int(num_samples) if num_samples.isdigit() else 30
            
            success, message = face_auth.capture_face_samples(username, num_samples)
            if success:
                print(f"✓ {message}")
            else:
                print(f"❌ {message}")
        
        elif choice == "2":
            success, result = face_auth.recognize_face()
            if success:
                print(f"\n✓ Welcome back, {result}!")
            else:
                print(f"\n❌ {result}")
        
        elif choice == "3":
            registered = face_auth.list_registered_faces()
            if not registered:
                print("\n❌ No faces registered yet")
                continue
            
            print("\nRegistered users:")
            for i, user in enumerate(registered, 1):
                print(f"{i}. {user}")
            
            username = input("\nEnter username to update: ").strip()
            if username not in registered:
                print(f"❌ User '{username}' not found")
                continue
            
            num_samples = input("Number of samples to capture (default 30): ").strip()
            num_samples = int(num_samples) if num_samples.isdigit() else 30
            
            success, message = face_auth.update_face(username, num_samples)
            if success:
                print(f"✓ {message}")
            else:
                print(f"❌ {message}")
        
        elif choice == "4":
            registered = face_auth.list_registered_faces()
            if not registered:
                print("\n❌ No faces registered yet")
                continue
            
            print("\nRegistered users:")
            for i, user in enumerate(registered, 1):
                print(f"{i}. {user}")
            
            username = input("\nEnter username to delete: ").strip()
            if username not in registered:
                print(f"❌ User '{username}' not found")
                continue
            
            confirm = input(f"Are you sure you want to delete face data for '{username}'? (yes/no): ").lower()
            if confirm == "yes":
                success, message = face_auth.delete_face(username)
                if success:
                    print(f"✓ {message}")
                else:
                    print(f"❌ {message}")
            else:
                print("Deletion cancelled")
        
        elif choice == "5":
            registered = face_auth.list_registered_faces()
            if not registered:
                print("\n❌ No faces registered yet")
            else:
                print("\n📋 Registered Faces:")
                print("="*60)
                for i, username in enumerate(registered, 1):
                    data = face_auth.face_data[username]
                    print(f"{i}. {username}")
                    print(f"   User ID: {data['user_id']}")
                    print(f"   Samples: {data['num_samples']}")
                    print(f"   Registered: {data['registered_date']}")
                    print()
        
        elif choice == "6":
            print("\nGoodbye! 👋")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")


def main():
    """Main function to run the face authentication system."""
    print("="*60)
    print("FACE AUTHENTICATION SYSTEM")
    print("Using OpenCV + LBPH Face Recognizer")
    print("="*60)
    
    interactive_mode()


if __name__ == "__main__":
    main()