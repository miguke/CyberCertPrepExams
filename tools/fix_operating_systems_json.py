import json
import os
import re
from datetime import datetime
import shutil

# Path to the operating systems JSON file
input_file = '../data/1102/operating-systems.json'

# Create a backup directory if it doesn't exist
backup_dir = '../data/1102/backups'
os.makedirs(backup_dir, exist_ok=True)

# Create a backup of the original file
backup_filename = f"operating-systems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
backup_path = os.path.join(backup_dir, backup_filename)
shutil.copy(input_file, backup_path)
print(f"Backup created at {backup_path}")

# Load the JSON data
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} questions from {input_file}")

# Function to check if a question is embedded in the options or explanation
def check_for_embedded_questions(item):
    # Regular expressions to detect embedded questions
    question_patterns = [
        r'([A-Z]\d+\.\s.+\?)',  # Pattern like "B60. A macOS user needs..."
        r'(More information:.+\d+ Practice Exam [A-Z] - Answers \d+\s+[A-Z]\d+\.\s.+\?)'  # Pattern after "More information"
    ]
    
    # Check each option for embedded questions
    embedded_questions = []
    for option in item.get("options", []):
        for pattern in question_patterns:
            matches = re.findall(pattern, option)
            for match in matches:
                embedded_questions.append(match)
    
    # Check explanation for embedded questions
    explanation = item.get("explanation", "")
    for pattern in question_patterns:
        matches = re.findall(pattern, explanation)
        for match in matches:
            embedded_questions.append(match)
            
    return embedded_questions

# Function to extract a new question from text containing an embedded question
def extract_question_data(embedded_text, original_item):
    # Example format: "B60. A macOS user needs encrypt all..."
    
    # Extract the question ID (like B60)
    source_id_match = re.match(r'([A-Z]\d+)', embedded_text)
    source_id = source_id_match.group(1) if source_id_match else None
    
    # Extract the question text
    question_match = re.search(r'([A-Z]\d+\.\s)(.+?\?))', embedded_text)
    question = question_match.group(2) if question_match else embedded_text
    
    # Look for options in the original item's options after this question
    options = []
    found_options = False
    for option in original_item.get("options", []):
        if question in option:
            found_options = True
            continue
        if found_options and not option.startswith("The Answers:") and not option.startswith("More information:"):
            options.append(option)
    
    # Extract the correct answer from the explanation
    correct_index = None
    explanation = ""
    if "explanation" in original_item:
        explanation_text = original_item["explanation"]
        # This is more complex and would need custom parsing for each case
        
    return {
        "source_id": source_id,
        "question": question,
        "options": options,
        "type": "single",
        "source_pdf": original_item.get("source_pdf", "")
    }

# Manually fix known problematic questions
fixed_data = []
next_id = 1  # Initialize ID counter

# Process each question
for item in data:
    current_id = next_id
    next_id += 1
    
    # Handle specific known problematic questions
    if item["id"] == 63:
        # Fix the first question (ID 63)
        fixed_question_1 = {
            "id": current_id,
            "question": "A user in the accounting department has installed a new application for the upcoming tax year. Although the current application worked perfectly, the newer application runs significantly slower. Which of the following should be the FIRST troubleshooting step?",
            "options": [
                "Roll back to the previous application",
                "Run a repair installation",
                "Verify the requirements for the new application", 
                "Perform a system file check"
            ],
            "correct": [2],
            "explanation": "Verify the requirements for the new application. The new application may not have the same requirements as the older application, so the user's computer may require additional CPU, memory, or storage space.",
            "type": "single",
            "source_pdf": item.get("source_pdf", ""),
            "source_id": item.get("source_id", "")
        }
        fixed_data.append(fixed_question_1)
        
        # Create the second question (FileVault)
        fixed_question_2 = {
            "id": next_id,
            "question": "A macOS user needs encrypt all of the information on their laptop. Which of the following would be the BEST choice for this requirement?",
            "options": [
                "Spaces",
                "Remote Disc",
                "FileVault",
                "Keychain"
            ],
            "correct": [2],
            "explanation": "FileVault is the correct answer. The FileVault utility provides full disk encryption for macOS devices.",
            "type": "single",
            "source_pdf": item.get("source_pdf", ""),
            "source_id": "B60"
        }
        fixed_data.append(fixed_question_2)
        next_id += 1
        
    elif item["id"] == 89:
        # Create the server security question
        fixed_question_1 = {
            "id": current_id,
            "question": "An administrator is implementing security measures on a server. Which TWO of the following would be the BEST choices to increase the security of this server? (Choose two.)",
            "options": [
                "Disable guest account",
                "Enable file storage quotas",
                "Enable password complexity",
                "Enable a BIOS user password",
                "Connect the server to a wireless network",
                "Limit the number of concurrent connections"
            ],
            "correct": [0, 2],
            "explanation": "Disable guest account and enable password complexity. The only available options associated with server security are those to disable guest accounts and increase the complexity of the passwords. Guest accounts can be exploited, and passwords that are easy to guess or set to defaults can be discovered by an attacker.",
            "type": "multiple",
            "source_pdf": item.get("source_pdf", ""),
            "source_id": item.get("source_id", "")
        }
        fixed_data.append(fixed_question_1)
        
        # Create the 32-bit OS RAM question
        fixed_question_2 = {
            "id": next_id,
            "question": "A user has purchased a computer that uses a 32-bit version of an operating system. Which of the following would be the maximum amount of RAM supported in this OS?",
            "options": [
                "32 GB",
                "2 TB",
                "512 GB",
                "128 GB",
                "4 GB",
                "16 GB"
            ],
            "correct": [4],
            "explanation": "4 GB. A 32-bit operating system can store 2^32 values, or approximately 4 GB of address space.",
            "type": "single",
            "source_pdf": item.get("source_pdf", ""),
            "source_id": "C75"
        }
        fixed_data.append(fixed_question_2)
        next_id += 1
    
    else:
        # For all other questions, just update the ID and keep them
        item["id"] = current_id
        fixed_data.append(item)

# Update all IDs to be sequential
for i, item in enumerate(fixed_data, 1):
    item["id"] = i

# Save the fixed data
with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(fixed_data, f, indent=2, ensure_ascii=False)

print(f"Fixed data saved with {len(fixed_data)} questions")
print(f"Original data had {len(data)} questions")
print(f"Added {len(fixed_data) - len(data)} new questions that were previously embedded")
