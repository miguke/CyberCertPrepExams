#!/usr/bin/env python3
import json
import os
import re
import argparse
from difflib import SequenceMatcher
from collections import defaultdict

# Configuration for each exam core
EXAM_CONFIGS = {
    '1101': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1101'),
        'topic_files': [
            "hardware.json", "mobile-devices.json", "networking.json",
            "troubleshooting.json", "virtualization-cloud.json", "miscellaneous.json"
        ]
    },
    '1102': {
        'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data', '1102'),
        'topic_files': [
            "operating-systems.json", "security.json",
            "software-troubleshooting.json", "operational-procedures.json", "miscellaneous.json"
        ]
    }
}

# Regex to strip 'NEW QUESTION n' prefixes and other common prefixes
CLEAN_TEXT_RE = re.compile(r'^NEW QUESTION \d+\s*|^QUESTION \d+\s*', re.IGNORECASE)

# Spam phrases to remove for cleaner comparison
SPAM_PHRASES = [
    'The Leader of IT Certification visit - https://www.certleader.com',
    '100% Valid and Newest Version 220-1102 Questions & Answers shared by Certleader',
    'https://www.certleader.com/220-1102-dumps.html (402 Q&As)'
]

def clean_text(text):
    """Clean question text for comparison by removing spam phrases and normalizing."""
    text = text.strip()
    for phrase in SPAM_PHRASES:
        text = text.replace(phrase, '')
    text = CLEAN_TEXT_RE.sub('', text).strip().casefold()
    return text

def get_similarity(text1, text2):
    """Calculate similarity ratio between two text strings using SequenceMatcher."""
    return SequenceMatcher(None, text1, text2).ratio()

def are_answers_same(q1, q2):
    """Check if two questions have the same correct answers."""
    if not isinstance(q1.get("correct"), list) or not isinstance(q2.get("correct"), list):
        return False
    
    # Make sure both have correct answers arrays with same contents regardless of order
    correct1 = sorted(q1.get("correct", []))
    correct2 = sorted(q2.get("correct", []))
    return correct1 == correct2

def find_similar_questions_within_topic(questions, similarity_threshold=0.9):
    """Find pairs of questions that are similar above the threshold within the same topic."""
    similar_pairs = []
    for i in range(len(questions)):
        q1 = questions[i]
        q1_text = clean_text(q1.get("question", ""))
        
        for j in range(i+1, len(questions)):
            q2 = questions[j]
            q2_text = clean_text(q2.get("question", ""))
            
            # Calculate similarity
            similarity = get_similarity(q1_text, q2_text)
            
            # Check if similarity is above threshold
            if similarity >= similarity_threshold:
                # Check if answers are the same
                same_answers = are_answers_same(q1, q2)
                
                similar_pairs.append({
                    'index1': i,
                    'index2': j,
                    'similarity': similarity,
                    'same_answers': same_answers,
                    'q1_text': q1.get("question", "").strip(),
                    'q2_text': q2.get("question", "").strip(),
                    'q1_correct': q1.get("correct", []),
                    'q2_correct': q2.get("correct", [])
                })
    
    return similar_pairs

def find_similar_questions_across_topics(all_topic_questions, similarity_threshold=0.9):
    """Find pairs of questions that are similar above the threshold across different topics."""
    cross_topic_pairs = []
    
    # Get list of all topics
    topics = list(all_topic_questions.keys())
    
    # Compare questions between different topics
    for i in range(len(topics)):
        topic1 = topics[i]
        questions1 = all_topic_questions[topic1]
        
        for j in range(i+1, len(topics)):
            topic2 = topics[j]
            questions2 = all_topic_questions[topic2]
            
            # Compare each question in topic1 with each question in topic2
            for idx1, q1 in enumerate(questions1):
                q1_text = clean_text(q1.get("question", ""))
                
                for idx2, q2 in enumerate(questions2):
                    q2_text = clean_text(q2.get("question", ""))
                    
                    # Calculate similarity
                    similarity = get_similarity(q1_text, q2_text)
                    
                    # Check if similarity is above threshold
                    if similarity >= similarity_threshold:
                        # Check if answers are the same
                        same_answers = are_answers_same(q1, q2)
                        
                        cross_topic_pairs.append({
                            'topic1': topic1,
                            'topic2': topic2,
                            'file1': f"{topic1}.json",
                            'file2': f"{topic2}.json",
                            'index1': idx1,
                            'index2': idx2,
                            'similarity': similarity,
                            'same_answers': same_answers,
                            'q1_text': q1.get("question", "").strip(),
                            'q2_text': q2.get("question", "").strip(),
                            'q1_correct': q1.get("correct", []),
                            'q2_correct': q2.get("correct", [])
                        })
    
    return cross_topic_pairs

