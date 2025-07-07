import os
import json

# --- CONFIGURATION ---
# Input file with 'topic_id_from_pdf' field
INPUT_STAGING_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'new_questions_staging_v2.json')

# Output file where a 'topic' field will be added
OUTPUT_STAGING_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'new_questions_staging_v3_mapped.json')

# Mapping from the main topic number in the PDF to the target topic name
# Based on user feedback and existing file structure.
TOPIC_MAP = {
    '1': 'mobile-devices',
    '2': 'networking',
    '3': 'hardware',
    '4': 'virtualization-cloud',
    '5': 'troubleshooting' 
}

# --- SCRIPT LOGIC ---

def main():
    """Main function to map topic IDs to topic names."""
    print(f"--- Starting Topic ID Mapping Process ---")

    if not os.path.exists(INPUT_STAGING_FILE):
        print(f"ERROR: Input staging file not found at {INPUT_STAGING_FILE}")
        return

    try:
        with open(INPUT_STAGING_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERROR: Could not read or parse {INPUT_STAGING_FILE}. Error: {e}")
        return

    print(f"Loaded {len(questions)} questions from the input file.")

    mapped_count = 0
    unmapped_count = 0

    for q in questions:
        topic_id_from_pdf = q.get('topic_id_from_pdf')
        if not topic_id_from_pdf:
            unmapped_count += 1
            q['topic'] = 'miscellaneous' # Assign a default if missing
            continue

        # Extract the main topic number (e.g., '1' from '1.3')
        main_topic_num = topic_id_from_pdf.split('.')[0]

        # Look up the topic name in our map
        topic_name = TOPIC_MAP.get(main_topic_num)

        if topic_name:
            q['topic'] = topic_name
            mapped_count += 1
        else:
            print(f"Warning: No mapping found for topic ID '{topic_id_from_pdf}'. Assigning to miscellaneous.")
            q['topic'] = 'miscellaneous'
            unmapped_count += 1

    # Save the updated questions to the new staging file
    try:
        with open(OUTPUT_STAGING_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"ERROR: Could not write to output file {OUTPUT_STAGING_FILE}. Error: {e}")
        return

    print(f"\n--- Mapping Summary ---")
    print(f"Successfully mapped {mapped_count} questions.")
    print(f"Assigned {unmapped_count} questions to 'miscellaneous' due to missing or un-mappable IDs.")
    print(f"Processed questions saved to: {OUTPUT_STAGING_FILE}")

if __name__ == '__main__':
    main()
