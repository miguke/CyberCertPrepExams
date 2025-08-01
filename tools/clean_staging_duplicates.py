import json
import os
import argparse
from collections import defaultdict

def clean_staging_duplicates(analysis_file, staging_files):
    """Cleans staging files based on a duplicate analysis report."""
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading analysis file {analysis_file}: {e}")
        return

    indices_to_delete = defaultdict(set)

    # Process within-file duplicates
    for pair in analysis_results.get('within_file_duplicates', []):
        # We only care about duplicates in our staging files
        if pair['filename'] in [os.path.basename(f) for f in staging_files]:
            # Mark the second question in the pair for deletion
            indices_to_delete[pair['filename']].add(pair['index2'])

    # Process cross-file duplicates
    for pair in analysis_results.get('cross_file_duplicates', []):
        file1_base = os.path.basename(pair['file1'])
        file2_base = os.path.basename(pair['file2'])
        staging_basenames = [os.path.basename(f) for f in staging_files]

        # Case 1: One file is a staging file, the other is not (i.e., an existing topic file)
        # Mark the question from the staging file for deletion.
        if file1_base in staging_basenames and file2_base not in staging_basenames:
            indices_to_delete[file1_base].add(pair['index1'])
        elif file2_base in staging_basenames and file1_base not in staging_basenames:
            indices_to_delete[file2_base].add(pair['index2'])
        
        # Case 2: Both files are staging files
        # Mark the second one for deletion to be consistent.
        elif file1_base in staging_basenames and file2_base in staging_basenames:
            indices_to_delete[file2_base].add(pair['index2'])

    # Now, read each staging file, filter out the duplicates, and write a new cleaned file
    for file_path in staging_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading staging file {file_path}: {e}")
            continue

        basename = os.path.basename(file_path)
        delete_indices = indices_to_delete.get(basename, set())
        
        if not delete_indices:
            print(f"No duplicates to remove from {basename}.")
            cleaned_questions = questions
        else:
            print(f"Removing {len(delete_indices)} duplicate questions from {basename}...")
            cleaned_questions = [q for i, q in enumerate(questions) if i not in delete_indices]

        # Write the cleaned file
        dir_name = os.path.dirname(file_path)
        file_name_root, ext = os.path.splitext(basename)
        output_path = os.path.join(dir_name, f"{file_name_root}_cleaned{ext}")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_questions, f, indent=2, ensure_ascii=False)
        
        print(f"Wrote {len(cleaned_questions)} unique questions to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Clean duplicate questions from staging files based on an analysis report.')
    parser.add_argument('analysis_file', help='Path to the duplicate_analysis_results.json file.')
    parser.add_argument('staging_files', nargs='+', help='Paths to the staging JSON files to be cleaned.')
    args = parser.parse_args()

    clean_staging_duplicates(args.analysis_file, args.staging_files)

if __name__ == "__main__":
    main()
