import json
import argparse
import os

def merge_json_files(input_files, output_file):
    """Merges multiple JSON files (each containing a list of objects) into one."""
    merged_questions = []
    total_questions = 0

    for file_path in input_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                merged_questions.extend(questions)
                print(f"Read {len(questions)} questions from {os.path.basename(file_path)}.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading file {file_path}: {e}")
            return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_questions, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully merged {len(merged_questions)} total questions into {output_file}.")
    except IOError as e:
        print(f"Error writing to output file {output_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Merge multiple JSON question files into a single output file.')
    parser.add_argument('output_file', help='Path to the final merged JSON file.')
    parser.add_argument('input_files', nargs='+', help='Paths to the input JSON files to be merged.')
    args = parser.parse_args()

    merge_json_files(args.input_files, args.output_file)

if __name__ == "__main__":
    main()
