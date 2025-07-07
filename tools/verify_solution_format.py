import os
import pdfplumber

# --- CONFIGURATION ---
INPUT_PDF_PATH = os.path.join(os.path.dirname(__file__), '..', "PDF's", 'comptia-a-practice-test-core-1-220-1101-over-500-practice-questions-to-help-you-pass-the-comptia-a-cor.pdf')

# Pages to check (0-indexed)
# PDF page 131 is index 130
SOLUTION_PAGES_TO_CHECK = range(130, 133) # Check PDF pages 131, 132, 133

def verify_format():
    """Extracts and prints the raw text from the first few solution pages."""
    if not os.path.exists(INPUT_PDF_PATH):
        print(f"ERROR: Input PDF not found at {INPUT_PDF_PATH}")
        return

    print(f"--- Checking raw text from PDF pages {SOLUTION_PAGES_TO_CHECK.start + 1} to {SOLUTION_PAGES_TO_CHECK.stop} ---")
    try:
        with pdfplumber.open(INPUT_PDF_PATH) as pdf:
            for i in SOLUTION_PAGES_TO_CHECK:
                if i < len(pdf.pages):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    print(f"\n--- START OF PAGE {i+1} ---\n")
                    print(text)
                    print(f"\n--- END OF PAGE {i+1} ---")
                else:
                    print(f"Warning: Page {i+1} is out of range.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    verify_format()
