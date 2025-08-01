import json
import os
import argparse
from collections import defaultdict
import glob

def get_topic_files(directory):
    """Gets all topic JSON files, excluding specific files like staging or results."""
    pattern = os.path.join(directory, '*.json')
    all_files = glob.glob(pattern)
    # Exclude files that are not part of the main dataset
    excluded_keywords = ['staging', 'results', 'cleaned']
    return [f for f in all_files if not any(keyword in os.path.basename(f) for keyword in excluded_keywords)]

def import_and_resequence(staging_file, topics_directory):
    """Merges questions from a staging file into topic files and resequences all IDs."""
    # 1. Load new questions from the final staging file
    try:
        with open(staging_file, 'r', encoding='utf-8') as f:
            new_questions = json.load(f)
        print(f"Loaded {len(new_questions)} new questions from {os.path.basename(staging_file)}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading staging file {staging_file}: {e}")
        return

    # 2. Group new questions by topic
    new_questions_by_topic = defaultdict(list)
    for q in new_questions:
        topic = q.get('topic')
        if topic:
            new_questions_by_topic[topic].append(q)
        else:
            print(f"Warning: Question found with no topic. Skipping: {q.get('question', 'N/A')[:50]}...")

    # 3. Append new questions to their corresponding topic files
    topic_files = get_topic_files(topics_directory)
    for topic_name, questions_to_add in new_questions_by_topic.items():
        topic_filename = f"{topic_name}.json"
        topic_filepath = os.path.join(topics_directory, topic_filename)

        if not os.path.exists(topic_filepath):
            print(f"Warning: Topic file not found for topic '{topic_name}'. Creating new file: {topic_filepath}")
            existing_questions = []
        else:
            try:
                with open(topic_filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    existing_questions = json.loads(content) if content.strip() else []
            except json.JSONDecodeError as e:
                print(f"Error reading topic file {topic_filepath}, skipping merge for this topic. Error: {e}")
                continue
        
        print(f"Adding {len(questions_to_add)} questions to {topic_filename}...")
        existing_questions.extend(questions_to_add)
        
        with open(topic_filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_questions, f, indent=2, ensure_ascii=False)

    # 4. Resequence all question IDs across all topic files
    print("\n--- Starting ID Resequencing ---")
    all_questions_by_topic = defaultdict(list)
    current_id = 1

    # Read all questions from all topic files again to ensure we have the complete set
    topic_files = get_topic_files(topics_directory)
    for file_path in sorted(topic_files): # Sort to ensure a consistent order
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

    print(f"\nProcess complete. Total questions: {current_id - 1}")

def main():
    parser = argparse.ArgumentParser(description='Merge final staging questions into topic files and resequence all IDs.')
    parser.add_argument('staging_file', help='Path to the final_staging.json file.')
    parser.add_argument('topics_directory', help='Path to the directory containing the topic JSON files.')
    args = parser.parse_args()

    # It's a good practice to ask for confirmation before a destructive operation
    confirm = input(f"This will modify the topic files in '{args.topics_directory}'. Are you sure you want to continue? (y/n): ")
    if confirm.lower() == 'y':
        import_and_resequence(args.staging_file, args.topics_directory)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
