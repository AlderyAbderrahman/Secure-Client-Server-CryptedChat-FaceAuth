#!/usr/bin/env python3
"""
Test script for Face Authentication System
"""

from face_auth import FaceAuthSystem

def test_system():
    """Test the face authentication system with a demo."""
    print("\n" + "="*60)
    print("FACE AUTHENTICATION SYSTEM - TEST MODE")
    print("="*60)
    
    # Initialize system
    face_auth = FaceAuthSystem()
    
    print("\nThis test will:")
    print("1. Register a new face")
    print("2. Try to recognize that face")
    print("3. Show registered faces")
    
    input("\nPress Enter to continue...")
    
    # Test 1: Register a face
    print("\n" + "="*60)
    print("TEST 1: REGISTERING A FACE")
    print("="*60)
    
    username = input("Enter a username to register: ").strip()
    if not username:
        print("❌ Username cannot be empty. Test cancelled.")
        return
    
    print(f"\nRegistering face for '{username}'...")
    print("The camera will open. Position your face clearly.")
    
    success, message = face_auth.capture_face_samples(username, num_samples=20)
    
    if success:
        print(f"\n✓ TEST 1 PASSED: {message}")
    else:
        print(f"\n❌ TEST 1 FAILED: {message}")
        return
    
    input("\nPress Enter to continue to face recognition test...")
    
    # Test 2: Recognize the face
    print("\n" + "="*60)
    print("TEST 2: RECOGNIZING YOUR FACE")
    print("="*60)
    print("The camera will open again. Let's see if it recognizes you!")
    
    success, result = face_auth.recognize_face(confidence_threshold=70)
    
    if success:
        if result == username:
            print(f"\n✓ TEST 2 PASSED: Successfully recognized as '{result}'")
        else:
            print(f"\n⚠️  TEST 2 WARNING: Recognized as '{result}' instead of '{username}'")
    else:
        print(f"\n❌ TEST 2 FAILED: {result}")
    
    # Test 3: List registered faces
    print("\n" + "="*60)
    print("TEST 3: LISTING REGISTERED FACES")
    print("="*60)
    
    registered = face_auth.list_registered_faces()
    
    if registered:
        print(f"\n✓ Found {len(registered)} registered face(s):")
        for i, user in enumerate(registered, 1):
            data = face_auth.face_data[user]
            print(f"\n{i}. Username: {user}")
            print(f"   User ID: {data['user_id']}")
            print(f"   Samples: {data['num_samples']}")
            print(f"   Registered: {data['registered_date']}")
    else:
        print("\n❌ No registered faces found")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
    
    # Ask if user wants to delete test data
    delete = input("\nDo you want to delete the test face data? (yes/no): ").lower()
    if delete == "yes":
        success, message = face_auth.delete_face(username)
        if success:
            print(f"✓ {message}")
        else:
            print(f"❌ {message}")


def main():
    """Main function."""
    print("="*60)
    print("FACE AUTHENTICATION SYSTEM - TESTING")
    print("="*60)
    print("\nThis script will test the face authentication features:")
    print("- Face registration")
    print("- Face recognition")
    print("- Database management")
    print("\nMake sure:")
    print("✓ Your camera is connected")
    print("✓ You're in a well-lit area")
    print("✓ opencv-contrib-python is installed")
    print("="*60)
    
    ready = input("\nAre you ready to start? (yes/no): ").lower()
    
    if ready == "yes":
        try:
            test_system()
        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            print("\nMake sure opencv-contrib-python is installed:")
            print("  pip install opencv-contrib-python")
    else:
        print("\nTest cancelled. Run this script again when ready!")


if __name__ == "__main__":
    main()