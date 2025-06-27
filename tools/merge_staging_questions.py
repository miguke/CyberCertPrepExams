import json
import os
import argparse

EXAM_CONFIGS = {
    '1101': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1101'),
        'staging_file': os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'new_questions_staging.json'),
        'topic_files': {
            "hardware": "hardware.json",
            "mobile-devices": "mobile-devices.json",
            "networking": "networking.json",
            "troubleshooting": "troubleshooting.json",
            "virtualization-cloud": "virtualization-cloud.json",
            "miscellaneous": "miscellaneous.json",
        }
    },
    '1102': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1102'),
        'staging_file': os.path.join(os.path.dirname(__file__), '..', 'data', '1102', 'new_questions_staging.json'),
        'topic_files': {
            "operating-systems": "operating-systems.json",
            "security": "security.json",
            "software-troubleshooting": "software-troubleshooting.json",
            "operational-procedures": "operational-procedures.json",
            "miscellaneous": "miscellaneous.json",
        }
    }
}

def load_json_file(file_path):
    """Loads a single JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content) if content.strip() else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: File {file_path} is not valid JSON.")
        return []

def save_json_file(file_path, data):
    """Saves data to a single JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main(args):
    config = EXAM_CONFIGS[args.exam]
    data_dir = config['data_dir']
    staging_file = config['staging_file']
    topic_files = config['topic_files']

    print(f"--- Merging Staging Questions for Exam {args.exam} ---")

    staging_questions = load_json_file(staging_file)

    if not staging_questions:
        print("Staging file is empty or not found. No questions to merge.")
        return

    print(f"Found {len(staging_questions)} questions to merge.")

    for topic_key, filename in topic_files.items():
        filepath = os.path.join(data_dir, filename)
        topic_questions = load_json_file(filepath)
        
        # Add questions from staging that belong to this topic
        questions_to_add = [q for q in staging_questions if q.get('topic') == topic_key]
        
        if questions_to_add:
            topic_questions.extend(questions_to_add)
            save_json_file(filepath, topic_questions)
            print(f"Merged {len(questions_to_add)} questions into {filename}")

    # Clear the staging file after merging
    save_json_file(staging_file, [])
    print(f"Staging file '{staging_file}' has been cleared.")

    print("\nMerge complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge questions from a staging file into the main topic files.')
    parser.add_argument('exam', choices=['1101', '1102'], help='The exam core to process.')
    args = parser.parse_args()
    main(args)
