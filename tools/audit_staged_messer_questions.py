import json
import os
import re

# --- CONFIGURATION ---
STAGING_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', '1102', 'new_questions_staging_messer.json')
REPORT_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'reports', 'messer_audit_report.md')

# This mapping must match the one in the importer script
OBJECTIVE_TO_TOPIC_MAP = {
    '1': 'operating-systems',
    '2': 'security',
    '3': 'software-troubleshooting',
    '4': 'operational-procedures'
}

# Regex to find the objective ID within the question block (explanation)
OBJECTIVE_RE = re.compile(r"220-1102, Objective (\d+)\.\d+")

# --- MAIN AUDIT LOGIC ---

def audit_questions():
    """Loads the staged questions and runs a series of validation checks."""
    print(f"Starting audit of {STAGING_FILE_PATH}...")
    
    try:
        with open(STAGING_FILE_PATH, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Could not read or parse the staging file. {e}")
        return

    errors = []
    total_questions = len(questions)

    for i, q in enumerate(questions):
        source_id = q.get('source_id', 'N/A')
        
        # 1. Structural Integrity Checks
        if not q.get('question', '').strip():
            errors.append(f"**{source_id} (Index {i}): Missing Question Text**")

        if not q.get('explanation', '').strip():
            errors.append(f"**{source_id} (Index {i}): Missing Explanation Text**")

        options = q.get('options', [])
        if len(options) < 4:
            errors.append(f"**{source_id} (Index {i}): Insufficient Options** - Found {len(options)}, expected at least 4.")

        correct_indices = q.get('correct', [])
        if not correct_indices or not isinstance(correct_indices, list):
            errors.append(f"**{source_id} (Index {i}): Invalid 'correct' field** - Must be a non-empty list.")
        elif any(idx >= len(options) for idx in correct_indices):
            errors.append(f"**{source_id} (Index {i}): Invalid Answer Index** - Index {correct_indices} is out of bounds for {len(options)} options.")

        # 2. Topic Verification Check
        # We need to find the objective ID in the explanation to verify the topic
        explanation_text = q.get('explanation', '')
        obj_match = OBJECTIVE_RE.search(explanation_text)
        
        expected_topic = 'unclassified'
        if obj_match:
            main_objective_id = obj_match.group(1)
            expected_topic = OBJECTIVE_TO_TOPIC_MAP.get(main_objective_id, 'unclassified')
        
        if q.get('topic') != expected_topic:
            errors.append(f"**{source_id} (Index {i}): Topic Mismatch** - Found '{q.get('topic')}', but expected '{expected_topic}'.")

    # --- REPORT GENERATION ---
    print(f"Audit complete. Found {len(errors)} issues.")
    
    # Ensure the reports directory exists
    os.makedirs(os.path.dirname(REPORT_FILE_PATH), exist_ok=True)
    
    with open(REPORT_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write("# Messer Core 2 (220-1102) Staging File Audit Report\n\n")
        f.write(f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**File Audited:** `{os.path.basename(STAGING_FILE_PATH)}`\n")
        f.write(f"**Total Questions Audited:** {total_questions}\n")
        f.write(f"**Total Issues Found:** {len(errors)}\n\n")
        f.write("---\n\n")

        if not errors:
            f.write("## ✅ Success!\n\nAll questions passed validation checks. The file is ready for merging.\n")
        else:
            f.write("## ❌ Issues Found\n\n")
            for error in errors:
                f.write(f"- {error}\n")

    print(f"Report saved to {REPORT_FILE_PATH}")

if __name__ == '__main__':
    audit_questions()
