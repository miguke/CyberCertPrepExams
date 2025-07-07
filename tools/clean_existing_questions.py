import os
import json
import re

# --- CONFIGURATION ---
# Define the root directory for the data files. The script will scan subdirectories.
DATA_ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Define the regex patterns to identify and remove promotional text.
# These are designed to be broad enough to catch variations.
SPAM_PATTERNS = [
    # Matches phrases like '...2PassEasy.com...'
    re.compile(r'.*2passeasy\.com.*', re.IGNORECASE),
    # Matches phrases like '...surepassexam.com...'
    re.compile(r'.*surepassexam\.com.*', re.IGNORECASE),
    # Matches phrases like '...certleader.com...'
    re.compile(r'.*certleader\.com.*', re.IGNORECASE),
    # A more generic pattern for common spam phrases
    re.compile(r'Passing Certification Exams Made Easy.*|Welcome to download the Newest.*|Get the Full.*dumps in VCE and PDF.*', re.IGNORECASE),
    # Catches the specific 'The Leader of IT Certification visit' line
    re.compile(r'The Leader of IT Certification visit.*', re.IGNORECASE)
]

def clean_text(text):
    """Applies all spam patterns to a single string."""
    if not isinstance(text, str):
        return text
    cleaned_text = text
    for pattern in SPAM_PATTERNS:
        cleaned_text = pattern.sub('', cleaned_text)
    # Remove resulting blank lines and excess whitespace
    cleaned_text = '\n'.join(line for line in cleaned_text.splitlines() if line.strip())
    return cleaned_text.strip()

def clean_question_file(filepath):
    """Loads a JSON file, cleans its questions, and overwrites it if changes were made."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERROR: Could not read or parse {filepath}. Skipping. Error: {e}")
        return 0

    questions_cleaned = 0
    made_changes = False

    for q in questions:
        original_q_text = q.get('question', '')
        original_expl_text = q.get('explanation', '')
        original_options = q.get('options', [])

        # Clean the main question text and explanation
        q['question'] = clean_text(original_q_text)
        q['explanation'] = clean_text(original_expl_text)
        
        # Clean each option
        cleaned_options = [clean_text(opt) for opt in original_options]
        q['options'] = cleaned_options

        # Check if any text was actually changed
        if (
            q['question'] != original_q_text or
            q['explanation'] != original_expl_text or
            any(cleaned_options[i] != original_options[i] for i in range(len(original_options)))
        ):
            questions_cleaned += 1
            made_changes = True

    if made_changes:
        print(f"Found and cleaned {questions_cleaned} question(s) in {os.path.basename(filepath)}.")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"ERROR: Could not write cleaned file to {filepath}. Error: {e}")
            return 0
    
    return questions_cleaned

def main():
    """Main function to find and clean all question JSON files."""
    print(f"--- Starting Cleanup of Existing Question Files ---")
    print(f"Scanning for JSON files in: {DATA_ROOT_DIR}")
    
    total_cleaned_count = 0
    total_files_processed = 0

    for root, _, files in os.walk(DATA_ROOT_DIR):
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(root, filename)
                total_files_processed += 1
                total_cleaned_count += clean_question_file(filepath)
    
    print(f"\n--- Cleanup Summary ---")
    print(f"Processed {total_files_processed} JSON files.")
    print(f"Total questions cleaned: {total_cleaned_count}")
    if total_cleaned_count == 0:
        print("No promotional text found in any files.")
    else:
        print("Cleanup complete.")

if __name__ == '__main__':
    main()
