import json
import os

# --- CONFIGURATION ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1102')
CLEANUP_CHAR = '❍'

def clean_string(text):
    """Removes the specified character from a string."""
    return text.replace(CLEANUP_CHAR, '').strip()

def main():
    """Main function to clean up special characters from all topic files."""
    print(f"--- Starting Cleanup Process for Core 2 ({DATA_DIR}) ---")

    if not os.path.exists(DATA_DIR):
        print(f"ERROR: Data directory not found at {DATA_DIR}")
        return

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            print(f"Processing {filename}...")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        print(f"  - Skipping empty file.")
                        continue
                    questions = json.loads(content)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  - ERROR: Could not read or parse file. Error: {e}")
                continue

            if not isinstance(questions, list):
                print(f"  - ERROR: Expected a list of questions, but found {type(questions)}. Skipping.")
                continue

            # Clean each question and its options
            for question in questions:
                if 'question' in question and isinstance(question['question'], str):
                    question['question'] = clean_string(question['question'])
                if 'options' in question and isinstance(question['options'], list):
                    question['options'] = [clean_string(opt) for opt in question['options']]
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, indent=2, ensure_ascii=False)
                print(f"  - Successfully cleaned {len(questions)} questions.")
            except IOError as e:
                print(f"  - ERROR: Could not write to file. Error: {e}")

    print(f"\n--- Cleanup Complete ---")

if __name__ == '__main__':
    main()
