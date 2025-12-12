import string
from collections import Counter

# ============================================================================
# LANGUAGE DETECTION & FREQUENCY ANALYSIS
# ============================================================================

# English letter frequency (from most to least common)
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
}

# French letter frequency
FRENCH_FREQ = {
    'E': 14.72, 'A': 7.64, 'I': 7.46, 'S': 7.95, 'N': 7.10,
    'R': 6.55, 'T': 7.24, 'O': 5.80, 'L': 5.46, 'U': 6.31,
    'D': 3.67, 'C': 3.26, 'M': 2.97, 'P': 3.02, 'G': 0.97,
    'B': 0.90, 'V': 1.63, 'H': 0.74, 'F': 1.06, 'Q': 1.36,
    'Y': 0.31, 'X': 0.39, 'J': 0.45, 'K': 0.05, 'W': 0.04, 'Z': 0.12
}

# Common English words for validation
ENGLISH_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
}

# Common French words
FRENCH_WORDS = {
    'le', 'de', 'un', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je',
    'son', 'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au',
    'pour', 'pas', 'que', 'vous', 'par', 'sur', 'faire', 'plus', 'dire', 'me',
    'on', 'mon', 'lui', 'nous', 'comme', 'mais', 'pouvoir', 'avec', 'tout', 'y',
    'aller', 'voir', 'en', 'sans', 'bien', 'où', 'notre', 'leur', 'dont', 'autre'
}


def calculate_frequency_score(text, language='english'):
    """
    Calculate how well the text matches expected letter frequency.
    Lower score = better match.
    
    Args:
        text: Text to analyze
        language: 'english' or 'french'
    
    Returns:
        Frequency score (lower is better)
    """
    # Choose frequency table
    freq_table = ENGLISH_FREQ if language == 'english' else FRENCH_FREQ
    
    # Count letters in text
    text_upper = text.upper()
    letter_count = Counter(char for char in text_upper if char.isalpha())
    
    # Calculate total letters
    total_letters = sum(letter_count.values())
    if total_letters == 0:
        return float('inf')
    
    # Calculate chi-squared statistic
    chi_squared = 0
    for letter in string.ascii_uppercase:
        expected_freq = freq_table.get(letter, 0) / 100 * total_letters
        observed_freq = letter_count.get(letter, 0)
        
        if expected_freq > 0:
            chi_squared += ((observed_freq - expected_freq) ** 2) / expected_freq
    
    return chi_squared


def count_dictionary_words(text, language='english'):
    """
    Count how many common words appear in the text.
    
    Args:
        text: Text to analyze
        language: 'english' or 'french'
    
    Returns:
        Number of dictionary words found
    """
    word_set = ENGLISH_WORDS if language == 'english' else FRENCH_WORDS
    
    # Split text into words and convert to lowercase
    words = text.lower().split()
    
    # Count matches
    matches = sum(1 for word in words if word in word_set)
    
    return matches


def detect_language(text):
    """
    Detect if text is more likely English or French.
    
    Args:
        text: Text to analyze
    
    Returns:
        'english' or 'french'
    """
    english_score = calculate_frequency_score(text, 'english')
    french_score = calculate_frequency_score(text, 'french')
    
    return 'english' if english_score < french_score else 'french'


# ============================================================================
# CAESAR CIPHER FUNCTIONS
# ============================================================================

def caesar_decrypt_with_shift(text, shift):
    """
    Decrypt Caesar cipher with a specific shift.
    
    Args:
        text: Encrypted text
        shift: Shift amount
    
    Returns:
        Decrypted text
    """
    result = ""
    
    for char in text:
        if char.isupper():
            result += chr((ord(char) - shift - 65) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) - shift - 97) % 26 + 97)
        else:
            result += char
    
    return result


# ============================================================================
# AUTOMATIC BREAKING METHODS
# ============================================================================

