#!/usr/bin/env python3
import json
import os
import glob
import shutil
import argparse

def backup_file(filepath):
    """Create a backup of the file before modifying it."""
    backup_path = filepath + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"Backup created: {backup_path}")

def fix_question_types(directory, fix=False):
    """
    Find and optionally fix questions with multiple choice indicators but marked as single type.
    """
    files = glob.glob(os.path.join(directory, '*.json'))
    issues = []
    
    for file_path in files:
        filename = os.path.basename(file_path)
        modified = False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                
            for i, q in enumerate(questions):
                question_text = q.get('question', '')
                q_type = q.get('type', '')
                correct_answers = q.get('correct', [])
                
                # Check for multiple choice indicators
                indicators = ['(Choose two', '(choose two', '(Select two', '(select two',
                             '(Choose three', '(choose three', '(Select three', '(select three']
                
                is_multiple_indicator = any(indicator in question_text for indicator in indicators)
                
                if is_multiple_indicator and q_type == 'single':
                    issues.append({
                        'file': filename,
                        'index': i,
                        'id': q.get('id', 'unknown'),
                        'question': question_text[:100] + ('...' if len(question_text) > 100 else ''),
                        'type': q_type,
                        'correct_count': len(correct_answers),
                        'correct': correct_answers
                    })
                    
                    # Fix the question type if requested
                    if fix:
                        questions[i]['type'] = 'multiple'
                        modified = True
            
            # Save the modified file if changes were made
            if fix and modified:
                backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, indent=2, ensure_ascii=False)
                print(f"Updated question types in {filename}")
                    
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print(f"\nFound {len(issues)} questions with multiple choice indicators but marked as single type:")
    print("=" * 80)
    
    for issue in issues:
        print(f"File: {issue['file']}")
        print(f"Index: {issue['index']}, ID: {issue['id']}")
        print(f"Question: {issue['question']}")
        print(f"Type: {issue['type']}")
        print(f"Correct answers: {issue['correct_count']}")
        print(f"Correct array: {issue['correct']}")
        print("-" * 80)
    
    return issues

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find and fix questions with incorrect type settings')
    parser.add_argument('directory', help='Directory containing JSON question files')
    parser.add_argument('--fix', action='store_true', help='Fix incorrect question types by changing them to "multiple"')
    
    args = parser.parse_args()
    fix_question_types(args.directory, args.fix)
