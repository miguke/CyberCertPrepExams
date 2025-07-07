import json
import os

# --- CONFIGURATION ---
STAGING_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'new_questions_staging_v3_mapped.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1101')

# Mapping from the first digit of 'topic_id_from_pdf' to the topic filename
TOPIC_MAPPING = {
    '1': 'mobile-devices.json',
    '2': 'networking.json',
    '3': 'hardware.json',
    '4': 'virtualization-cloud.json',
    '5': 'troubleshooting.json',
}

def load_json_file(filepath, default=[]):
    """Safely loads a JSON file, returning a default value if it doesn't exist or is invalid."""
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read or parse {filepath}. Error: {e}. Starting with an empty list.")
        return default

def write_json_file(filepath, data):
    """Writes data to a JSON file with pretty printing."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def resequence_ids(questions):
    """Resequences the 'id' field for a list of questions, starting from 1."""
    for i, question in enumerate(questions):
        question['id'] = i + 1
    return questions

def main():
    """Main function to merge staged questions into their respective topic files."""
    staged_questions = load_json_file(STAGING_FILE)
    if not staged_questions:
        print(f"No new questions found in {STAGING_FILE}. Nothing to do.")
        return

    # Group new questions by their target topic file
    questions_by_topic_file = {filename: [] for filename in TOPIC_MAPPING.values()}

    for q in staged_questions:
        topic_id_prefix = q.get('topic_id_from_pdf', '').split('.')[0]
        target_file = TOPIC_MAPPING.get(topic_id_prefix)

        if target_file:
            # Clean up the question object before appending
            q.pop('topic_id_from_pdf', None)
            q.pop('topic_id_from_pdf_and_question', None)
            q.pop('source_pdf', None)
            questions_by_topic_file[target_file].append(q)
        else:
            print(f"Warning: No mapping found for topic_id '{q.get('topic_id_from_pdf')}'. Skipping question.")

    # Process each topic file
    for filename, new_questions in questions_by_topic_file.items():
        if not new_questions:
            continue

        filepath = os.path.join(DATA_DIR, filename)
        existing_questions = load_json_file(filepath)
        
        print(f"Merging {len(new_questions)} new questions into {filename}...")
        
        # Append new questions and re-sequence all IDs
        combined_questions = existing_questions + new_questions
        final_questions = resequence_ids(combined_questions)
        
        write_json_file(filepath, final_questions)
        print(f"Successfully updated {filename}. Total questions: {len(final_questions)}")

    print("\nMerge process complete.")

if __name__ == '__main__':
    main()