def break_caesar_frequency(encrypted_text, language='english'):
    """
    Break Caesar cipher using frequency analysis.
    
    Args:
        encrypted_text: The encrypted message
        language: 'english' or 'french'
    
    Returns:
        Tuple (decrypted_text, shift, confidence_score)
    """
    print(f"\n{'='*60}")
    print(f"BREAKING CAESAR CIPHER - FREQUENCY ANALYSIS ({language.upper()})")
    print(f"{'='*60}")
    print(f"\nEncrypted text: {encrypted_text}")
    print(f"\nTrying all 26 possible shifts...\n")
    
    best_shift = 0
    best_score = float('inf')
    best_decryption = ""
    
    results = []
    
    # Try all 26 possible shifts
    for shift in range(26):
        decrypted = caesar_decrypt_with_shift(encrypted_text, shift)
        
        # Calculate frequency score
        freq_score = calculate_frequency_score(decrypted, language)
        
        # Count dictionary words
        word_count = count_dictionary_words(decrypted, language)
        
        # Combined score (lower frequency score + more words = better)
        combined_score = freq_score - (word_count * 10)
        
        results.append({
            'shift': shift,
            'text': decrypted,
            'freq_score': freq_score,
            'word_count': word_count,
            'combined_score': combined_score
        })
        
        if combined_score < best_score:
            best_score = combined_score
            best_shift = shift
            best_decryption = decrypted
    
    # Display top 3 candidates
    print(f"{'Shift':<8} {'Words':<8} {'Freq Score':<15} {'Preview'}")
    print("-" * 60)
    
    sorted_results = sorted(results, key=lambda x: x['combined_score'])
    
    for i, result in enumerate(sorted_results[:3]):
        preview = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
        marker = "★" if i == 0 else " "
        print(f"{marker} {result['shift']:<7} {result['word_count']:<8} {result['freq_score']:<15.2f} {preview}")
    
    # Calculate confidence (percentage of dictionary words)
    words_in_best = best_decryption.split()
    confidence = (sorted_results[0]['word_count'] / len(words_in_best) * 100) if words_in_best else 0
    
    print(f"\n{'='*60}")
    print(f"RESULT")
    print(f"{'='*60}")
    print(f"Best shift: {best_shift}")
    print(f"Confidence: {confidence:.1f}%")
    print(f"Dictionary words found: {sorted_results[0]['word_count']}/{len(words_in_best)}")
    print(f"\nDecrypted message:\n{best_decryption}")
    
    return best_decryption, best_shift, confidence


def break_caesar_auto(encrypted_text):
    """
    Automatically break Caesar cipher with language detection.
    
    Args:
        encrypted_text: The encrypted message
    
    Returns:
        Tuple (decrypted_text, shift, confidence_score, language)
    """
    # First, try to detect language
    detected_language = detect_language(encrypted_text)
    
    print(f"\n{'='*60}")
    print(f"AUTOMATIC CAESAR CIPHER BREAKER")
    print(f"{'='*60}")
    print(f"Detected language: {detected_language.upper()}")
    
    # Break using detected language
    decrypted, shift, confidence = break_caesar_frequency(encrypted_text, detected_language)
    
    return decrypted, shift, confidence, detected_language


