#!/usr/bin/env python3
import json
import os
import re
import sys

def determine_correct_answer(question):
    """
    Analyze the explanation to determine the correct answer index.
    """
    if question.get("correct") and len(question["correct"]) > 0:
        # Skip if already has correct answers
        return question["correct"]
    
    explanation = question.get("explanation", "")
    options = question.get("options", [])
    
    # Initialize with empty array
    correct_indices = []
    
    # Common indicators in explanations
    if not correct_indices:
        # Look for option references like (A), (B) etc. that are mentioned as incorrect
        incorrect_options = set()
        for match in re.finditer(r'\(([A-D])\)', explanation):
            letter = match.group(1)
            # Convert letter to index (A=0, B=1, etc.)
            incorrect_index = ord(letter) - ord('A')
            incorrect_options.add(incorrect_index)
        
        # If we found incorrect options, assume the rest are correct
        if incorrect_options and len(incorrect_options) < len(options):
            correct_indices = [i for i in range(len(options)) if i not in incorrect_options]

    # Look for direct mentions of the option text in the explanation
    if not correct_indices:
        for i, option in enumerate(options):
            # Check if the option is positively mentioned at the beginning of the explanation
            # This is a common pattern where the explanation starts by confirming the correct answer
            if option and len(option) > 5:  # Avoid very short options that might cause false positives
                option_words = option.lower().split()
                explanation_start = explanation.lower().split("explanation:")[1].strip() if "explanation:" in explanation.lower() else explanation.lower()
                
                # Check if the first sentence contains significant words from the option
                first_sentence_end = explanation_start.find('.')
                if first_sentence_end > 0:
                    first_sentence = explanation_start[:first_sentence_end].strip()
                    matches = sum(1 for word in option_words if len(word) > 3 and word in first_sentence)
                    if matches >= 2:  # If multiple significant words match
                        correct_indices.append(i)
                        break

    # Additional method: Look for specific keywords that indicate correctness
    if not correct_indices:
        lines = explanation.split('.')
        for i, option in enumerate(options):
            option_lower = option.lower()
            for line in lines:
                line_lower = line.lower()
                
                # Keywords that suggest this option is correct
                positive_indicators = ["correct", "appropriate", "best", "most likely", "should use", "would use", "proper"]
                if any(indicator in line_lower and option_lower in line_lower for indicator in positive_indicators):
                    correct_indices.append(i)
                    break
    
    # If all else fails, default to option B (index 1) as it's often the correct answer in certification exams
    if not correct_indices:
        print(f"WARNING: Could not determine correct answer for question: {question['question'][:50]}...")
        print(f"         Will have to be fixed manually.")
    
    return correct_indices

def process_file(filepath):
    """
    Process a single JSON file to fill in empty correct arrays.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    total_questions = len(data)
    empty_count = sum(1 for q in data if not q.get("correct") or len(q["correct"]) == 0)
    
    print(f"Processing {os.path.basename(filepath)} - Found {empty_count} questions with empty correct arrays out of {total_questions}")
    
    for question in data:
        if not question.get("correct") or len(question["correct"]) == 0:
            correct_indices = determine_correct_answer(question)
            if correct_indices:
                question["correct"] = correct_indices
                updated_count += 1
    
    remaining_empty = sum(1 for q in data if not q.get("correct") or len(q["correct"]) == 0)
    print(f"Updated {updated_count} questions. Remaining empty: {remaining_empty}")
    
    # Create a backup of the original file
    backup_path = filepath + ".bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w', encoding='utf-8') as f:
            with open(filepath, 'r', encoding='utf-8') as original:
                f.write(original.read())
    
    # Write the updated data back to the file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return updated_count, remaining_empty

def main():
    data_dir = os.path.join(os.getcwd(), "data", "sy0-701")
    if not os.path.exists(data_dir):
        print(f"Error: Directory not found: {data_dir}")
        sys.exit(1)
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        sys.exit(1)
    
    total_updated = 0
    total_remaining = 0
    
    for json_file in json_files:
        filepath = os.path.join(data_dir, json_file)
        updated, remaining = process_file(filepath)
        total_updated += updated
        total_remaining += remaining
    
    print(f"\nSummary: Updated {total_updated} questions. Remaining questions with empty correct arrays: {total_remaining}")
    if total_remaining > 0:
        print("These remaining questions will need manual review.")

if __name__ == "__main__":
    main()
