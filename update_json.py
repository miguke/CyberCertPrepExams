import json
import sys
import os

def append_questions_from_file(target_file_path, new_questions_file_path):
    try:
        # Read existing questions
        existing_questions = []
        if os.path.exists(target_file_path) and os.path.getsize(target_file_path) > 0:
            with open(target_file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_questions = json.load(f)
                    if not isinstance(existing_questions, list):
                        print(f"Error: Existing JSON in {target_file_path} is not a list.")
                        return False
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON from {target_file_path}.")
                    existing_questions = []
        
        # Read new questions from the provided file path
        try:
            with open(new_questions_file_path, 'r', encoding='utf-8') as f_new:
                new_questions = json.load(f_new)
            if not isinstance(new_questions, list):
                print(f"Error: JSON in {new_questions_file_path} is not a list.")
                return False
        except FileNotFoundError:
            print(f"Error: New questions file {new_questions_file_path} not found.")
            return False
        except json.JSONDecodeError as e_new:
            print(f"Error: Could not decode JSON from {new_questions_file_path}: {e_new}")
            return False

        # Append new questions
        combined_questions = existing_questions + new_questions
        
        # Write back pretty-printed
        with open(target_file_path, 'w', encoding='utf-8') as f_target:
            json.dump(combined_questions, f_target, indent=2, ensure_ascii=False)
        
        print(f"Successfully updated {target_file_path} with {len(new_questions)} new questions from {new_questions_file_path}.")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_json.py <target_file_path> <new_questions_file_path>")
        sys.exit(1)
    
    target_file_path_arg = sys.argv[1]
    new_questions_file_path_arg = sys.argv[2]
    
    if not append_questions_from_file(target_file_path_arg, new_questions_file_path_arg):
        sys.exit(1)
