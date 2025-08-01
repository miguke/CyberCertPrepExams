import json
import os
import argparse

EXAM_CONFIGS = {
    '1101': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1101'),
        'question_files': [
            'hardware.json',
            'mobile-devices.json',
            'networking.json',
            'troubleshooting.json',
            'virtualization-cloud.json',
            'miscellaneous.json',
            'new_questions_staging.json'
        ]
    },
    '1102': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1102'),
        'question_files': [
            'operating-systems.json',
            'security.json',
            'software-troubleshooting.json',
            'operational-procedures.json',
            'miscellaneous.json',
            'new_questions_staging.json'
        ]
    }
}

def validate_questions(filepath):
    """Validates a single JSON file, returns counts for valid, invalid, and total questions."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            questions = json.loads(content) if content.strip() else []
    except FileNotFoundError:
        print(f"Skipping {os.path.basename(filepath)}: File not found.")
        return 0, [], 0
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {os.path.basename(filepath)}.")
        return 0, [], 0

    print(f"Validating {len(questions)} questions in {os.path.basename(filepath)}")
    print("-" * 80)
    
    if not questions:
        print("No questions to validate.")
        return 0, [], 0

    valid_count = 0
    invalid_questions = []
    
    for i, q in enumerate(questions, 1):
        errors = []
        
        if not q.get('question', '').strip():
            errors.append("Missing or empty question text")
            
        options = q.get('options', [])
        if not isinstance(options, list) or not options:
            errors.append("Missing or empty options array")
        else:
            for j, opt in enumerate(options):
                # Allow empty strings as options, but they must be strings.
                if not isinstance(opt, str):
                    errors.append(f"Invalid option at index {j} (value is not a string: {opt})")
        
        correct = q.get('correct', [])
        if not isinstance(correct, list):
            errors.append("Correct answers field is not a list")
        else:
            for ans in correct:
                if not isinstance(ans, int) or ans < 0 or ans >= len(options):
                    errors.append(f"Invalid correct answer index {ans} (options length: {len(options)})")
        
        if 'id' not in q:
            errors.append("Missing question ID")
            
        if q.get('type') not in ['single', 'multiple']:
            errors.append("Missing or invalid question type")
        
        if errors:
            invalid_questions.append({
                'index': i - 1,
                'id': q.get('id', 'N/A'),
                'errors': errors,
                'question_preview': (q.get('question') or '')[:100] + '...' if q.get('question') else 'EMPTY'
            })
        else:
            valid_count += 1
    
    print(f"Valid questions: {valid_count}/{len(questions)}")
    print(f"Invalid questions: {len(invalid_questions)}")
    
    if invalid_questions:
        print("\nFirst 5 invalid questions:")
        for iq in invalid_questions[:5]:
            print(f"\nQuestion #{iq['index'] + 1} (ID: {iq['id']})")
            print(f"Preview: {iq['question_preview']}")
            print("Errors:")
            for err in iq['errors']:
                print(f"  - {err}")
        
        if len(invalid_questions) > 5:
            print(f"\n... and {len(invalid_questions) - 5} more invalid questions.")
    
    return valid_count, invalid_questions, len(questions)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate the structure of CompTIA question JSON files.')
    parser.add_argument('--file', type=str, help='Path to a specific JSON file to validate.')
    parser.add_argument('--exam', choices=['1101', '1102'], help='The exam core to validate (1101 or 1102). Used if --file is not specified.')
    args = parser.parse_args()

    total_valid_questions = 0
    total_invalid_questions = 0
    total_questions_processed = 0

    if args.file:
        print(f"\n--- Validating Single File ---")
        file_path = args.file
        valid, invalid_list, num_processed = validate_questions(file_path)
        total_valid_questions = valid
        total_invalid_questions = len(invalid_list)
        total_questions_processed = num_processed
    elif args.exam:
        config = EXAM_CONFIGS[args.exam]
        data_dir = config['data_dir']
        question_files = config['question_files']
        
        print(f"\n--- Validating Exam {args.exam} Data ---")

        for q_file in question_files:
            file_path = os.path.join(data_dir, q_file)
            valid, invalid_list, num_processed = validate_questions(file_path)
            total_valid_questions += valid
            total_invalid_questions += len(invalid_list)
            total_questions_processed += num_processed
    else:
        parser.print_help()
        exit(1)

    print("\n--- Overall Summary ---")
    print(f"Total questions processed: {total_questions_processed}")
    print(f"Total valid: {total_valid_questions}")
    print(f"Total invalid: {total_invalid_questions}")
    print("-----------------------")

