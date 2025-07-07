import json
import os
import re
import pdfplumber

# --- CONFIGURATION ---

# 1. Define the exam configuration you want to use.
#    Options: '1101_CORE_1', '1102_CORE_2'
SELECTED_CONFIG = '1102_CORE_2'

# 2. Specify the input PDF file.
INPUT_PDF_PATH = os.path.join(os.path.dirname(__file__), '..', "PDF's", '220-1102_1.pdf')

# 3. Specify the output file for newly extracted, unique questions.
#    The script will not modify your main topic files directly.
STAGING_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1102', 'new_questions_staging.json')

# --- EXAM-SPECIFIC MAPPINGS ---

CONFIGURATIONS = {
    '1101_CORE_1': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1101'),
        'topic_map': {
            1: 'hardware',
            2: 'networking',
            3: 'mobile-devices',
            4: 'troubleshooting',
            5: 'virtualization-cloud',
        },
        'topic_files': [
            'hardware.json',
            'mobile-devices.json',
            'networking.json',
            'troubleshooting.json',
            'virtualization-cloud.json',
            'miscellaneous.json'
        ]
    },
    '1102_CORE_2': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1102'),
        'topic_map': {
            1: 'operating-systems',
            2: 'security',
            3: 'software-troubleshooting',
            4: 'operational-procedures',
        },
        'topic_files': [
            'operating-systems.json',
            'security.json',
            'software-troubleshooting.json',
            'operational-procedures.json',
            'miscellaneous.json'
        ]
    }
}

# --- SCRIPT LOGIC (WORK IN PROGRESS) ---

NEW_QUESTION_RE = re.compile(r'^NEW QUESTION \d+\s*', re.IGNORECASE)

def get_question_signature(question_obj):
    """Creates a unique signature for a question for deduplication."""
    # Remove NEW QUESTION n prefix and normalize
    question_text = question_obj.get("question", "")
    question_text = NEW_QUESTION_RE.sub('', question_text).strip().casefold()
    options = [str(opt).strip().casefold() for opt in question_obj.get("options", [])]
    sorted_options = sorted(options)
    return f"{question_text}|{'|'.join(sorted_options)}"

def load_existing_signatures(config):
    """Loads signatures of all existing questions to avoid duplicates."""
    existing_signatures = set()
    data_dir = config['data_dir']
    topic_files = config['topic_files']

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

def extract_text_from_pdf(pdf_path):
    """Extracts all text from a given PDF file."""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return None

    print(f"Reading text from {pdf_path}...")
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

