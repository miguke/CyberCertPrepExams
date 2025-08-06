#!/usr/bin/env python3
import json
import os
import shutil
from collections import defaultdict

def backup_file(filepath):
    backup_path = filepath + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"Backup created: {backup_path}")

# Load questions from a file
def load_questions(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Save questions to a file
def save_questions(filepath, questions):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

# Remove duplicates as listed in the analysis file
def remove_duplicates(analysis_file):
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    # Collect all removals by file and index
    removals = defaultdict(set)

    # Handle within-file duplicates
    for pair in analysis.get('within_file_duplicates', []):
        filename = pair['filename']
        # Always remove the second occurrence (index2)
        removals[filename].add(pair['index2'])

    # Handle cross-file duplicates (remove from file2, index2)
    for pair in analysis.get('cross_file_duplicates', []) + analysis.get('cross_topic_pairs', []):
        filename = pair['file2']
        removals[filename].add(pair['index2'])

    # Remove duplicates from each file
    for filename, indices in removals.items():
        filepath = os.path.join(os.path.dirname(analysis_file), filename)
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
        questions = load_questions(filepath)
        backup_file(filepath)
        # Remove by index (careful: indices will shift as we remove)
        indices_to_remove = sorted(indices, reverse=True)
        for idx in indices_to_remove:
            if 0 <= idx < len(questions):
                del questions[idx]
        save_questions(filepath, questions)
        print(f"Removed {len(indices_to_remove)} duplicates from {filename}.")

    print("\nAll reviewed duplicates have been removed.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python remove_reviewed_duplicates.py <path_to_duplicate_analysis_results.json>")
        sys.exit(1)
    remove_duplicates(sys.argv[1])
