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
    parser = argparse.ArgumentParser(description='Find similar questions within and across topic files that may be duplicates.')
    parser.add_argument('exam', choices=['1101', '1102'], nargs='?', default='1101', 
                        help='The exam core to check (1101 or 1102). Defaults to 1101.')
    parser.add_argument('--threshold', type=float, default=0.9, 
                        help='Similarity threshold (0.0-1.0). Default is 0.9 (90%)')
    parser.add_argument('--show-all', action='store_true',
                        help='Show all similar pairs regardless of whether answers match')
    parser.add_argument('--cross-topic-only', action='store_true',
                        help='Only show cross-topic duplicates')
    args = parser.parse_args()
    
    config = EXAM_CONFIGS[args.exam]
    data_dir = config['data_dir']
    
    print(f"--- Finding Similar Questions in Exam {args.exam} with {args.threshold*100:.0f}% Similarity Threshold ---")
    
    within_topic_pairs = []
    cross_topic_pairs = []
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
                if not args.cross_topic_only:
                    print(f"Analyzing {topic}...")
                    similar = find_similar_questions_within_topic(questions, args.threshold)
                    
                    for pair in similar:
                        pair['topic'] = topic
                        pair['filename'] = filename
                        within_topic_pairs.append(pair)
        except json.JSONDecodeError:
            print(f"Error: Could not decode {filename}. Skipping.")
    
    # Find similar questions across different topic files
    print("\nLooking for cross-topic duplicates...")
    cross_topic_pairs = find_similar_questions_across_topics(topic_questions, args.threshold)
    
    # Sort results by similarity (highest first)
    within_topic_pairs.sort(key=lambda x: x['similarity'], reverse=True)
    cross_topic_pairs.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Filter by same answers if needed
    if not args.show_all:
        within_topic_pairs = [p for p in within_topic_pairs if p['same_answers']]
        cross_topic_pairs = [p for p in cross_topic_pairs if p['same_answers']]
    
    # Display results for within-topic duplicates
    if within_topic_pairs and not args.cross_topic_only:
        print(f"\nFound {len(within_topic_pairs)} potentially duplicate question pairs WITHIN the same topic")
        print("=" * 80)
        
        for idx, pair in enumerate(within_topic_pairs, 1):
            select_two1 = check_for_select_two(pair['q1_text'])
            select_two2 = check_for_select_two(pair['q2_text'])
            
            print(f"Duplicate #{idx} - Similarity: {pair['similarity']*100:.2f}%, "
                  f"Same Answers: {'YES' if pair['same_answers'] else 'NO'}")
            print(f"Topic: {pair['topic']} (File: {pair['filename']})")
            print(f"Q1 (Index {pair['index1']}): {pair['q1_text'][:100]}{'...' if len(pair['q1_text']) > 100 else ''}")
            print(f"Q1 Contains 'Select TWO': {'YES' if select_two1 else 'NO'}")
            print(f"Q2 (Index {pair['index2']}): {pair['q2_text'][:100]}{'...' if len(pair['q2_text']) > 100 else ''}")
            print(f"Q2 Contains 'Select TWO': {'YES' if select_two2 else 'NO'}")
            print(f"Q1 Answers: {pair['q1_correct']}")
            print(f"Q2 Answers: {pair['q2_correct']}")
            print("-" * 80)
        
        # Summary of within-topic duplicates
        print("\nWithin-Topic Summary:")
        by_topic = defaultdict(int)
        for pair in within_topic_pairs:
            by_topic[pair['topic']] += 1
        
        for topic, count in by_topic.items():
            print(f"- {topic}: {count} potential duplicates")
    
    # Display results for cross-topic duplicates
    if cross_topic_pairs:
        print(f"\nFound {len(cross_topic_pairs)} potentially duplicate question pairs ACROSS different topics")
        print("=" * 80)
        
        for idx, pair in enumerate(cross_topic_pairs, 1):
            select_two1 = check_for_select_two(pair['q1_text'])
            select_two2 = check_for_select_two(pair['q2_text'])
            
            print(f"Cross-Topic Duplicate #{idx} - Similarity: {pair['similarity']*100:.2f}%, "
                  f"Same Answers: {'YES' if pair['same_answers'] else 'NO'}")
            print(f"Topic 1: {pair['topic1']} (File: {pair['file1']}, Index: {pair['index1']})")
            print(f"Topic 2: {pair['topic2']} (File: {pair['file2']}, Index: {pair['index2']})")
            print(f"Q1: {pair['q1_text'][:100]}{'...' if len(pair['q1_text']) > 100 else ''}")
            print(f"Q1 Contains 'Select TWO': {'YES' if select_two1 else 'NO'}")
            print(f"Q2: {pair['q2_text'][:100]}{'...' if len(pair['q2_text']) > 100 else ''}")
            print(f"Q2 Contains 'Select TWO': {'YES' if select_two2 else 'NO'}")
            print(f"Q1 Answers: {pair['q1_correct']}")
            print(f"Q2 Answers: {pair['q2_correct']}")
            print("-" * 80)
        
        # Summary of cross-topic duplicates
        print("\nCross-Topic Summary:")
        by_topic_pair = defaultdict(int)
        for pair in cross_topic_pairs:
            topic_key = f"{pair['topic1']}-{pair['topic2']}"
            by_topic_pair[topic_key] += 1
        
        for topic_pair, count in by_topic_pair.items():
            print(f"- {topic_pair}: {count} potential duplicates")
    
    # If no duplicates found
    if not within_topic_pairs and not cross_topic_pairs:
        print("\nSuccess: No similar questions found with the current threshold.")
    
    # Save results to files
    results = {
        'threshold': args.threshold,
        'within_topic': {
            'total_pairs': len(within_topic_pairs),
            'pairs': within_topic_pairs
        },
        'cross_topic': {
            'total_pairs': len(cross_topic_pairs),
            'pairs': cross_topic_pairs
        }
    }
    
    results_file = os.path.join(data_dir, f"duplicate_analysis_enhanced_{args.threshold:.1f}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Additional recommendation for users
    if within_topic_pairs or cross_topic_pairs:
        print("\nRecommendation: ")
        print("1. Run 'python clean_duplicate_questions.py' to automatically clean within-topic duplicates")
        print("2. Review cross-topic duplicates manually to decide which topic is most appropriate")

if __name__ == '__main__':
    main()
