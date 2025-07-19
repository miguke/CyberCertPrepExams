#!/usr/bin/env python3
"""
TXT Parser for CompTIA A+ 220-1102 v2 Real Exam Questions
Parses TXT files to populate 1102_v2 JSON topic files
"""

import json
import os
import re
from datetime import datetime

# Configuration
MAIN_QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1102_v2', '220-1102_en_RealDeal_compressed.txt')
ANSWER_KEY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', '1102_v2', 'real deal fixed questions .txt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '1102_v2')

# Questions to ignore completely
IGNORE_QUESTION_IDS = {1, 9, 187, 189, 199, 423, 435, 436, 485, 534, 586}

# Topic mapping based on content keywords
TOPIC_KEYWORDS = {
    'operating-systems': [
        'windows', 'linux', 'macos', 'ubuntu', 'boot', 'registry', 'file system', 'ntfs', 'fat32',
        'command prompt', 'powershell', 'terminal', 'bash', 'sudo', 'chmod', 'chown', 'ls', 'dir',
        'task manager', 'services', 'msconfig', 'regedit', 'control panel', 'system configuration',
        'device manager', 'disk management', 'event viewer', 'performance monitor', 'resource monitor',
        'startup', 'shutdown', 'hibernate', 'sleep', 'user account', 'group policy', 'active directory',
        'domain', 'workgroup', 'local account', 'microsoft account', 'administrator', 'standard user',
        'power user', 'guest account', 'uac', 'user access control', 'permissions', 'ntfs permissions',
        'share permissions', 'inheritance', 'ownership', 'security tab', 'properties'
    ],
    'security': [
        'malware', 'virus', 'trojan', 'ransomware', 'spyware', 'adware', 'rootkit', 'keylogger',
        'phishing', 'social engineering', 'shoulder surfing', 'tailgating', 'dumpster diving',
        'firewall', 'antivirus', 'anti-malware', 'windows defender', 'encryption', 'bitlocker',
        'vpn', 'ssl', 'tls', 'https', 'certificate', 'digital signature', 'hash', 'md5', 'sha',
        'password', 'authentication', 'authorization', 'multifactor', 'biometric', 'smart card',
        'token', 'kerberos', 'ldap', 'radius', 'tacacs', 'single sign-on', 'sso',
        'access control', 'principle of least privilege', 'role-based access', 'mandatory access',
        'discretionary access', 'security policy', 'incident response', 'forensics', 'chain of custody',
        'penetration testing', 'vulnerability assessment', 'security audit', 'compliance'
    ],
    'software-troubleshooting': [
        'application', 'software', 'program', 'install', 'uninstall', 'update', 'patch', 'upgrade',
        'compatibility', 'dependency', 'dll', 'driver', 'blue screen', 'bsod', 'crash', 'freeze',
        'hang', 'slow performance', 'memory leak', 'cpu usage', 'disk usage', 'network usage',
        'error message', 'exception', 'log file', 'event log', 'system log', 'application log',
        'security log', 'debug', 'troubleshoot', 'diagnostic', 'repair', 'restore', 'backup',
        'system restore', 'recovery', 'safe mode', 'msconfig', 'clean boot', 'selective startup',
        'startup repair', 'system file checker', 'sfc', 'dism', 'chkdsk', 'defrag', 'disk cleanup',
        'registry cleaner', 'temp files', 'cache', 'cookies', 'browser', 'internet explorer',
        'chrome', 'firefox', 'edge', 'safari', 'add-on', 'extension', 'plugin', 'java', 'flash'
    ],
    'operational-procedures': [
        'documentation', 'procedure', 'policy', 'standard', 'guideline', 'best practice',
        'change management', 'change control', 'change request', 'approval', 'rollback',
        'incident management', 'problem management', 'service desk', 'help desk', 'ticket',
        'escalation', 'sla', 'service level agreement', 'kpi', 'key performance indicator',
        'communication', 'customer service', 'professionalism', 'ethics', 'confidentiality',
        'privacy', 'data protection', 'gdpr', 'hipaa', 'sox', 'compliance', 'audit',
        'safety', 'esd', 'electrostatic discharge', 'grounding', 'anti-static', 'msds',
        'material safety data sheet', 'hazardous material', 'disposal', 'recycling',
        'environmental', 'green it', 'power management', 'energy efficiency', 'carbon footprint',
        'backup', 'disaster recovery', 'business continuity', 'risk assessment', 'risk management',
        'asset management', 'inventory', 'licensing', 'software licensing', 'volume licensing'
    ]
}

