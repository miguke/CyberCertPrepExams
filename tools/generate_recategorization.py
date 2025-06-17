import re

def main():
    moves = []
    with open('topic_audit_report.txt', 'r', encoding='utf-8') as f:
        for line in f:
            # Example: 1. ID: 14 | File: hardware.json | Index: 12 | Current: hardware | Suggested: mobile-devices
            if 'ID:' in line and 'Index:' in line and 'Current:' in line and 'Suggested:' in line:
                parts = line.strip().split('|')
                file_part = parts[1].split(':')[1].strip()
                index_part = int(parts[2].split(':')[1].strip())
                current_topic = parts[3].split(':')[1].strip()
                suggested_topic = parts[4].split(':')[1].strip()
                moves.append({
                    'original_file_key': current_topic,
                    'original_index': index_part,
                    'target_topic_key': suggested_topic
                })
    # Write to file as a Python list of dicts
    with open('moves_for_apply.txt', 'w', encoding='utf-8') as out:
        out.write('# Copy the following list into REMOVES_AND_MOVES in apply_categorization_changes.py\n')
        out.write('REMOVES_AND_MOVES = [\n')
        for move in moves:
            out.write(f'    {move},\n')
        out.write(']\n')
    print(f"Generated {len(moves)} recategorization moves. Output written to moves_for_apply.txt.")

if __name__ == "__main__":
    main()
