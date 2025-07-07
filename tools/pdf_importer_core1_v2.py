import json
import os
import re
import pdfplumber

# --- CONFIGURATION ---
INPUT_PDF_PATH = os.path.join(os.path.dirname(__file__), '..', "PDF's", 'comptia-a-practice-test-core-1-220-1101-over-500-practice-questions-to-help-you-pass-the-comptia-a-cor.pdf')
STAGING_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'new_questions_staging_v3_mapped.json') # Output to the v3 mapped file

# Page ranges (0-indexed)
QUESTION_PAGES = (0, 129)
SOLUTION_PAGES = (130, 186)

# Regex patterns
TOPIC_HEADER_RE = re.compile(r'^\s*(\d+\.\d+)\s+(.+?)\s*$', re.MULTILINE)
OPTION_RE = re.compile(r'([A-Z])\.\s+(.+)')

# --- DEDUPLICATION LOGIC ---

def get_question_signature(question_obj):
    """Creates a unique signature for a question for deduplication."""
    question_text = question_obj.get("question", "").strip().casefold()
    options = sorted([str(opt).strip().casefold() for opt in question_obj.get("options", [])])
    return f"{question_text}|{'|'.join(options)}"

def load_existing_signatures():
    """Loads signatures of all existing 1101 questions to avoid duplicates."""
    existing_signatures = set()
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', '1101')
    # Only check against main topic files, not staging files
    topic_files = ['hardware.json', 'networking.json', 'mobile-devices.json', 'troubleshooting.json', 'virtualization-cloud.json', 'miscellaneous.json']

    for filename in topic_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    for q in questions:
                        existing_signatures.add(get_question_signature(q))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not process {filepath}. Error: {e}")
    
    print(f"Loaded {len(existing_signatures)} existing question signatures for deduplication.")
    return existing_signatures

# --- PDF PARSING LOGIC (REVISED) ---

def parse_content_by_topic(pdf, page_range):
    """Parses either questions or solutions, organizing them by topic."""
    print(f"Parsing pages {page_range[0]+1} to {page_range[1]+1}...")
    full_text = ''
    for i in range(page_range[0], page_range[1] + 1):
        if i < len(pdf.pages):
            full_text += pdf.pages[i].extract_text() + '\n'

    # Stop at the mock exam section if present
    mock_exam_marker = 'MOCK EXAM'
    mock_idx = full_text.find(mock_exam_marker)
    if mock_idx != -1:
        full_text = full_text[:mock_idx]

    content_by_topic = {}
    # Split the text by topic headers
    topic_splits = TOPIC_HEADER_RE.split(full_text)
    
    for i in range(1, len(topic_splits), 3):
        topic_id = topic_splits[i]
        topic_content = topic_splits[i+2]
        content_by_topic[topic_id] = topic_content
        
    return content_by_topic

def extract_questions(topic_content):
    """Extracts individual questions from a block of topic text."""
    questions = {}
    question_blocks = re.split(r'\n(?=\d+\.\s)', topic_content)

    for block in question_blocks:
        block = block.strip()
        if not block:
            continue

        q_match = re.match(r'(\d+)\.\s+(.*)', block, re.DOTALL)
        if not q_match:
            continue
        
        qid = int(q_match.group(1))
        q_and_options = q_match.group(2)
        
        options = []
        option_matches = list(OPTION_RE.finditer(q_and_options))
        
        if not option_matches:
            continue

        first_option_start = option_matches[0].start()
        question_text = q_and_options[:first_option_start].replace('\n', ' ').strip()
        
        for opt_match in option_matches:
            options.append(opt_match.group(2).replace('\n', ' ').strip())

        if question_text and options:
            questions[qid] = {"question": question_text, "options": options}
    return questions

def extract_solutions(topic_content):
    """Extracts individual solutions from a block of topic text."""
    solutions = {}
    solution_blocks = re.split(r'\n(?=\d+\.\s)', topic_content)

    for block in solution_blocks:
        block = block.strip()
        if not block:
            continue

        match = re.search(r'^(?P<qid>\d+)\.\s+The correct answer is (?P<letter>[A-D])\.\s*(?P<exp>.*)', block, re.DOTALL)
        if match:
            qid = int(match.group('qid'))
            letter = match.group('letter')
            explanation = match.group('exp').replace('\n', ' ').strip()
            solutions[qid] = {
                'correct_index': ord(letter) - ord('A'),
                'explanation': explanation
            }
    return solutions

def main():
    """Main function to run the full import and merge process."""
    if not os.path.exists(INPUT_PDF_PATH):
        print(f"ERROR: Input PDF not found at {INPUT_PDF_PATH}")
        return

    existing_signatures = load_existing_signatures()
    
    with pdfplumber.open(INPUT_PDF_PATH) as pdf:
        question_content_by_topic = parse_content_by_topic(pdf, QUESTION_PAGES)
        solution_content_by_topic = parse_content_by_topic(pdf, SOLUTION_PAGES)

    final_questions = []
    skipped_duplicates = 0
    skipped_no_solution = 0
    total_questions_processed = 0

    for topic_id, content in question_content_by_topic.items():
        questions_in_topic = extract_questions(content)
        solutions_in_topic = extract_solutions(solution_content_by_topic.get(topic_id, ''))

        for q_num, q_data in questions_in_topic.items():
            total_questions_processed += 1
            composite_id = f"{topic_id}.{q_num}"

            # Check for duplicates before processing
            sig = get_question_signature(q_data)
            if sig in existing_signatures:
                skipped_duplicates += 1
                continue
            
            solution_data = solutions_in_topic.get(q_num)
            if not solution_data:
                print(f"Warning: No solution found for question with composite ID {composite_id}.")
                skipped_no_solution += 1
                continue

            final_questions.append({
                "id": -1,
                "topic_id_from_pdf": topic_id,
                "topic_id_from_pdf_and_question": composite_id,
                "question": q_data['question'],
                "options": q_data['options'],
                "correct": [solution_data['correct_index']],
                "explanation": solution_data['explanation'],
                "type": "single",
                "source_pdf": os.path.basename(INPUT_PDF_PATH)
            })
            existing_signatures.add(sig)

    print("\n--- Import Summary ---")
    print(f"Total questions processed from PDF: {total_questions_processed}")
    print(f"Skipped (already exist): {skipped_duplicates}")
    print(f"Skipped (no solution found): {skipped_no_solution}")
    print(f"New unique questions to be saved: {len(final_questions)}")

    if final_questions:
        os.makedirs(os.path.dirname(STAGING_OUTPUT_FILE), exist_ok=True)
        with open(STAGING_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_questions, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully saved {len(final_questions)} new questions to {STAGING_OUTPUT_FILE}")

if __name__ == '__main__':
    main()