def clean_text(text):
    """Clean text by removing specified phrases and normalizing"""
    if not text:
        return ""
    
    # Remove specified spam phrases
    text = re.sub(r'https://VirtuLearner\.com\s*\d*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'220-1102|220\s+1102', '', text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def parse_answer_key(file_path):
    """Parse the answer key file to get corrected answers"""
    answer_corrections = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # More flexible pattern to match various formats in the file
        # Pattern 1: Q[number] – Provided Answer(s): [letter] – By Study Guide should be answer [letter]
        pattern1 = r'Q(\d+)\s*[–-]\s*Provided Answer\(s\):\s*([A-F,\s]+)\s*[–-]\s*By Study Guide should be answer\s*([A-F,\s]+)'
        
        # Pattern 2: Q[number] – Provided Answer(s): [letter] – By Study Guide should be
        pattern2 = r'Q(\d+)\s*[–-]\s*Provided Answer\(s\):\s*([A-F,\s]+)\s*[–-]\s*By Study Guide should be\s*([A-F,\s]*?)(?=\s*Rationale|\n|$)'
        
        all_matches = []
        all_matches.extend(re.findall(pattern1, content, re.IGNORECASE | re.MULTILINE))
        all_matches.extend(re.findall(pattern2, content, re.IGNORECASE | re.MULTILINE))
        
        # Remove duplicates based on question ID
        seen_questions = set()
        unique_matches = []
        for match in all_matches:
            question_id = int(match[0])
            if question_id not in seen_questions:
                unique_matches.append(match)
                seen_questions.add(question_id)
        
        for match in unique_matches:
            question_id = int(match[0])
            if len(match) >= 3 and match[2].strip():  # Ensure we have a correction
                correct_answer = match[2].strip().replace(',', '').replace(' ', '')
                
                # Convert letter(s) to index(es)
                correct_indices = []
                for letter in correct_answer:
                    if letter.upper() in 'ABCDEF':
                        correct_indices.append(ord(letter.upper()) - ord('A'))
                
                if correct_indices:
                    answer_corrections[question_id] = correct_indices
                    print(f"Applied correction for Q{question_id}: {correct_answer}")
        
        print(f"Loaded {len(answer_corrections)} answer corrections from answer key")
        return answer_corrections
        
    except Exception as e:
        print(f"Error parsing answer key: {e}")
        return {}

def assign_topic(question_text, options_text, explanation_text=""):
    """Assign a topic based on content analysis with improved weighting"""
    full_text = f"{question_text} {options_text} {explanation_text}".lower()
    
    # Priority keywords that strongly indicate specific topics
    priority_indicators = {
        'operational-procedures': [
            'change management', 'change request', 'change control', 'change advisory board',
            'incident management', 'service desk', 'help desk', 'ticket', 'escalation',
            'documentation', 'procedure', 'policy', 'best practice', 'compliance',
            'safety', 'esd', 'electrostatic discharge', 'disposal', 'recycling',
            'backup', 'disaster recovery', 'business continuity', 'risk assessment',
            'asset management', 'inventory', 'licensing', 'communication', 'professionalism',
            'customer service', 'privacy', 'confidentiality', 'data protection'
        ],
        'security': [
            'malware', 'virus', 'trojan', 'ransomware', 'spyware', 'adware', 'rootkit',
            'phishing', 'social engineering', 'encryption', 'bitlocker', 'vpn',
            'firewall', 'antivirus', 'authentication', 'authorization', 'multifactor',
            'biometric', 'certificate', 'digital signature', 'hash', 'penetration testing',
            'vulnerability', 'security audit', 'access control', 'principle of least privilege'
        ],
        'software-troubleshooting': [
            'application crash', 'software crash', 'program crash', 'blue screen', 'bsod',
            'slow performance', 'memory leak', 'error message', 'troubleshoot', 'diagnostic',
            'system restore', 'safe mode', 'system file checker', 'sfc', 'chkdsk',
            'browser', 'add-on', 'extension', 'plugin', 'compatibility', 'driver issue'
        ],
        'operating-systems': [
            'windows 10', 'windows 11', 'linux', 'macos', 'ubuntu', 'file system',
            'registry', 'group policy', 'active directory', 'domain join',
            'user account', 'administrator', 'permissions', 'device manager'
        ]
    }
    
    topic_scores = {}
    
    # First pass: Check for priority indicators (weighted heavily)
    for topic, priority_keywords in priority_indicators.items():
        score = 0
        for keyword in priority_keywords:
            if keyword in full_text:
                score += 10  # High weight for priority keywords
        topic_scores[topic] = score
    
    # Second pass: Add regular keyword scores
    for topic, keywords in TOPIC_KEYWORDS.items():
        if topic not in topic_scores:
            topic_scores[topic] = 0
            
        for keyword in keywords:
            if keyword.lower() in full_text:
                # Weight based on keyword specificity
                weight = len(keyword.split()) + 1
                topic_scores[topic] += weight
    
    # Special rules to prevent over-assignment to operating-systems
    if topic_scores.get('operating-systems', 0) > 0:
        # Reduce OS score if other topics also have significant scores
        other_max = max([score for topic, score in topic_scores.items() if topic != 'operating-systems'], default=0)
        if other_max >= topic_scores['operating-systems'] * 0.7:
            topic_scores['operating-systems'] *= 0.5
    
    # Return the topic with the highest score
    if not topic_scores or max(topic_scores.values()) == 0:
        return 'operational-procedures'  # Default to operational procedures instead of OS
    
    return max(topic_scores, key=topic_scores.get)

def parse_questions_file(file_path, answer_corrections):
    """Parse the main questions file"""
    questions_by_topic = {
        'operating-systems': [],
        'security': [],
        'software-troubleshooting': [],
        'operational-procedures': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match questions: QUESTION: [number] ... Answer(s): [letter]
        question_pattern = r'QUESTION:\s*(\d+)\s*(.*?)(?=QUESTION:\s*\d+|$)'
        
        questions = re.findall(question_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for question_match in questions:
            question_id = int(question_match[0])
            question_block = question_match[1].strip()
            
            # Skip ignored questions
            if question_id in IGNORE_QUESTION_IDS:
                print(f"Skipping ignored question ID: {question_id}")
                continue
            
            # Extract answer from the block
            answer_match = re.search(r'Answer\(s\):\s*([A-F,\s]+)', question_block, re.IGNORECASE)
            if answer_match:
                # Remove the answer line and everything after it (including explanations)
                answer_pos = answer_match.start()
                question_block = question_block[:answer_pos].strip()
            
            # Clean the question block
            question_block = clean_text(question_block)
            
            if not question_block:
                continue
            
            # Split into question text and options
            # First, find where options start by looking for the first "A."
            option_start_match = re.search(r'\b[A-F]\.', question_block)
            if not option_start_match:
                print(f"No options found for question {question_id}, skipping")
                continue
            
            option_start_pos = option_start_match.start()
            question_text = question_block[:option_start_pos].strip()
            options_section = question_block[option_start_pos:].strip()
            
            # Extract all options using a more robust pattern
            # This pattern looks for letter followed by period, then captures everything until the next letter+period or end
            options_pattern = r'([A-F])\. (.*?)(?=\s*[A-F]\.|$)'
            options_matches = re.findall(options_pattern, options_section, re.DOTALL)
            
            if not options_matches:
                print(f"No options found for question {question_id}, skipping")
                continue
            
            # Build options list - ensure we have at least A, B, C, D
            options = []
            options_text = ""
            expected_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            
            # Create a dictionary to store options by letter
            options_dict = {}
            for letter, option_text in options_matches:
                # Clean up the option text - remove extra whitespace and newlines
                clean_option = re.sub(r'\s+', ' ', option_text.strip())
                clean_option = clean_text(clean_option)
                if clean_option:
                    options_dict[letter] = clean_option
            
            # Build the final options list in order (A, B, C, D, E, F)
            for letter in expected_letters:
                if letter in options_dict:
                    options.append(options_dict[letter])
                    options_text += f" {options_dict[letter]}"
                else:
                    break  # Stop when we reach a missing letter
            
            if len(options) < 4:
                print(f"Insufficient options for question {question_id} (found {len(options)}, need at least 4), skipping")
                continue
            
            # Determine correct answer
            correct_indices = []
            if question_id in answer_corrections:
                correct_indices = answer_corrections[question_id]
            elif answer_match:
                # Parse original answer
                original_answer = answer_match.group(1).strip().replace(',', '').replace(' ', '')
                for letter in original_answer:
                    if letter.upper() in 'ABCDEF':
                        idx = ord(letter.upper()) - ord('A')
                        if idx < len(options):
                            correct_indices.append(idx)
            
            if not correct_indices:
                print(f"No correct answer found for question {question_id}, skipping")
                continue
            
            # Assign topic
            topic = assign_topic(question_text, options_text)
            
            # Create question object
            question_obj = {
                "id": question_id,
                "question": clean_text(question_text),
                "options": options,
                "correct": correct_indices,
                "explanation": "",  # No explanations in the source file
                "source_pdf": "220-1102_en_RealDeal_compressed.txt",
                "type": "multiple" if len(correct_indices) > 1 else "single",
                "topic": topic
            }
            
            questions_by_topic[topic].append(question_obj)
            print(f"Processed question {question_id} -> {topic}")
        
        return questions_by_topic
        
    except Exception as e:
        print(f"Error parsing questions file: {e}")
        return questions_by_topic

def save_topic_files(questions_by_topic, output_dir):
    """Save questions to topic JSON files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for topic, questions in questions_by_topic.items():
        if not questions:
            print(f"No questions found for topic: {topic}")
            continue
        
        # Sort questions by ID and reassign sequential IDs
        questions.sort(key=lambda x: x['id'])
        for i, question in enumerate(questions, 1):
            question['id'] = i
        
        # Create backup of existing file if it exists
        topic_file = os.path.join(output_dir, f"{topic}.json")
        if os.path.exists(topic_file):
            backup_file = os.path.join(output_dir, 'backups', f"{topic}_{timestamp}.json")
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            with open(topic_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            print(f"Backup created: {backup_file}")
        
        # Save new questions
        with open(topic_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(questions)} questions to {topic}.json")

def main():
    """Main execution function"""
    print("Starting TXT parsing for 1102_v2...")
    
    # Parse answer key
    print("Parsing answer key...")
    answer_corrections = parse_answer_key(ANSWER_KEY_FILE)
    
    # Parse main questions file
    print("Parsing main questions file...")
    questions_by_topic = parse_questions_file(MAIN_QUESTIONS_FILE, answer_corrections)
    
    # Print summary
    total_questions = sum(len(questions) for questions in questions_by_topic.values())
    print(f"\nParsing Summary:")
    print(f"Total questions processed: {total_questions}")
    for topic, questions in questions_by_topic.items():
        print(f"  {topic}: {len(questions)} questions")
    
    # Save to files
    print("\nSaving to topic files...")
    save_topic_files(questions_by_topic, OUTPUT_DIR)
    
    print("\nTXT parsing completed successfully!")

if __name__ == '__main__':
    main()
