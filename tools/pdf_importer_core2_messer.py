import json
import os
import re
import pdfplumber
import multiprocessing
from multiprocessing import Pool, TimeoutError

# --- CONFIGURATION ---

# Input and output paths
INPUT_PDF_PATH = os.path.join(os.path.dirname(__file__), '..', "PDF's", 'comptia-220-1102-a-core-2-practice-exams-james-messer.pdf')
DATA_DIR_1102 = os.path.join(os.path.dirname(__file__), '..', 'data', '1102')
STAGING_OUTPUT_FILE = os.path.join(DATA_DIR_1102, 'new_questions_staging_messer.json')

# Page ranges for each exam section (0-indexed)
# Corrected based on user feedback to point to the 'Detailed Answers' sections.
EXAM_PAGE_RANGES = {
    'A': (49, 136),   # PDF Pages 50-137
    'B': (179, 264),  # PDF Pages 180-265
    'C': (307, 396)   # PDF Pages 308-397
}

# --- TOPIC MAPPING --- 
# Maps the main objective number from the PDF to our topic filenames
OBJECTIVE_TO_TOPIC_MAP = {
    '1': 'operating-systems',
    '2': 'security',
    '3': 'software-troubleshooting',
    '4': 'operational-procedures'
}

# --- REGEX PATTERNS ---

# Matches the start of a question, e.g., 'A1. Some question text...'
# Captures: 1=Exam Letter, 2=Question Number, 3=Rest of the block
# The re.MULTILINE flag allows '^' to match the start of each line, not just the start of the string.
# The pattern is now non-greedy (.+?) and uses a lookahead to properly segment questions.
QUESTION_START_RE = re.compile(r"^([A-C])(\d+)\. (.+?)(?=(?:\n^[A-C]\d+\.|$))", re.DOTALL | re.MULTILINE)

# Matches an option, e.g., 'A. An option'. This lookahead is more specific to stop before the next option, the answer, or the incorrect answer explanations.
OPTION_RE = re.compile(r"^\s*(?:❍ )?([A-F])\. (.*?)(?=(?:^\s*(?:❍ )?[A-F]\.)|\Z)", re.DOTALL | re.MULTILINE)

# Matches the answer line, e.g., 'The Answer: A'
ANSWER_RE = re.compile(r"The Answer: ([A-Z])\.(.*)", re.DOTALL)

# Matches the objective ID line, e.g., '220-1102, Objective 3.1 - ...'
OBJECTIVE_RE = re.compile(r"220-1102, Objective (\d+)\.\d+")

# Matches the explanation line, e.g., 'The Answer: A. ...'
EXPLANATION_RE = re.compile(r"The Answer: [A-Z]\. (.*)", re.DOTALL)

# --- HELPER FUNCTIONS ---

# --- DEDUPLICATION LOGIC ---

def get_question_signature(question_obj):
    """Creates a unique signature for a question for deduplication."""
    question_text = question_obj.get("question", "").strip().casefold()
    options = sorted([str(opt).strip().casefold() for opt in question_obj.get("options", [])])
    return f"{question_text}|{'|'.join(options)}"

def load_existing_signatures(data_dir):
    """Loads signatures of all existing 1102 questions to avoid duplicates."""
    existing_signatures = set()
    if not os.path.exists(data_dir):
        return existing_signatures

    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    for q in questions:
                        existing_signatures.add(get_question_signature(q))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not process {filepath}. Error: {e}")
    
    print(f"Loaded {len(existing_signatures)} existing 1102 question signatures for deduplication.")
    return existing_signatures

# --- PDF PARSING LOGIC ---

