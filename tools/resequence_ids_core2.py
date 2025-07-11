import json
import os

# --- CONFIGURATION ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1102')

def resequence_ids(questions):
    """Resequences the 'id' field for a list of questions, starting from 1."""
    for i, question in enumerate(questions):
        question['id'] = i + 1
    return questions

def main():
    """Main function to re-sequence question IDs in all topic files."""
    print(f"--- Starting ID Resequencing for Core 2 ({DATA_DIR}) ---")

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

            updated_questions = resequence_ids(questions)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(updated_questions, f, indent=2, ensure_ascii=False)
                print(f"  - Successfully re-sequenced {len(updated_questions)} questions.")
            except IOError as e:
                print(f"  - ERROR: Could not write to file. Error: {e}")

    print("\n--- ID Resequencing Complete ---")

if __name__ == '__main__':
    main()
