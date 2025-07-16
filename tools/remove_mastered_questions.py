import json
import os
import glob
from datetime import datetime
import shutil

# Directory containing the 1102 JSON files
data_dir = '../data/1102'

# Create backup directory if it doesn't exist
backup_dir = os.path.join(data_dir, 'backups')
os.makedirs(backup_dir, exist_ok=True)

# Timestamp for backups
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Find all JSON files in the directory
json_files = glob.glob(os.path.join(data_dir, '*.json'))
print(f"Found {len(json_files)} JSON files to process")

total_removed = 0

for json_file in json_files:
    file_name = os.path.basename(json_file)
    
    # Skip the backup directory
    if 'backup' in json_file:
        continue
        
    print(f"Processing {file_name}...")
    
    # Create a backup of the original file
    backup_path = os.path.join(backup_dir, f"{file_name.split('.')[0]}_{timestamp}.json")
    shutil.copy(json_file, backup_path)
    print(f"  Backup created at {backup_path}")
    
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data)
    print(f"  Original question count: {original_count}")
    
    # Filter out questions with only "Mastered" and "Not Mastered" options
    filtered_data = []
    removed_count = 0
    
    for question in data:
        options = question.get('options', [])
        # Check if the only options are "Mastered" and "Not Mastered" (in any order)
        if len(options) == 2 and set(options) == {"Mastered", "Not Mastered"}:
            removed_count += 1
            continue
        # Also check for case variations (e.g., "MASTERED", "mastered", etc.)
        elif len(options) == 2 and {opt.lower() for opt in options} == {"mastered", "not mastered"}:
            removed_count += 1
            continue
        else:
            filtered_data.append(question)
    
    # Update IDs to be sequential
    for i, item in enumerate(filtered_data, 1):
        item["id"] = i
    
    # Save the filtered data back to the file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Removed {removed_count} questions with 'Mastered/Not Mastered' options")
    print(f"  New question count: {len(filtered_data)}")
    total_removed += removed_count

print(f"\nProcessing complete! Total questions removed: {total_removed}")
