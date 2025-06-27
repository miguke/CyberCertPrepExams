import re
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Generate recategorization moves from a topic audit report.')
    parser.add_argument('exam', choices=['1101', '1102'], nargs='?', default='1101', help='The exam core for which to generate moves (1101 or 1102). Defaults to 1101.')
    args = parser.parse_args()

    report_filename = f'topic_audit_report_{args.exam}.txt'
    output_filename = f'moves_for_apply_{args.exam}.txt'

    if not os.path.exists(report_filename):
        print(f"Error: Audit report '{report_filename}' not found. Please run the audit script first.")
        return

    moves = []
    current_move = {}

    with open(report_filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Match the first line of a mismatch report entry
            # e.g., "1. ID: ... | File: hardware.json | Index: 12"
            match1 = re.search(r'File:\s*(.*?)\s*\|\s*Index:\s*(\d+)', line)
            if match1:
                # Start a new move object when the first line is found
                current_move = {
                    'original_index': int(match1.group(2))
                }
                continue

            # Match the second line of a mismatch report entry
            # e.g., "Current: hardware | Suggested: mobile-devices"
            match2 = re.search(r'Current:\s*(.*?)\s*\|\s*Suggested:\s*(.*)', line)
            if match2 and current_move:
                current_move['original_file_key'] = match2.group(1).strip()
                current_move['target_topic_key'] = match2.group(2).strip()
                moves.append(current_move)
                current_move = {} # Reset for the next entry

    # Write to file as a Python list of dicts
    with open(output_filename, 'w', encoding='utf-8') as out:
        out.write(f'# Copy the following list into REMOVES_AND_MOVES in apply_categorization_changes.py for exam {args.exam}\n')
        out.write('REMOVES_AND_MOVES = [\n')
        for move in moves:
            # Reorder keys for readability
            ordered_move = {
                'original_file_key': move['original_file_key'],
                'original_index': move['original_index'],
                'target_topic_key': move['target_topic_key']
            }
            out.write(f'    {ordered_move},\n')
        out.write(']\n')
    
    print(f"Generated {len(moves)} recategorization moves for exam {args.exam}. Output written to {output_filename}.")

if __name__ == "__main__":
    main()
