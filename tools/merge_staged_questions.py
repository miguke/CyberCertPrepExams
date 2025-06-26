import os
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
