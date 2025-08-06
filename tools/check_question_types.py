#!/usr/bin/env python3
import json
import os
import glob

def check_question_types(directory):
    """Check for questions with multiple choice indicators but marked as single type."""
    files = glob.glob(os.path.join(directory, '*.json'))
    issues = []
    
    for file_path in files:
        filename = os.path.basename(file_path)
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
                    
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    return issues

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python check_question_types.py <directory>")
        sys.exit(1)
        
    directory = sys.argv[1]
    issues = check_question_types(directory)
    
    print(f"Found {len(issues)} questions with multiple choice indicators but marked as single type:")
    print("=" * 80)
    
    for issue in issues:
        print(f"File: {issue['file']}")
        print(f"Index: {issue['index']}, ID: {issue['id']}")
        print(f"Question: {issue['question']}")
        print(f"Type: {issue['type']}")
        print(f"Correct answers: {issue['correct_count']}")
        print(f"Correct array: {issue['correct']}")
        print("-" * 80)
