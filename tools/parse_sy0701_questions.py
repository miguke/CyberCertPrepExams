#!/usr/bin/env python3
"""
Security+ SY0-701 Question Parser
Parses Questions.txt and populates the topic JSON files in data/sy0-701/
"""

import json
import re
import os
from pathlib import Path
import argparse

# Topic mapping from the questions to JSON files
TOPIC_MAPPING = {
    "General Security Concepts": "general-security-concepts.json",
    "Threats": "threats-vulnerabilities-mitigations.json", 
    "Security Architecture": "security-architecture.json",
    "Security Operations": "security-operations.json",
    "Security Program Management": "security-program-management-oversight.json"
}

def parse_answer_line(answer_line):
    """
    Parse the answer line to extract correct answer(s)
    Handles formats like:
    - "Answer: A – False positive"
    - "Answer: A and B"
    - "Answer: A, B"
    - "Answer: A, B, C"
    """
    # Remove "Answer: " prefix and any explanation after "–"
    answer_part = answer_line.replace("Answer: ", "").split("–")[0].strip()
    
    # Extract letter(s) - handle various formats
    letters = []
    
    # Check for "and" format: "A and B"
    if " and " in answer_part:
        parts = answer_part.split(" and ")
        for part in parts:
            letter = part.strip()
            if letter.isalpha() and len(letter) == 1:
                letters.append(letter)
    
    # Check for comma format: "A, B" or "A,B"
    elif "," in answer_part:
        parts = answer_part.split(",")
        for part in parts:
            letter = part.strip()
            if letter.isalpha() and len(letter) == 1:
                letters.append(letter)
    
    # Single letter format: "A"
    else:
        letter = answer_part.strip()
        if letter.isalpha() and len(letter) == 1:
            letters.append(letter)
    
    # Convert letters to 0-based indices
    indices = []
    for letter in letters:
        if letter in ['A', 'B', 'C', 'D', 'E', 'F']:
            indices.append(ord(letter) - ord('A'))
    
    return indices

def parse_questions_file(file_path):
    """Parse the Questions.txt file and return structured data"""
    questions = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "NEW QUESTION:" to get individual question blocks
    question_blocks = content.split("NEW QUESTION:")[1:]  # Skip empty first element
    
    for block in question_blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
            
        # Parse the header line: "1 – Security Operations"
        header_line = lines[0].strip()
        header_match = re.match(r'(\d+)\s*–\s*(.+)', header_line)
        if not header_match:
            print(f"Warning: Could not parse header: {header_line}")
            continue
            
        question_num = int(header_match.group(1))
        topic = header_match.group(2).strip()
        
        # Find the question text (everything until options start)
        question_lines = []
        options = []
        answer_line = ""
        explanation = ""
        
        i = 1
        # Collect question text
        while i < len(lines) and not lines[i].strip().startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.')):
            if lines[i].strip():
                question_lines.append(lines[i].strip())
            i += 1
        
        question_text = ' '.join(question_lines)
        
        # Collect options
        while i < len(lines) and lines[i].strip().startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.')):
            option_text = lines[i].strip()
            # Remove the letter prefix (A., B., etc.)
            option_content = re.sub(r'^[A-F]\.\s*', '', option_text)
            options.append(option_content)
            i += 1
        
        # Skip empty lines
        while i < len(lines) and not lines[i].strip():
            i += 1
        
        # Find answer line
        if i < len(lines) and lines[i].strip().startswith("Answer:"):
            answer_line = lines[i].strip()
            i += 1
        
        # Skip empty lines
        while i < len(lines) and not lines[i].strip():
            i += 1
        
        # Find explanation
        if i < len(lines) and lines[i].strip().startswith("Explanation:"):
            explanation_lines = [lines[i].strip().replace("Explanation: ", "")]
            i += 1
            # Collect multi-line explanations
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("NEW QUESTION:"):
                explanation_lines.append(lines[i].strip())
                i += 1
            explanation = ' '.join(explanation_lines)
        
        # Parse correct answers
        correct_indices = parse_answer_line(answer_line) if answer_line else []
        
        # Determine question type
        question_type = "multiple" if len(correct_indices) > 1 else "single"
        
        # Create question object
        question_obj = {
            "id": question_num,
            "question": question_text,
            "options": options,
            "correct": correct_indices,
            "explanation": explanation,
            "type": question_type,
            "topic": topic.lower().replace(" ", "-")
        }
        
        questions.append(question_obj)
    
    return questions

def group_questions_by_topic(questions):
    """Group questions by their topic"""
    topic_groups = {}
    
    for question in questions:
        topic = question["topic"]
        if topic not in topic_groups:
            topic_groups[topic] = []
        topic_groups[topic].append(question)
    
    return topic_groups

def write_topic_files(topic_groups, data_dir):
    """Write questions to their respective JSON files"""
    
    # Create mapping from topic names to file names
    file_mapping = {}
    for topic_name, file_name in TOPIC_MAPPING.items():
        topic_key = topic_name.lower().replace(" ", "-")
        file_mapping[topic_key] = file_name
    
    for topic, questions in topic_groups.items():
        # Find the correct file name
        file_name = file_mapping.get(topic)
        if not file_name:
            print(f"Warning: No file mapping found for topic '{topic}'")
            continue
            
        file_path = os.path.join(data_dir, file_name)
        
        # Sort questions by ID
        questions.sort(key=lambda x: x["id"])
        
        # Write to JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        print(f"Written {len(questions)} questions to {file_name}")

def main():
    """Main function to parse file and write to staging."""
    parser = argparse.ArgumentParser(description="Parse SY0-701 questions from a text file into a JSON staging file.")
    parser.add_argument("input_file", help="Path to the input text file (e.g., 'Questions 3.txt')")
    parser.add_argument("output_file", help="Path to the output JSON staging file")
    args = parser.parse_args()

    questions_file = Path(args.input_file)
    output_staging_file = Path(args.output_file)
    
    if not questions_file.exists():
        print(f"Error: Input file not found at {questions_file}")
        return
    
    print(f"Parsing questions from: {questions_file}")
    
    # Parse questions
    questions = parse_questions_file(questions_file)
    print(f"Parsed {len(questions)} questions")

    # Write to a single staging file
    print(f"\nWriting to staging file: {output_staging_file}")
    with open(output_staging_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! All {len(questions)} questions have been parsed and written to {output_staging_file}.")


if __name__ == "__main__":
    main()