def check_for_select_two(text):
    """Check if the question text contains a 'Select TWO' instruction."""
    return "(Select TWO)" in text

def main():
    parser = argparse.ArgumentParser(description='Find similar questions within and across topic JSON files.')
    parser.add_argument('--files', nargs='+', help='A list of JSON file paths to compare.')
    parser.add_argument('--exam', choices=['1101', '1102'], help='The exam core to check (1101 or 1102). Used if --files is not specified.')
    parser.add_argument('--threshold', type=float, default=0.9, help='Similarity threshold (0.0 to 1.0). Default is 0.9.')
    parser.add_argument('--show-all', action='store_true',
                        help='Show all similar pairs regardless of whether answers match')
    parser.add_argument('--cross-topic-only', action='store_true',
                        help='Only show cross-topic duplicates')
    args = parser.parse_args()

    all_topic_questions = {}
    data_dir = None

    if args.files:
        # Use the directory of the first file as the base for output
        if args.files:
            data_dir = os.path.dirname(args.files[0])

        for filepath in args.files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    filename = os.path.basename(filepath)
                    topic_name = os.path.splitext(filename)[0]
                    all_topic_questions[topic_name] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: File not found, skipping: {filepath}")
                continue
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON, skipping: {filepath}")
                continue
    elif args.exam:
        config = EXAM_CONFIGS[args.exam]
        data_dir = config['data_dir']
        topic_files = config['topic_files']
        for filename in topic_files:
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    topic_name = os.path.splitext(filename)[0]
                    all_topic_questions[topic_name] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: File not found, skipping: {filepath}")
                continue
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON, skipping: {filepath}")
                continue
    else:
        parser.print_help()
        return

    if not all_topic_questions:
        print("Error: No questions loaded. Please check file paths or exam configuration.")
        return

    print(f"Loaded {sum(len(q) for q in all_topic_questions.values())} questions from {len(all_topic_questions)} files.")

    # --- Start of Analysis Logic ---
    within_topic_pairs = []
    cross_topic_pairs = []

    # Find similar questions within each file
    for topic, questions in all_topic_questions.items():
        print(f"Analyzing {topic} for internal duplicates...")
        similar = find_similar_questions_within_topic(questions, args.threshold)
        for pair in similar:
            pair['topic'] = topic
            pair['filename'] = f"{topic}.json"
            within_topic_pairs.append(pair)

    # Find similar questions across different files
    print("\nAnalyzing for cross-file duplicates...")
    cross_topic_pairs = find_similar_questions_across_topics(all_topic_questions, args.threshold)

    # Sort results by similarity (highest first)
    within_topic_pairs.sort(key=lambda x: x['similarity'], reverse=True)
    cross_topic_pairs.sort(key=lambda x: x['similarity'], reverse=True)

    # Display results for within-topic duplicates
    if within_topic_pairs:
        print(f"\nFound {len(within_topic_pairs)} potentially duplicate question pairs WITHIN the same file")
        print("=" * 80)
        for idx, pair in enumerate(within_topic_pairs, 1):
            print(f"Duplicate #{idx} - Similarity: {pair['similarity']*100:.2f}% - Same Answers: {pair['same_answers']}")
            print(f"File: {pair['filename']}")
            print(f"  Q1 (Index {pair['index1']}): {pair['q1_text'][:100]}...")
            print(f"  Q2 (Index {pair['index2']}): {pair['q2_text'][:100]}...")
            print("-" * 80)

    # Display results for cross-topic duplicates
    if cross_topic_pairs:
        print(f"\nFound {len(cross_topic_pairs)} potentially duplicate question pairs ACROSS different files")
        print("=" * 80)
        for idx, pair in enumerate(cross_topic_pairs, 1):
            print(f"Cross-File Duplicate #{idx} - Similarity: {pair['similarity']*100:.2f}% - Same Answers: {pair['same_answers']}")
            print(f"  File 1: {pair['file1']} (Index: {pair['index1']}) | Q: {pair['q1_text'][:80]}...")
            print(f"  File 2: {pair['file2']} (Index: {pair['index2']}) | Q: {pair['q2_text'][:80]}...")
            print("-" * 80)

    if not within_topic_pairs and not cross_topic_pairs:
        print("\nSuccess: No similar questions found with the current threshold.")

    # Save detailed results to a file
    if data_dir:
        results = {
            'threshold': args.threshold,
            'within_file_duplicates': within_topic_pairs,
            'cross_file_duplicates': cross_topic_pairs
        }
        results_file = os.path.join(data_dir, f"duplicate_analysis_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")

if __name__ == '__main__':
    main()
