import os
import json

# --- CONFIGURATION ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1101')
# Process files in a consistent, sorted order to ensure IDs are assigned predictably.
TOPIC_FILES = sorted([
    "hardware.json",
    "mobile-devices.json",
    "networking.json",
    "troubleshooting.json",
    "virtualization-cloud.json",
    "miscellaneous.json"
])

def main():
    """Resequences all question IDs across all specified topic files."""
    print("--- Starting Question ID Resequencing Process ---")
    
    global_id_counter = 1
    total_questions_processed = 0

    for filename in TOPIC_FILES:
        filepath = os.path.join(DATA_DIR, filename)

        if not os.path.exists(filepath):
            print(f"Warning: File {filename} not found. Skipping.")
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Handle empty or whitespace-only files
                questions = json.loads(content) if content.strip() else []
        except (json.JSONDecodeError, IOError) as e:
            print(f"ERROR: Could not read or parse {filename}. Aborting. Error: {e}")
            continue
        
        if not questions:
            print(f"Info: No questions found in {filename}. Skipping.")
            continue

        # Assign new sequential IDs
        for question in questions:
            question['id'] = global_id_counter
            global_id_counter += 1
        
        # Write the updated data back to the file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            print(f"Successfully re-sequenced {len(questions)} questions in {filename}.")
            total_questions_processed += len(questions)
        except IOError as e:
            print(f"ERROR: Could not write updated questions to {filename}. Error: {e}")

    print("\n--- Resequencing Complete ---")
    print(f"Total questions re-sequenced across all files: {total_questions_processed}")
    print(f"The next available question ID is now: {global_id_counter}")

if __name__ == '__main__':
    main()
