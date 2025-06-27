import json
import os
import re
import argparse

# Regex to strip 'NEW QUESTION n' prefixes
NEW_QUESTION_RE = re.compile(r'^NEW QUESTION \d+\s*', re.IGNORECASE)

# Configuration for each exam core
EXAM_CONFIGS = {
    '1101': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1101'),
        'topic_files': [
            "hardware.json", "mobile-devices.json", "networking.json",
            "troubleshooting.json", "virtualization-cloud.json", "miscellaneous.json"
        ],
        'staging_file': 'new_questions_staging.json'
    },
    '1102': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1102'),
        'topic_files': [
            "operating-systems.json", "security.json",
            "software-troubleshooting.json", "operational-procedures.json", "miscellaneous.json"
        ],
        'staging_file': 'new_questions_staging.json'
    }
}

def get_question_signature(question_obj):
    """Creates a unique, normalized signature for a question for deduplication."""
    question_text = question_obj.get("question", "")
    # Strip common spam phrases and normalize text
    spam_phrases = [
        'The Leader of IT Certification visit - https://www.certleader.com',
        '100% Valid and Newest Version 220-1102 Questions & Answers shared by Certleader',
        'https://www.certleader.com/220-1102-dumps.html (402 Q&As)'
    ]
    for phrase in spam_phrases:
        question_text = question_text.replace(phrase, '')
    
    question_text = NEW_QUESTION_RE.sub('', question_text).strip().casefold()
    
    options = sorted([str(opt).strip().casefold() for opt in question_obj.get("options", [])])
    return f"{question_text}|{'|'.join(options)}"

def main():
    parser = argparse.ArgumentParser(description='Verify staging questions against existing topic files for duplicates.')
    parser.add_argument('exam', choices=['1101', '1102'], nargs='?', default='1101', help='The exam core to check (1101 or 1102). Defaults to 1101.')
    args = parser.parse_args()

    config = EXAM_CONFIGS[args.exam]
    data_dir = config['data_dir']
    
    print(f"--- Checking for Duplicates in Staging File for Exam {args.exam} ---")

    # 1. Load signatures from all main topic files
    existing_signatures = set()
    for filename in config['topic_files']:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    questions = json.loads(content) if content.strip() else []
                    for q in questions:
                        existing_signatures.add(get_question_signature(q))
            except json.JSONDecodeError:
                print(f"Warning: Could not decode {filename}. Skipping for duplicate check.")

    print(f"Loaded {len(existing_signatures)} unique signatures from main topic files.")

    # 2. Load the staging file
    staging_filepath = os.path.join(data_dir, config['staging_file'])
    if not os.path.exists(staging_filepath):
        print(f"Staging file not found: {staging_filepath}")
        return

    try:
        with open(staging_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            staging_questions = json.loads(content) if content.strip() else []
    except json.JSONDecodeError:
        print(f"Error: Could not decode staging file {staging_filepath}.")
        return

    if not staging_questions:
        print("Staging file is empty. No duplicates to check.")
        return

    # 3. Check for duplicates
    duplicate_indices = []
    for i, q in enumerate(staging_questions):
        if get_question_signature(q) in existing_signatures:
            duplicate_indices.append(i)

    if duplicate_indices:
        print(f"\nFound {len(duplicate_indices)} DUPLICATE(S) in the staging file.")
        print("Indices of duplicate questions in 'new_questions_staging.json':", duplicate_indices)
        print("These questions should be removed from the staging file before merging.")
    else:
        print("\nSuccess: No duplicates found in the staging file.")

if __name__ == '__main__':
    main()