def parse_questions_from_text(text, pdf_filename):
    """Parses raw text from a PDF to extract structured question objects and stats."""
    print("Parsing text to find question blocks...")

    # Use a robust split based on "NEW QUESTION" which acts as a reliable delimiter.
    # The first item is ignored as it's content before the first question.
    question_blocks = re.split(r'\nNEW QUESTION \d+', text)[1:]
    
    parsed_questions = []
    stats = {
        'total_blocks': len(question_blocks),
        'skipped_missing_answer': 0,
        'skipped_missing_options': 0,
        'skipped_dragdrop_sim_hotspot': 0,
        'skipped_parsing_error': 0
    }
    for i, block in enumerate(question_blocks, 1):
        try:
            # --- Extract individual fields using regex ---
            answer_match = re.search(r'Answer:\s*([A-Z]+)', block, re.IGNORECASE)
            explanation_match = re.search(r'Explanation:(.*)', block, re.DOTALL | re.IGNORECASE)
            explanation = explanation_match.group(1).strip() if explanation_match else ""

            if not answer_match:
                print(f"Warning: Skipping block {i} due to missing answer.")
                stats['skipped_missing_answer'] += 1
                continue

            # --- Isolate the main content (question + options) ---
            # We no longer look for the topic number as it's unreliable
            start_index = 0
            end_index = answer_match.start()
            content_block = block[start_index:end_index].strip()

            # --- Separate Question from Options ---
            # Options are assumed to start with a line beginning with "A."
            options_start_match = re.search(r'\nA\.', content_block)
            if not options_start_match:
                print(f"Warning: Skipping block {i} due to missing options start (A.).")
                stats['skipped_missing_options'] += 1
                continue
            
            # Extract the question text (remove the 'NEW QUESTION #' line)
            question_text = content_block.split('?', 1)[0] + '?'
            # Remove any '-(Topic X)' line that might be present
            question_text = re.sub(r'^\s*-\s*\(Topic\s+\d+\)\s*$', '', question_text, flags=re.MULTILINE).strip()
            # Remove the 'NEW QUESTION #' line
            question_text = re.sub(r'^NEW QUESTION \d+\s*', '', question_text, flags=re.MULTILINE).strip()
            options_block_raw = content_block[options_start_match.start():].strip()

            # Skip DRAG DROP, SIMULATION, and HOTSPOT questions
            if "DRAG DROP" in question_text or "SIMULATION" in question_text or "HOTSPOT" in question_text:
                print(f"Skipping block {i} because it is a DRAG DROP, SIMULATION, or HOTSPOT question")
                stats['skipped_dragdrop_sim_hotspot'] += 1
                continue
            
            # --- Process Options ---
            # Split into a list of options, handling multi-line options
            option_splits = re.split(r'\n(?=[B-Z]\.)', options_block_raw)
            cleaned_options = [
                re.sub(r'^[A-Z]\.\s*', '', opt.replace('\n', ' ').strip()).strip()
                for opt in option_splits
            ]

            # Clean spam from options, question, and explanation
            spam_patterns = [
                re.compile(r'Passing Certification Exams Made Easy visit - https://www\.2PassEasy\.com Welcome to download the Newest 2passeasy 220-1101 dumps https://www\.2passeasy\.com/dumps/220-1101/ \(443 New Questions\)'),
                re.compile(r'Passing Certification Exams Made Easy visit - https://www\.surepassexam\.com Recommend!! Get the Full 220-1101 dumps in VCE and PDF From SurePassExam https://www\.surepassexam\.com/220-1101-exam-dumps\.html \(443 New Questions\)')
            ]
            for pattern in spam_patterns:
                cleaned_options = [pattern.sub('', opt).strip() for opt in cleaned_options]
                question_text = pattern.sub('', question_text).strip()
                explanation = pattern.sub('', explanation).strip()

            # --- Format final object ---
            answer_str = answer_match.group(1)
            correct_indices = [ord(char.upper()) - ord('A') for char in answer_str]

            # Add 'type' field and validate 'correct' indices
            valid_correct = [idx for idx in correct_indices if 0 <= idx < len(cleaned_options)]
            if len(valid_correct) != len(correct_indices):
                print(f"Warning: Adjusted correct indices for question {i} due to out-of-range values.")
            q_type = "single" if len(valid_correct) == 1 else "multiple"
            question_obj = {
                "id": -1, # Will be reassigned later if merged
                "question": question_text,
                "options": cleaned_options,
                "correct": valid_correct,
                "explanation": explanation,
                "source_pdf": os.path.basename(pdf_filename),
                "type": q_type
                # We remove 'source_topic_id' because we'll categorize by content
            }
            parsed_questions.append(question_obj)

        except Exception as e:
            print(f"Error parsing question block {i}. Error: {e}\nBlock content:\n{block[:300]}...")
            stats['skipped_parsing_error'] += 1
            continue

    return parsed_questions, stats

def categorize_question(question_text, explanation):
    """Categorize a question into a domain based on its content."""
    # Combine the question and explanation for better context
    content = (question_text + " " + explanation).lower()
    
    # Define keywords for each domain with weights
    # The weights are arbitrary but help in scoring
    keywords = {
        'hardware': [
            ('ram', 2), ('cpu', 2), ('motherboard', 3), ('hard drive', 2), ('ssd', 2),
            ('power supply', 2), ('gpu', 2), ('cooling', 1), ('desktop', 1), ('printer', 1),
            ('hdd', 3), ('sata', 3), ('nvme', 3), ('raid', 2), ('bios', 2), ('uefi', 2),
            ('peripheral', 1), ('monitor', 1), ('keyboard', 1), ('mouse', 1), ('connector', 3), ('fan', 3), ('battery', 1),
            ('timings',2), ('voltage',2 ), ('safety', 3), ('thermal', 2)
        ],
        'networking': [
            ('router', 2), ('switch', 2), ('firewall', 2), ('wifi', 2), ('ethernet', 2),
            ('tcp/ip', 2), ('dns', 2), ('vpn', 2), ('lan', 2), ('wan', 2), ('port', 1),
            ('ip address', 2), ('subnet', 2), ('gateway', 2), ('dhcp', 2), ('nat', 2),
            ('osi', 2), ('SOHO', 5), ('ping',2 ), ('traffic', 2), ('protocol', 2), ('protocols', 2),
            ('2.4GHz', 6), ('5GHz', 6), ('networking', 5)
            
        ],
        'mobile-devices': [
                        ('laptop', 5), ('tablet', 2), ('smartphone', 5), ('battery', 1), ('touch screen', 1),
            ('mobile device', 5), ('usb-c', 1), ('nfc', 2), ('bluetooth', 1), ('tablet', 1),
            ('ios', 2), ('android', 2), ('wearable', 2), ('mobile os', 2), ('sync', 1),
            ('mobile security', 2), ('face recognition', 2), ('camera', 2), ('calls', 3), 
        ],
        'troubleshooting': [
            ('troubleshoot', 4), ('error', 3), ('fix', 2), ('issue', 4), ('problem', 3),
            ('not working', 2), ('resolve', 2), ('diagnose', 2), ('repair', 2), ('symptom', 2), ('thecnhician', 3),
            ('failure', 2), ('blue screen', 3), ('bsod', 3), ('crash', 2), ('won\'t start', 2),
            ('slow', 2), ('freeze', 2), ('unresponsive', 2), ('bulging', 2), ('report', 2), ('reporting', 2),
            ('discovered', 3), ('standpipe', 3), ('user', 3), ('reports', 3), ('overheating', 3), ('drains', 2),
            ('failing', 2), ('failed', 2), ('replacing', 2), ('latency', 2)
        ],
        'virtualization-cloud': [
            ('virtual', 3), ('vm', 3), ('cloud', 4), ('hypervisor', 3), ('iaas', 2),
            ('paas', 3), ('saas', 3), ('vdi', 2), ('server', 3), ('host', 2),
            ('vmware', 2), ('hyper-v', 2), ('virtualbox', 2), ('aws', 2), ('azure', 2),
            ('gcp', 2), ('private cloud', 2), ('public cloud', 2), ('hybrid cloud', 2), ('web', 2)
        ]
    }
    
    # Initialize scores for each domain
    scores = {domain: 0 for domain in keywords}
    
    # Score the content based on keyword matches
    for domain, terms in keywords.items():
        for (keyword, weight) in terms:
            if keyword in content:
                scores[domain] += weight
    
    # Find the domain with the highest score
    best_domain = max(scores, key=scores.get)
    
    # Only return the best domain if its score is above a threshold
    if scores[best_domain] >= 2:  # At least one significant match
        return best_domain
    else:
        return 'miscellaneous'

