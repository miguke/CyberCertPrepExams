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

def find_similar_questions(questions, similarity_threshold=0.9):
    """Find pairs of questions that are similar above the threshold."""
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

def main():
    parser = argparse.ArgumentParser(description='Find similar questions within topic files that may be duplicates.')
    parser.add_argument('exam', choices=['1101', '1102'], nargs='?', default='1101', 
                        help='The exam core to check (1101 or 1102). Defaults to 1101.')
    parser.add_argument('--threshold', type=float, default=0.9, 
                        help='Similarity threshold (0.0-1.0). Default is 0.9 (90%)')
    parser.add_argument('--show-all', action='store_true',
                        help='Show all similar pairs regardless of whether answers match')
    args = parser.parse_args()
    
    config = EXAM_CONFIGS[args.exam]
    data_dir = config['data_dir']
    
    print(f"--- Finding Similar Questions in Exam {args.exam} with {args.threshold*100:.0f}% Similarity Threshold ---")
    
    all_similar_pairs = []
    topic_questions = {}
    
    # Load questions from each topic file
    for filename in config['topic_files']:
        filepath = os.path.join(data_dir, filename)
        topic = filename.replace('.json', '')
        
        if not os.path.exists(filepath):
            print(f"Warning: File {filename} not found. Skipping.")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                questions = json.loads(content) if content.strip() else []
                print(f"Loaded {len(questions)} questions from {filename}")
                
                # Store questions for cross-topic analysis
                topic_questions[topic] = questions
                
                # Find similar questions within this topic file
                print(f"Analyzing {topic}...")
                similar = find_similar_questions(questions, args.threshold)
                
                for pair in similar:
                    pair['topic'] = topic
                    pair['filename'] = filename
                    all_similar_pairs.append(pair)
        except json.JSONDecodeError:
            print(f"Error: Could not decode {filename}. Skipping.")
    
    # Sort results by similarity (highest first)
    all_similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Filter by same answers if needed
    if not args.show_all:
        filtered_pairs = [p for p in all_similar_pairs if p['same_answers']]
    else:
        filtered_pairs = all_similar_pairs
    
    # Display results
    if filtered_pairs:
        print(f"\nFound {len(filtered_pairs)} potentially duplicate question pairs")
        print("=" * 80)
        
        for idx, pair in enumerate(filtered_pairs, 1):
            print(f"Duplicate #{idx} - Similarity: {pair['similarity']*100:.2f}%, "
                  f"Same Answers: {'YES' if pair['same_answers'] else 'NO'}")
            print(f"Topic: {pair['topic']} (File: {pair['filename']})")
            print(f"Question 1 (Index {pair['index1']}): {pair['q1_text'][:100]}...")
            print(f"Question 2 (Index {pair['index2']}): {pair['q2_text'][:100]}...")
            print(f"Q1 Answers: {pair['q1_correct']}")
            print(f"Q2 Answers: {pair['q2_correct']}")
            print("-" * 80)
            
        print("\nSummary:")
        by_topic = defaultdict(int)
        for pair in filtered_pairs:
            by_topic[pair['topic']] += 1
        
        for topic, count in by_topic.items():
            print(f"- {topic}: {count} potential duplicates")
        
        print("\nRecommendation: Review these question pairs and consider removing duplicates.")
    else:
        print("\nSuccess: No similar questions found with the current threshold.")
    
    # Optional: Save results to a file
    results_file = os.path.join(data_dir, f"duplicate_analysis_{args.threshold:.1f}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'threshold': args.threshold,
            'total_pairs': len(filtered_pairs),
            'pairs': filtered_pairs
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == '__main__':
    main()
