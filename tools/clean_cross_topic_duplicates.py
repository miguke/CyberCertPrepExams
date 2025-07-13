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

def prompt_for_choice(pair):
    """Display duplicate information and prompt for which version to keep."""
    print("\n" + "=" * 80)
    print(f"Cross-Topic Duplicate - Similarity: {pair['similarity']*100:.2f}%")
    print(f"Topic 1: {pair['topic1']} (File: {pair['file1']})")
    print(f"Topic 2: {pair['topic2']} (File: {pair['file2']})")
    print("-" * 80)
    print(f"Question from {pair['topic1']}:")
    print(pair['q1_text'])
    print(f"Correct answers: {pair['q1_correct']}")
    print("-" * 80)
    print(f"Question from {pair['topic2']}:")
    print(pair['q2_text'])
    print(f"Correct answers: {pair['q2_correct']}")
    print("=" * 80)
    
    while True:
        choice = input(f"\nWhich version do you want to keep? (1={pair['topic1']}, 2={pair['topic2']}, s=skip): ")
        if choice in ['1', '2', 's']:
            return choice
        print("Invalid choice. Please enter 1, 2, or s.")

def clean_cross_topic_duplicates(analysis_file):
    """Clean cross-topic duplicate questions based on the enhanced analysis file."""
    print(f"Processing duplicate analysis file: {analysis_file}")
    
    # Load the duplicate analysis
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    cross_topic_pairs = analysis.get('cross_topic', {}).get('pairs', [])
    if not cross_topic_pairs:
        print("No cross-topic duplicates found in the analysis file.")
        return
    
    print(f"Found {len(cross_topic_pairs)} cross-topic duplicate pairs to review.")
    
    # Track all files that will be modified
    files_to_modify = {}
    data_dir = os.path.dirname(analysis_file)
    
    # Process each cross-topic pair
    for i, pair in enumerate(cross_topic_pairs, 1):
        print(f"\nReviewing duplicate pair {i} of {len(cross_topic_pairs)}")
        
        # Get file paths
        file1 = os.path.join(data_dir, pair['file1'])
        file2 = os.path.join(data_dir, pair['file2'])
        
        # Ensure both files exist
        if not os.path.exists(file1):
            print(f"Warning: File {file1} not found. Skipping this pair.")
            continue
        
        if not os.path.exists(file2):
            print(f"Warning: File {file2} not found. Skipping this pair.")
            continue
        
        # Prompt for user choice
        choice = prompt_for_choice(pair)
        
        if choice == 's':
            print("Skipping this duplicate pair.")
            continue
        
        # Initialize file data if not already loaded
        if file1 not in files_to_modify:
            with open(file1, 'r', encoding='utf-8') as f:
                files_to_modify[file1] = json.loads(f.read())
        
        if file2 not in files_to_modify:
            with open(file2, 'r', encoding='utf-8') as f:
                files_to_modify[file2] = json.loads(f.read())
        
        # Determine which question to remove based on user choice
        if choice == '1':
            # Keep question in file1, remove from file2
            remove_file = file2
            remove_index = pair['index2']
            keep_file = file1
            print(f"Keeping question in {pair['topic1']} and removing from {pair['topic2']}")
        else:  # choice == '2'
            # Keep question in file2, remove from file1
            remove_file = file1
            remove_index = pair['index1']
            keep_file = file2
            print(f"Keeping question in {pair['topic2']} and removing from {pair['topic1']}")
        
        # Mark the question for removal
        if 0 <= remove_index < len(files_to_modify[remove_file]):
            files_to_modify[remove_file][remove_index] = None  # Mark for removal
    
    # Remove marked questions and save files
    for filepath, questions in files_to_modify.items():
        # Create backup before modifying
        backup_file(filepath)
        
        # Remove None values (questions marked for removal)
        updated_questions = [q for q in questions if q is not None]
        
        # Save updated questions
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(updated_questions, f, indent=2)
        
        print(f"Updated {filepath}: Removed {len(questions) - len(updated_questions)} questions")
    
    print("\nCross-topic duplicate cleaning complete.")

def main():
    parser = argparse.ArgumentParser(description='Clean cross-topic duplicate questions interactively.')
    parser.add_argument('analysis_file', nargs='?', 
                        default=None,
                        help='Path to the enhanced duplicate_analysis JSON file. If not provided, looks for the most recent one.')
    parser.add_argument('--threshold', type=float, default=0.9, 
                        help='Only used if analysis_file not provided. Similarity threshold to look for.')
    parser.add_argument('--exam', choices=['1101', '1102'], default='1101',
                        help='Only used if analysis_file not provided. Exam to process.')
    args = parser.parse_args()
    
    if args.analysis_file:
        analysis_file = args.analysis_file
    else:
        # Find the most recent enhanced analysis file
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', args.exam)
        analysis_pattern = f"duplicate_analysis_enhanced_{args.threshold:.1f}.json"
        analysis_file = os.path.join(data_dir, analysis_pattern)
        
        if os.path.exists(analysis_file):
            analysis_file = analysis_file
        else:
            print(f"Error: Could not find analysis file {analysis_file}")
            print("Please run find_similar_questions_enhanced.py first or specify the analysis file path.")
            return 1
    
    clean_cross_topic_duplicates(analysis_file)
    return 0

if __name__ == '__main__':
    main()