def worker_extract_text(page_number, pdf_path):
    """Worker function to extract text from a single page using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_number]
            return page.extract_text()
    except Exception as e:
        return f"WORKER_ERROR: {e}"

def extract_text_from_pdf(pdf_path, ranges, timeout=15):
    """
    Extracts text from specified page ranges in a PDF.
    Uses a fast direct method for most pages and a robust, slower,
    timeout-based method for known problematic pages.
    """
    all_texts = {}
    problem_pages = {106}  # Page 107 is at index 106

    # Use a single Pool that can be called for problem pages
    with Pool(processes=1) as pool:
        # Open the PDF once for the fast extraction part
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            for exam_letter, (start_page, end_page) in ranges.items():
                print(f"Extracting text for Exam {exam_letter} (pages {start_page+1}-{end_page+1})...")
                exam_text = ''

                for i in range(start_page, end_page + 1):
                    if i >= total_pages:
                        continue

                    print(f"  -> Processing page {i+1}...", end='')

                    # Use the robust timeout method only for known problem pages
                    if i in problem_pages:
                        print(" (using safe mode)")
                        try:
                            result = pool.apply_async(worker_extract_text, (i, pdf_path))
                            page_text = result.get(timeout=timeout)
                            if "WORKER_ERROR" in page_text:
                                print(f"     [!] Skipping page {i+1} due to worker error: {page_text}")
                                continue
                            exam_text += page_text + '\n'
                        except TimeoutError:
                            print(f"     [!] Skipping page {i+1} due to timeout.")
                            continue
                        except Exception as e:
                            print(f"     [!] Skipping page {i+1} due to an unexpected error: {e}")
                            continue
                    else:
                        # Use the fast, direct method for all other pages
                        print("") # Newline for clean output
                        try:
                            page = pdf.pages[i]
                            page_text = page.extract_text()
                            if page_text:
                                exam_text += page_text + '\n'
                        except Exception as e:
                            print(f"     [!] Skipping page {i+1} due to a direct extraction error: {e}")
                            continue
                all_texts[exam_letter] = exam_text
    return all_texts

def parse_questions_from_text(text_by_exam):
    """Parses the raw text to extract structured question data using a find-and-iterate approach."""
    all_questions = []
    for exam_letter, full_text in text_by_exam.items():
        # --- Multi-pass parsing strategy ---
        # Pass 1: Find all GUARANTEED question starts. A real question has an answer.
        # This avoids false positives from list items like "A. ..." inside explanations.
        GUARANTEED_START_RE = re.compile(f"^({exam_letter})(\d{{1,2}})\\. .*?The Answer:", re.DOTALL | re.MULTILINE)
        
        matches = list(GUARANTEED_START_RE.finditer(full_text))
        print(f"  [{exam_letter}] Found {len(matches)} guaranteed question starts.")

        # Pass 2: Use the reliable start points to define the full question blocks.
        parsed_count = 0
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
            q_block_text = full_text[start_pos:end_pos]

            # Pass 3: Parse the clean, full block for details.
            
            # Extract the question header info from the original match
            q_id_letter = match.group(1)
            q_id_num = match.group(2)
            header_len = len(q_id_letter) + len(q_id_num) + 2 # Letter + Number + ". "

            # Find where the options end and the answer begins within this block.
            answer_match = ANSWER_RE.search(q_block_text)
            if not answer_match:
                # This shouldn't happen with the new GUARANTEED_START_RE, but as a safeguard:
                print(f"    [!] Skipping block starting with {q_id_letter}{q_id_num} because a clear answer was not found.")
                continue
            
            options_block = q_block_text[:answer_match.start()]

            # Extract options from the options_block
            options = []
            option_matches = list(OPTION_RE.finditer(options_block))
            
            # The actual question text is everything before the first option.
            if not option_matches:
                print(f"    [!] Skipping block {q_id_letter}{q_id_num} - no options found.")
                continue

            first_option_start = option_matches[0].start()
            question_text = options_block[header_len:first_option_start].replace('\n', ' ').strip()
            
            for opt_match in option_matches:
                options.append(opt_match.group(2).replace('\n', ' ').strip())

            # Extract answer and explanation from the answer_match we found earlier
            correct_letter = answer_match.group(1)
            correct_index = ord(correct_letter) - ord('A')
            explanation = answer_match.group(2).replace('\n', ' ').strip()

            # Extract topic using the objective regex
            topic = 'unclassified'
            obj_match = OBJECTIVE_RE.search(q_block_text)
            if obj_match:
                main_objective_id = obj_match.group(1)
                topic = OBJECTIVE_TO_TOPIC_MAP.get(main_objective_id, 'unclassified')

            if question_text and options and explanation:
                all_questions.append({
                    "id": -1,
                    "topic": topic,
                    "question": question_text,
                    "options": options,
                    "correct": [correct_index],
                    "explanation": explanation,
                    "type": "single",
                    "source_pdf": os.path.basename(INPUT_PDF_PATH),
                    "source_id": f"{q_id_letter}{q_id_num}"
                })
                parsed_count += 1
        print(f"  [{exam_letter}] Successfully parsed {parsed_count} questions.")
    return all_questions

# --- MAIN EXECUTION ---

def main():
    """Main function to run the full import process."""
    print("--- Script starting... ---")
    if not os.path.exists(INPUT_PDF_PATH):
        print(f"ERROR: Input PDF not found at {INPUT_PDF_PATH}")
        return

    # Ensure 1102 data directory exists
    os.makedirs(DATA_DIR_1102, exist_ok=True)

    existing_signatures = load_existing_signatures(DATA_DIR_1102)
    
    # We pass the path to the extractor function, not the pdf object, for multiprocessing
    text_by_exam = extract_text_from_pdf(INPUT_PDF_PATH, EXAM_PAGE_RANGES)
    print("\n--- Parsing Extracted Text ---")
    parsed_questions = parse_questions_from_text(text_by_exam)

    final_questions = []
    skipped_duplicates = 0

    for q in parsed_questions:
        sig = get_question_signature(q)
        if sig in existing_signatures:
            skipped_duplicates += 1
            continue
        
        final_questions.append(q)
        existing_signatures.add(sig) # Avoid duplicates from within the same PDF

    print("\n--- Import Summary ---")
    print(f"Total questions extracted from PDF: {len(parsed_questions)}")
    print(f"Skipped (already exist): {skipped_duplicates}")
    print(f"\n--- Saving {len(final_questions)} new questions to {STAGING_OUTPUT_FILE} ---")
    if final_questions:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(STAGING_OUTPUT_FILE), exist_ok=True)
        with open(STAGING_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_questions, f, indent=2)
        print(f"Successfully saved {len(final_questions)} questions.")
    else:
        print("No new, unique questions found to save.")

    if skipped_duplicates > 0:
        print(f"Skipped {skipped_duplicates} duplicate questions.")
    print("--- Script finished. ---")

if __name__ == '__main__':
    main()