def break_caesar_brute_force(encrypted_text):
    """
    Show all 26 possible Caesar decryptions.
    
    Args:
        encrypted_text: The encrypted message
    
    Returns:
        List of all possible decryptions
    """
    print(f"\n{'='*60}")
    print(f"BRUTE FORCE - ALL 26 POSSIBILITIES")
    print(f"{'='*60}")
    print(f"\nEncrypted text: {encrypted_text}\n")
    
    results = []
    
    print(f"{'Shift':<8} {'Decrypted Text'}")
    print("-" * 60)
    
    for shift in range(26):
        decrypted = caesar_decrypt_with_shift(encrypted_text, shift)
        results.append((shift, decrypted))
        print(f"{shift:<8} {decrypted}")
    
    return results


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    """Interactive Caesar breaker."""
    
    while True:
        print("\n" + "="*60)
        print("CAESAR CIPHER BREAKER")
        print("="*60)
        print("1. Automatic Break (Frequency Analysis + Language Detection)")
        print("2. Break with Specific Language")
        print("3. Brute Force (Show All 26 Possibilities)")
        print("4. Test with Sample Messages")
        print("5. Exit")
        print("="*60)
        
        choice = input("\nChoose an option (1-5): ").strip()
        
        if choice == "1":
            encrypted = input("\nEnter encrypted message: ").strip()
            
            if encrypted:
                decrypted, shift, confidence, language = break_caesar_auto(encrypted)
                
                print(f"\n{'='*60}")
                print(f"FINAL RESULT")
                print(f"{'='*60}")
                print(f"Language: {language}")
                print(f"Shift used: {shift}")
                print(f"Confidence: {confidence:.1f}%")
                print(f"Decrypted: {decrypted}")
        
        elif choice == "2":
            encrypted = input("\nEnter encrypted message: ").strip()
            print("\nChoose language:")
            print("1. English")
            print("2. French")
            lang_choice = input("Enter choice (1-2): ").strip()
            
            language = 'english' if lang_choice == '1' else 'french'
            
            if encrypted:
                decrypted, shift, confidence = break_caesar_frequency(encrypted, language)
        
        elif choice == "3":
            encrypted = input("\nEnter encrypted message: ").strip()
            
            if encrypted:
                results = break_caesar_brute_force(encrypted)
                
                correct = input("\nWhich shift looks correct? (0-25): ").strip()
                if correct.isdigit() and 0 <= int(correct) <= 25:
                    print(f"\nYou selected shift {correct}:")
                    print(results[int(correct)][1])
        
        elif choice == "4":
            print("\n--- TESTING WITH SAMPLE MESSAGES ---")
            
            # Test samples
            samples = [
                ("KHOOR ZRUOG", 3, "English"),
                ("WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ", 3, "English"),
                ("JVYUPVU PZ AOL RLF", 7, "English")
            ]
            
            for encrypted, actual_shift, lang in samples:
                print(f"\n{'='*60}")
                print(f"Sample: {encrypted}")
                print(f"Actual shift: {actual_shift}")
                decrypted, found_shift, confidence, detected_lang = break_caesar_auto(encrypted)
                
                if found_shift == actual_shift:
                    print("✓ Correctly identified shift!")
                else:
                    print(f"✗ Incorrect. Found {found_shift}, actual is {actual_shift}")
        
        elif choice == "5":
            print("\nGoodbye! 🔓")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_caesar_breaker():
    """Test the Caesar breaker with known examples."""
    print("="*60)
    print("TESTING CAESAR BREAKER")
    print("="*60)
    
    # Test case 1: Simple English
    print("\n[TEST 1] Simple English Message")
    encrypted1 = "KHOOR ZRUOG"
    print(f"Encrypted: {encrypted1}")
    print(f"Expected shift: 3")
    
    decrypted1, shift1, conf1, lang1 = break_caesar_auto(encrypted1)
    print(f"✓ Success!" if shift1 == 3 else f"✗ Failed")
    
    # Test case 2: Longer English
    print("\n[TEST 2] Longer English Message")
    encrypted2 = "WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ"
    print(f"Encrypted: {encrypted2}")
    print(f"Expected: THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG")
    print(f"Expected shift: 3")
    
    decrypted2, shift2, conf2, lang2 = break_caesar_auto(encrypted2)
    print(f"✓ Success!" if shift2 == 3 else f"✗ Failed")
    
    # Test case 3: Different shift
    print("\n[TEST 3] Different Shift Value")
    encrypted3 = "JVYUPVU PZ AOL RLF"
    print(f"Encrypted: {encrypted3}")
    print(f"Expected: CRYPTION IS THE KEY")
    print(f"Expected shift: 7")
    
    decrypted3, shift3, conf3, lang3 = break_caesar_auto(encrypted3)
    print(f"✓ Success!" if shift3 == 7 else f"✗ Failed")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE!")
    print("="*60)


# ============================================================================
# MAIN PROGRAM
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("CAESAR CIPHER BREAKER")
    print("Automatic Decryption Without Knowing the Key!")
    print("="*60)
    
    # Uncomment to run tests
    # test_caesar_breaker()
    
    # Run interactive mode
    interactive_mode()