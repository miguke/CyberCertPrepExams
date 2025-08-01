import json
import os
import glob
import argparse
from collections import defaultdict

# This map defines which topics should be merged into others.
# 'source_topic': 'destination_topic'
TOPIC_CONSOLIDATION_MAP = {
    'threats': 'threats-vulnerabilities-mitigations',
    'security-program-management': 'security-program-management-oversight'
}

def get_topic_files(directory):
    """Gets all topic JSON files, excluding specific files like staging or results."""
    pattern = os.path.join(directory, '*.json')
    all_files = glob.glob(pattern)
    excluded_keywords = ['staging', 'results', 'cleaned']
    return [f for f in all_files if not any(keyword in os.path.basename(f) for keyword in excluded_keywords)]

def consolidate_and_resequence(topics_directory):
    """Consolidates questions from incorrect topic files into correct ones and resequences all IDs."""
    print("--- Starting Topic Consolidation ---")

    # 1. Merge incorrect topic files into correct ones
    for source_topic, dest_topic in TOPIC_CONSOLIDATION_MAP.items():
        source_filepath = os.path.join(topics_directory, f"{source_topic}.json")
        dest_filepath = os.path.join(topics_directory, f"{dest_topic}.json")

        if not os.path.exists(source_filepath):
            print(f"Source file {os.path.basename(source_filepath)} not found. Skipping.")
            continue
        
        if not os.path.exists(dest_filepath):
            print(f"Destination file {os.path.basename(dest_filepath)} not found. Cannot merge. Skipping.")
            continue

        try:
            with open(source_filepath, 'r', encoding='utf-8') as f:
                source_questions = json.load(f)
            with open(dest_filepath, 'r', encoding='utf-8') as f:
                dest_questions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON files: {e}. Skipping merge for {source_topic}.")
            continue

        print(f"Merging {len(source_questions)} questions from '{source_topic}.json' into '{dest_topic}.json'...")
        dest_questions.extend(source_questions)

        with open(dest_filepath, 'w', encoding='utf-8') as f:
            json.dump(dest_questions, f, indent=2, ensure_ascii=False)
        
        # Remove the now-empty source file
        os.remove(source_filepath)
        print(f"Successfully merged and removed '{source_topic}.json'.")

    # 2. Resequence all question IDs across all remaining topic files
    print("\n--- Starting Final ID Resequencing ---")
    all_questions_by_topic = defaultdict(list)
    current_id = 1

    topic_files = get_topic_files(topics_directory)
    for file_path in sorted(topic_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                topic_name = os.path.splitext(os.path.basename(file_path))[0]
                all_questions_by_topic[topic_name].extend(questions)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not process {file_path} for re-sequencing: {e}")
            continue

    # Re-assign IDs and write back to files
    for topic_name in sorted(all_questions_by_topic.keys()):
        questions = all_questions_by_topic[topic_name]
        for question in questions:
            question['id'] = current_id
            current_id += 1
        
        topic_filepath = os.path.join(topics_directory, f"{topic_name}.json")
        with open(topic_filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        print(f"Resequenced {len(questions)} questions in {os.path.basename(topic_filepath)}.")

    print(f"\nCorrection complete. Total questions: {current_id - 1}")

def main():
    parser = argparse.ArgumentParser(description='Consolidate topic files and resequence all question IDs.')
    parser.add_argument('topics_directory', help='Path to the directory containing the topic JSON files.')
    args = parser.parse_args()

    confirm = input(f"This will modify topic files in '{args.topics_directory}'. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        consolidate_and_resequence(args.topics_directory)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
