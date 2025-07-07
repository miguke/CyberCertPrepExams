import os
import json
import collections

# --- CONFIGURATION ---
STAGING_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'new_questions_staging_v3_mapped.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1101')
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
    print("--- Starting Question Merge Process ---")

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
        q.pop('topic_id_from_pdf', None)
        
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
import json
import shutil

# Paths
TOOLS_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(TOOLS_DIR, '..', 'data', '1101'))
STAGING_FILE = os.path.abspath(os.path.join(TOOLS_DIR, '..', 'data', '1101', 'new_questions_staging.json'))
BACKUP_DIR = os.path.join(TOOLS_DIR, 'backup_before_merge')

# Topic to filename mapping (edit if new topics are added)
TOPIC_FILES = {
    'hardware': 'hardware.json',
    'networking': 'networking.json',
    'mobile-devices': 'mobile-devices.json',
    'troubleshooting': 'troubleshooting.json',
    'virtualization-cloud': 'virtualization-cloud.json',
    'miscellaneous': 'miscellaneous.json',
}

def backup_file(filepath):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    filename = os.path.basename(filepath)
    backup_path = os.path.join(BACKUP_DIR, filename)
    shutil.copy2(filepath, backup_path)
    print(f"Backed up {filename} to {backup_path}")

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_id(questions):
    ids = [q.get('id', -1) for q in questions if isinstance(q.get('id', -1), int) and q['id'] > 0]
    return max(ids, default=0) + 1

def main():
    if not os.path.exists(STAGING_FILE):
        print(f"No staging file found at {STAGING_FILE}. Exiting.")
        return
    
    staged_questions = load_json(STAGING_FILE)
    if not staged_questions:
        print("No questions in staging file. Nothing to merge.")
        return
    
    # Group questions by topic
    topic_to_questions = {k: [] for k in TOPIC_FILES}
    for q in staged_questions:
        topic = q.get('topic', 'miscellaneous')
        if topic not in TOPIC_FILES:
            print(f"Unknown topic '{topic}' in question: {q.get('question', '')[:40]}... Assigning to 'miscellaneous'.")
            topic = 'miscellaneous'
        topic_to_questions[topic].append(q)

    summary = []
    for topic, questions in topic_to_questions.items():
        if not questions:
            continue
        topic_file = os.path.join(DATA_DIR, TOPIC_FILES[topic])
        existing = load_json(topic_file)
        backup_file(topic_file)
        next_id = get_next_id(existing)
        for q in questions:
            q['id'] = next_id
            next_id += 1
            # Remove any temp fields if present
            q.pop('source_pdf', None)
        existing.extend(questions)
        save_json(topic_file, existing)
        summary.append(f"Merged {len(questions)} questions into {TOPIC_FILES[topic]}")
    
    # Archive the staging file
    archive_path = STAGING_FILE + '.archived'
    shutil.move(STAGING_FILE, archive_path)
    print("\n".join(summary))
    print(f"Staging file archived as {archive_path}")

if __name__ == '__main__':
    main()
