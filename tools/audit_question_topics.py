import os
import json
from pdf_question_importer import categorize_question

# Directory containing the topic JSON files
DATA_DIR = os.path.join("..", "data", "1101")
TOPIC_FILES = [
    "hardware.json",
    "mobile-devices.json",
    "networking.json",
    "troubleshooting.json",
    "virtualization-cloud.json",
    "miscellaneous.json",
]

def main():
    mismatches = []
    for filename in TOPIC_FILES:
        topic = filename.replace(".json", "")
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            questions = json.load(f)
        for idx, q in enumerate(questions):
            qtext = q.get("question", "")
            explanation = q.get("explanation", "")
            predicted = categorize_question(qtext, explanation)
            if predicted != topic:
                mismatches.append({
                    "file": filename,
                    "index": idx,
                    "id": q.get("id"),
                    "current_topic": topic,
                    "suggested_topic": predicted,
                    "question": qtext[:80]
                })
    # Write mismatches to file
    with open("topic_audit_report.txt", "w", encoding="utf-8") as out:
        for i, m in enumerate(mismatches, 1):
            out.write(f"{i}. ID: {m['id']} | File: {m['file']} | Index: {m['index']} | Current: {m['current_topic']} | Suggested: {m['suggested_topic']}\n   Q: {m['question']}\n\n")
    print(f"Audit complete. {len(mismatches)} mismatches found. Report written to topic_audit_report.txt")

if __name__ == "__main__":
    main()
