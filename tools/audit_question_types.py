import json
import os

# --- CONFIGURATION ---
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CORE_DIRS = ['1101', '1102']

def audit_and_fix_file(filepath):
    """Audits a single JSON file and corrects question types."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return 0 # Skip empty files
            questions = json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  - ERROR: Could not read or parse file. Error: {e}")
        return 0

    if not isinstance(questions, list):
        print(f"  - ERROR: Expected a list of questions, but found {type(questions)}. Skipping.")
        return 0

    fixes_made = 0
    for q in questions:
        correct_answers_count = len(q.get('correct', []))
        current_type = q.get('type')
        correct_type = 'multiple' if correct_answers_count > 1 else 'single'

        if current_type != correct_type:
            q['type'] = correct_type
            fixes_made += 1

    if fixes_made > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            print(f"  - Corrected {fixes_made} question type(s).")
        except IOError as e:
            print(f"  - ERROR: Could not write changes to file. Error: {e}")
            return 0
            
    return fixes_made

def main():
    """Main function to audit and fix question types across all specified core directories."""
    print("--- Starting Audit of Question Types (Single/Multiple) ---")
    total_fixes = 0

    for core_dir_name in CORE_DIRS:
        data_dir = os.path.join(BASE_DATA_DIR, core_dir_name)
        if not os.path.exists(data_dir):
            print(f"\nWarning: Directory not found, skipping: {data_dir}")
            continue

        print(f"\nProcessing directory: {data_dir}")
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                print(f"- Auditing {filename}...")
                total_fixes += audit_and_fix_file(filepath)

    print("\n--- Audit Complete ---")
    if total_fixes == 0:
        print("No issues found. All question types are correct.")
    else:
        print(f"Total questions fixed: {total_fixes}")

if __name__ == '__main__':
    main()
