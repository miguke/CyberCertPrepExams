import os
import json
import argparse
from pdf_question_importer import categorize_question, categorize_question_core2

# Configuration for each exam core
EXAM_CONFIGS = {
    '1101': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1101'),
        'topic_files': [
            "hardware.json",
            "mobile-devices.json",
            "networking.json",
            "troubleshooting.json",
            "virtualization-cloud.json",
            "miscellaneous.json",
            "new_questions_staging_v3_mapped.json"
        ],
        'categorize_func': categorize_question
    },
    '1102': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1102'),
        'topic_files': [
            "operating-systems.json",
            "security.json",
            "software-troubleshooting.json",
            "operational-procedures.json",
            "miscellaneous.json",
            "new_questions_staging.json"
        ],
        'categorize_func': categorize_question_core2
    }
}

def main():
    parser = argparse.ArgumentParser(description='Audit the categorization of CompTIA question files.')
    parser.add_argument('exam', choices=['1101', '1102'], nargs='?', default='1101', help='The exam core to audit (1101 or 1102). Defaults to 1101.')
    args = parser.parse_args()

    config = EXAM_CONFIGS[args.exam]
    data_dir = config['data_dir']
    topic_files = config['topic_files']
    categorize_func = config['categorize_func']
    
    print(f"--- Auditing Exam {args.exam} ---")

    mismatches = []
    total_questions = 0

    for filename in topic_files:
        # For staging files, the 'topic' is inside the JSON, not from the filename
        is_staging = "staging" in filename
        current_topic_from_file = filename.replace(".json", "").replace("new_questions_","")

        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            continue
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                questions = json.loads(content) if content.strip() else []
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {filename}. Skipping.")
            continue

        if not questions:
            continue
            
        total_questions += len(questions)

        for idx, q in enumerate(questions):
            qtext = q.get("question", "")
            explanation = q.get("explanation", "")
            
            # Use the topic key from within the question if it's a staging file, otherwise use the filename
            current_topic = q.get("topic") if is_staging else current_topic_from_file
            
            predicted_topic = categorize_func(qtext, explanation)
            
            if predicted_topic != current_topic:
                mismatches.append({
                    "file": filename,
                    "index": idx,
                    "id": q.get("id"),
                    "current_topic": current_topic,
                    "suggested_topic": predicted_topic,
                    "question": qtext.replace('\n', ' ')[:80] + '...'
                })

    # Write mismatches to file
    report_filename = f"topic_audit_report_{args.exam}.txt"
    with open(report_filename, "w", encoding="utf-8") as out:
        out.write(f"--- Topic Audit Report for Exam {args.exam} ---")
        out.write(f"\nFound {len(mismatches)} mismatches out of {total_questions} questions.\n\n")
        for i, m in enumerate(mismatches, 1):
            out.write(f"{i}. ID: {m['id']} | File: {m['file']} | Index: {m['index']}\n")
            out.write(f"   Current: {m['current_topic']} | Suggested: {m['suggested_topic']}\n")
            out.write(f"   Q: {m['question']}\n\n")

    print(f"Audit complete. {len(mismatches)} mismatches found. Report written to {report_filename}")

if __name__ == "__main__":
    main()