def categorize_question_core2(question_text, explanation):
    """Categorize a Core 2 question into a domain based on its content."""
    content = (question_text + " " + explanation).lower()
    keywords = {
        'operating-systems': [
            ('windows', 3), ('macos', 3), ('linux', 3), ('chrome os', 2), ('android', 2), ('ios', 2),
            ('install', 3), ('configure', 2), ('upgrade', 2), ('reimage', 3), ('boot', 2), ('partition', 2),
            ('file system', 2), ('ntfs', 3), ('fat32', 2), ('ext4', 2), ('apfs', 2), ('hfs', 2),
            ('command line', 2), ('cmd', 2), ('powershell', 2), ('terminal', 2), ('command prompt', 2),
            ('msconfig', 2), ('regedit', 3), ('services.msc', 2), ('mmc', 2), ('task manager', 2), 
            ('device manager', 2), ('disk management', 2), ('system restore', 3), ('control panel', 2), 
            ('gpedit', 2), ('gpedit.msc', 3), ('gpmc.msc', 3), ('gpupdate', 2), ('uac', 2),
            ('chkdsk', 3), ('sfc', 3), ('diskpart', 2), ('copy', 1), ('robocopy', 2), ('net use', 2),
            ('virtualization', 3), ('vm', 3), ('hypervisor', 3)
        ],
        'security': [
            ('security', 5), ('malware', 4), ('virus', 4), ('trojan', 3), ('spyware', 3), ('adware', 3),
            ('ransomware', 4), ('rootkit', 4), ('keylogger', 3), ('botnet', 3),
            ('phishing', 3), ('whaling', 3), ('social engineering', 3), ('impersonation', 2),
            ('tailgating', 2), ('dumpster diving', 2), ('shoulder surfing', 2), 
            ('evil twin', 3), ('rogue ap', 3),
            ('firewall', 3), ('antivirus', 3), ('anti-malware', 3), ('ids', 2), ('ips', 2),
            ('authentication', 3), ('mfa', 4), ('biometrics', 2), ('password', 2), ('pin', 2), ('smart card', 2),
            ('access control', 3), ('acl', 2), ('permissions', 2), ('least privilege', 3), ('user accounts', 2),
            ('encryption', 4), ('bitlocker', 3), ('filevault', 2), ('efs', 2), ('full disk encryption', 3), ('vpn', 3),
            ('network security', 2), ('wifi security', 2), ('wpa2', 2), ('wpa3', 2),
            ('physical security', 2), ('badge reader', 2), ('locking', 2),
            ('pki', 2), ('certificate', 2), ('chain of custody', 4), ('data destruction', 3),
            ('shredding', 2), ('degaussing', 2)
        ],
        'software-troubleshooting': [
            ('troubleshoot', 5), ('resolve', 4), ('issue', 3), ('problem', 3), ('error', 3),
            ('application', 3), ('software', 3), ('not working', 2), ('crashes', 3), ('unresponsive', 3),
            ('freeze', 3), ('slow performance', 3), ('low memory', 2),
            ('bsod', 4), ('stop code', 3), ('pop-up', 2), ('browser', 2), ('redirect', 2), ('hijack', 2),
            ('reinstall', 2), ('uninstall', 2), ('update', 2), ('roll back', 2), ('repair', 2),
            ('rebuild profile', 3), ('safe mode', 3), ('compatibility', 2), ('driver', 2),
            ('event viewer', 3), ('log files', 2), ('resource monitor', 2), ('performance monitor', 2),
            ('task manager', 3), ('sfc', 2), ('chkdsk', 2), ('system restore', 2)
        ],
        'operational-procedures': [
            ('professionalism', 3), ('communication', 3), ('customer service', 3),
            ('documentation', 4), ('change management', 4), ('ticketing system', 2),
            ('scope', 2), ('risk', 2), ('rollback', 2),
            ('incident response', 4), ('first responder', 3), ('chain of custody', 4),
            ('licensing', 3), ('eula', 2), ('aup', 2), ('pii', 3), ('gdpr', 2), ('privacy', 3),
            ('safety', 4), ('esd', 3), ('msds', 2), ('grounding', 2), ('disposal', 3), ('recycling', 2),
            ('backup', 3), ('recovery', 3), ('scripting', 2), ('bash', 2),
            ('powershell', 2), ('python', 2),
            ('remote access', 2), ('rdp', 2), ('ssh', 2), ('vnc', 2)
        ]
    }
    scores = {topic: 0 for topic in keywords}
    for topic, phrases in keywords.items():
        for phrase, weight in phrases:
            if phrase in content:
                scores[topic] += weight
    
    if not any(scores.values()):
        return 'miscellaneous'

    best_domain = max(scores, key=scores.get)
    if scores[best_domain] >= 2:
        return best_domain
    else:
        return 'miscellaneous'

