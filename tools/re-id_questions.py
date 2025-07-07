import os
import json

# --- CONFIGURATION ---
# Specify the directory containing the JSON files you want to re-ID.
# Options: 'data/1101', 'data/1102'
TARGET_DIRECTORY = 'data/1102'

# --- SCRIPT LOGIC ---

def get_all_json_files(directory_path):
    """Finds all .json files in the specified directory."""
    json_files = []
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith('.json'):
            json_files.append(os.path.join(directory_path, filename))
    return json_files

def re_id_questions_in_files(file_paths):
    """Loads all questions from a list of files, re-assigns sequential IDs, and saves them back."""
    all_questions_by_file = {}
    total_questions = 0

    # 1. Load all questions from all files into a dictionary
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                all_questions_by_file[path] = questions
                total_questions += len(questions)
        except (json.JSONDecodeError, IOError) as e:
            print(f"ERROR: Could not read or parse {path}. Skipping. Error: {e}")
            continue
    
    print(f"Found {total_questions} questions across {len(file_paths)} files.")

    # 2. Assign new, sequential IDs across all loaded questions
    current_id = 1
    for path in file_paths: # Iterate in the same sorted order
        if path in all_questions_by_file:
            for question in all_questions_by_file[path]:
                question['id'] = current_id
                current_id += 1

    # 3. Write the updated questions back to their original files
    changes_made = 0
    for path, questions in all_questions_by_file.items():
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            print(f"Successfully updated IDs in: {os.path.basename(path)}")
            changes_made += 1
        except IOError as e:
            print(f"ERROR: Could not write updated file to {path}. Error: {e}")

    return changes_made

def main():
    """Main function to run the re-ID process."""
    print(f"--- Starting Question Re-ID Process ---")
    base_path = os.path.join(os.path.dirname(__file__), '..')
    target_path = os.path.join(base_path, TARGET_DIRECTORY.replace('/', os.sep))

    if not os.path.isdir(target_path):
        print(f"ERROR: Target directory not found at {target_path}")
        return

    print(f"Scanning for JSON files in: {target_path}")
    json_files = get_all_json_files(target_path)

    if not json_files:
        print("No JSON files found to process.")
        return

    files_updated = re_id_questions_in_files(json_files)

    print(f"\n--- Re-ID Summary ---")
    print(f"Process complete. Updated {files_updated} file(s).")

if __name__ == '__main__':
    main()
