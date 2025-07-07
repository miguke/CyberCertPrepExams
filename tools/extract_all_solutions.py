import json
import os
import re
import pdfplumber

# --- CONFIGURATION ---
INPUT_PDF_PATH = os.path.join(os.path.dirname(__file__), '..', "PDF's", 'comptia-a-practice-test-core-1-220-1101-over-500-practice-questions-to-help-you-pass-the-comptia-a-cor.pdf')
OUTPUT_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', '1101', 'solutions_ground_truth.json')

# Page range for solutions (0-indexed). 
# The importer script indicated solutions end at page 187 (index 186).
SOLUTION_PAGES = (130, 186) 

# Regex to split the text into individual solution entries.
# This looks for a newline followed by a number, a period, and "The correct answer is".
SOLUTION_SPLIT_RE = re.compile(r'\n(?=\d+\.\s+The correct answer is)')

def extract_all_solutions():
    """Extracts all solutions from the PDF and saves them to a JSON file."""
    if not os.path.exists(INPUT_PDF_PATH):
        print(f"ERROR: Input PDF not found at {INPUT_PDF_PATH}")
        return

    print(f"Extracting solutions from pages {SOLUTION_PAGES[0] + 1} to {SOLUTION_PAGES[1] + 1}...")
    full_solution_text = ''
    try:
        with pdfplumber.open(INPUT_PDF_PATH) as pdf:
            for i in range(SOLUTION_PAGES[0], SOLUTION_PAGES[1] + 1):
                if i < len(pdf.pages):
                    page = pdf.pages[i]
                    # Add a space to handle cases where a solution block is split across pages
                    full_solution_text += page.extract_text() + '\n'
                else:
                    print(f"Warning: Page {i + 1} is out of range.")
                    break
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return

    # Split the entire text block into individual solutions
    solution_blocks = SOLUTION_SPLIT_RE.split(full_solution_text)
    
    extracted_solutions = []
    for i, block in enumerate(solution_blocks):
        if not block or not block.strip():
            continue
        
        # Clean up the block text
        # Remove the initial question number and "The correct answer is..."
        match = re.search(r'\d+\.\s+The correct answer is\s+[A-D]\.\s*(.*)', block.strip(), re.DOTALL)
        if match:
            explanation = match.group(1).replace('\n', ' ').strip()
            extracted_solutions.append({
                "ground_truth_id": i, # Assign a simple sequential ID
                "explanation": explanation
            })

    print(f"Successfully extracted {len(extracted_solutions)} explanations.")

    # Save the results to the output file
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(extracted_solutions, f, indent=2, ensure_ascii=False)
    
    print(f"Saved ground truth explanations to {OUTPUT_JSON_PATH}")

if __name__ == '__main__':
    extract_all_solutions()
