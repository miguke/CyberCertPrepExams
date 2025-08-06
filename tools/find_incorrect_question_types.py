#!/usr/bin/env python3
import json
import re
import glob
import os
import argparse

def find_incorrect_question_types(directory, fix=False):
    """
    Find questions that contain phrases like "(Choose two.)" but are marked as single-choice.
    Optionally fix them by changing the type to "multiple".
    """
    files = glob.glob(os.path.join(directory, '*.json'))
    results = []
    
    multiple_choice_patterns = [
        r'\(Choose two', r'\(choose two', 
        r'\(Choose Three', r'\(choose three',
        r'\(Select two', r'\(select two',
        r'\(Choose \d+\)', r'\(choose \d+\)',
        r'\(Select \d+\)', r'\(select \d+\)'
    ]
    
    pattern = re.compile('|'.join(multiple_choice_patterns))
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        for i, q in enumerate(data):
            question_text = q.get('question', '')
            if pattern.search(question_text) and q.get('type') == 'single':
                correct_answers = len(q.get('correct', []))
                results.append((os.path.basename(file), i, q.get('id', 'unknown'), 
                               question_text[:100] + '...' if len(question_text) > 100 else question_text,
                               correct_answers))
                
                # Fix the question type if requested
                if fix:
                    data[i]['type'] = 'multiple'
                    modified = True
        
        # Save the modified file if changes were made
        if fix and modified:
            backup_path = file + '.bak'
            if not os.path.exists(backup_path):
                os.rename(file, backup_path)
                print(f"Created backup: {backup_path}")
            
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated question types in {os.path.basename(file)}")
    
    print(f"\nFound {len(results)} questions with multiple choice indicators but marked as single type:")
    print("-" * 100)
    for r in results:
        print(f"File: {r[0]}")
        print(f"Index: {r[1]}, ID: {r[2]}")
        print(f"Question: {r[3]}")
        print(f"Correct answers: {r[4]}")
        print("-" * 100)
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find and optionally fix questions with incorrect type settings')
    parser.add_argument('directory', help='Directory containing JSON question files')
    parser.add_argument('--fix', action='store_true', help='Fix incorrect question types by changing them to "multiple"')
    
    args = parser.parse_args()
    find_incorrect_question_types(args.directory, args.fix)