def save_new_questions(questions, output_path):
    """Saves the list of new questions to the staging file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2)
        print(f"Successfully saved {len(questions)} new questions to {output_path}")
    except IOError as e:
        print(f"Error saving to staging file: {e}")

def main():
    """Main function to run the importer."""
    print(f"--- Starting PDF Question Importer ---")
    print(f"Using configuration: {SELECTED_CONFIG}")

    config = CONFIGURATIONS.get(SELECTED_CONFIG)
    if not config:
        print(f"Error: Configuration '{SELECTED_CONFIG}' not found.")
        return

    # Determine which categorization function to use based on the selected exam core
    if SELECTED_CONFIG == '1101_CORE_1':
        categorize_func = categorize_question
    elif SELECTED_CONFIG == '1102_CORE_2':
        categorize_func = categorize_question_core2
    else:
        print(f"Error: No categorization function is defined for the configuration '{SELECTED_CONFIG}'.")
        return

    # 1. Load signatures of existing questions for deduplication
    existing_signatures = load_existing_signatures(config)

    # 2. Extract raw text from the source PDF
    raw_text = extract_text_from_pdf(INPUT_PDF_PATH)
    if not raw_text:
        return

    # 3. Parse the text to get question objects
    extracted_questions, stats = parse_questions_from_text(raw_text, INPUT_PDF_PATH)

    # 4. Filter out duplicates and assign topics by content
    new_unique_questions = []
    misc_topic_name = 'miscellaneous'
    skipped_due_to_duplication = 0
    for q in extracted_questions:
        signature = get_question_signature(q)
        if signature not in existing_signatures:
            # Categorize the question based on its content using the selected function
            topic = categorize_func(q['question'], q.get('explanation', ''))
            q['topic'] = topic
            new_unique_questions.append(q)
            existing_signatures.add(signature) # Add to set to dedupe within the same PDF
        else:
            skipped_due_to_duplication += 1

    print(f"\n--- Import Summary ---")
    print(f"Total question blocks found: {stats['total_blocks']}")
    print(f" - Skipped due to missing answer: {stats['skipped_missing_answer']}")
    print(f" - Skipped due to missing options: {stats['skipped_missing_options']}")
    print(f" - Skipped DRAG DROP/SIM/HOTSPOT: {stats['skipped_dragdrop_sim_hotspot']}")
    print(f" - Skipped due to parsing error: {stats['skipped_parsing_error']}")
    print(f" - Skipped due to duplication: {skipped_due_to_duplication}")
    print(f" - New questions saved: {len(new_unique_questions)}")

    # 5. Save the new, unique questions to the staging file
    if new_unique_questions:
        save_new_questions(new_unique_questions, STAGING_OUTPUT_FILE)
    else:
        print("No new questions to save.")

    print("--- Importer finished ---")

if __name__ == "__main__":
    main()
