#!/usr/bin/env python3
import json
import os
import argparse
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the file with timestamp."""
    backup_dir = os.path.join(os.path.dirname(filepath), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
    
    shutil.copy2(filepath, backup_path)
    print(f"Created backup: {backup_path}")
    
    return backup_path

def should_remove_question(q1_text, q2_text):
    """Determine which question should be removed based on specified criteria."""
    # Check for "Select TWO" pattern - keep the one with it if only one has it
    q1_has_select_two = "(Select TWO)" in q1_text
    q2_has_select_two = "(Select TWO)" in q2_text
    
    if q1_has_select_two and not q2_has_select_two:
        return 2  # Remove q2
    elif q2_has_select_two and not q1_has_select_two:
        return 1  # Remove q1
    
    # If both have it or neither has it, remove the shorter one (likely less specific)
    if len(q1_text) < len(q2_text):
        return 1  # Remove q1
    else:
        return 2  # Remove q2

def clean_duplicates(duplicate_analysis_file):
    """Clean duplicate questions based on the analysis file."""
    print(f"Processing duplicate analysis file: {duplicate_analysis_file}")
    
    # Load the duplicate analysis
    with open(duplicate_analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # Group duplicates by topic file
    duplicates_by_file = {}
    for pair in analysis.get('pairs', []):
        filename = pair.get('filename')
        if filename not in duplicates_by_file:
            duplicates_by_file[filename] = []
        duplicates_by_file[filename].append(pair)
    
    # Process each topic file
    total_removed = 0
    data_dir = os.path.dirname(duplicate_analysis_file)
    
    for filename, pairs in duplicates_by_file.items():
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: File {filepath} not found. Skipping.")
            continue
        
        # Load questions from the file
        with open(filepath, 'r', encoding='utf-8') as f:
            questions = json.loads(f.read())
        
        # Create a backup
        backup_file(filepath)
        
        # Track indices to remove (in reverse order to avoid index shifting)
        indices_to_remove = set()
        
        # Process each duplicate pair
        for pair in pairs:
            idx1 = pair.get('index1')
            idx2 = pair.get('index2')
            q1_text = pair.get('q1_text')
            q2_text = pair.get('q2_text')
            
            # Skip if either index is already marked for removal
            if idx1 in indices_to_remove or idx2 in indices_to_remove:
                continue
            
            # Determine which question to remove
            to_remove = should_remove_question(q1_text, q2_text)
            if to_remove == 1:
                indices_to_remove.add(idx1)
                print(f"Removing Q{idx1} from {filename}: {q1_text[:50]}...")
            else:
                indices_to_remove.add(idx2)
                print(f"Removing Q{idx2} from {filename}: {q2_text[:50]}...")
        
        # Convert to sorted list and reverse to remove from end to start
        indices_to_remove = sorted(indices_to_remove, reverse=True)
        
        # Remove the duplicate questions
        for idx in indices_to_remove:
            if 0 <= idx < len(questions):
                questions.pop(idx)
        
        total_removed += len(indices_to_remove)
        
        # Save the updated questions
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2)
        
        print(f"Removed {len(indices_to_remove)} duplicates from {filename}. New count: {len(questions)}")
    
    print(f"\nCleaning complete. Removed {total_removed} duplicate questions in total.")

def main():
    parser = argparse.ArgumentParser(description='Clean duplicate questions based on similarity analysis.')
    parser.add_argument('analysis_file', nargs='?', 
                        default=None,
                        help='Path to the duplicate_analysis JSON file. If not provided, looks for the most recent one.')
    parser.add_argument('--threshold', type=float, default=0.9, 
                        help='Only used if analysis_file not provided. Similarity threshold to look for.')
    parser.add_argument('--exam', choices=['1101', '1102'], default='1101',
                        help='Only used if analysis_file not provided. Exam to process.')
    args = parser.parse_args()
    
    if args.analysis_file:
        duplicate_analysis_file = args.analysis_file
    else:
        # Find the most recent analysis file
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', args.exam)
        analysis_pattern = f"duplicate_analysis_{args.threshold:.1f}.json"
        analysis_file = os.path.join(data_dir, analysis_pattern)
        
        if os.path.exists(analysis_file):
            duplicate_analysis_file = analysis_file
        else:
            print(f"Error: Could not find analysis file {analysis_file}")
            print("Please run find_similar_questions.py first or specify the analysis file path.")
            return 1
    
    clean_duplicates(duplicate_analysis_file)
    return 0

if __name__ == '__main__':
    main()
