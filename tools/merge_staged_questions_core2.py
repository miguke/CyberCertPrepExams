import os
import json
import collections

# --- CONFIGURATION ---
STAGING_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1102', 'new_questions_staging_messer.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1102')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

def backup_file(filepath):
    """Creates a backup of a file."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(filepath) + '.bak')
    print(f"Backing up {filepath} to {backup_path}...")
    with open(filepath, 'r', encoding='utf-8') as f_in, open(backup_path, 'w', encoding='utf-8') as f_out:
        f_out.write(f_in.read())

def main():
    """Merges staged questions into their respective topic files."""
    print("--- Starting Core 2 Question Merge Process ---")

    if not os.path.exists(STAGING_FILE):
        print(f"ERROR: Staging file not found at {STAGING_FILE}")
        return

    try:
        with open(STAGING_FILE, 'r', encoding='utf-8') as f:
            staged_questions = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERROR: Could not read or parse staging file. Error: {e}")
        return

    print(f"Loaded {len(staged_questions)} questions from staging file.")

    # Group questions by their target topic file
    questions_by_topic = collections.defaultdict(list)
    for q in staged_questions:
        topic = q.get('topic')
        if not topic:
            print(f"Warning: Question found with no topic. Skipping. Question text: {q.get('question', 'N/A')[:50]}...")
            continue
        
        # Clean up the question object before appending
        q.pop('topic', None)
        
        target_filename = f"{topic}.json"
        questions_by_topic[target_filename].append(q)

    # Merge questions into each topic file
    merge_summary = collections.defaultdict(int)
    for filename, new_questions in questions_by_topic.items():
        filepath = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: Topic file {filename} not found. Creating a new one.")
            existing_questions = []
        else:
            backup_file(filepath)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    existing_questions = json.loads(content) if content.strip() else []
            except (json.JSONDecodeError, IOError) as e:
                print(f"ERROR: Could not read or parse {filename}. Skipping merge for this file. Error: {e}")
                continue

        existing_questions.extend(new_questions)
        merge_summary[filename] = len(new_questions)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_questions, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"ERROR: Could not write to {filename}. Error: {e}")

    print("\n--- Merge Complete ---")
    if not merge_summary:
        print("No questions were merged.")
    else:
        print("Summary of merged questions:")
        for filename, count in merge_summary.items():
            print(f"  - Added {count} questions to {filename}")
            
    print(f"\nNext step: Run a script to re-sequence all question IDs.")

if __name__ == '__main__':
    main()
