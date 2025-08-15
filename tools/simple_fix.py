#!/usr/bin/env python3
"""
Simple targeted fix for the specific JSON issues in security-architecture.json
"""

import json
import sys

def fix_specific_issues(content):
    """
    Fix only the specific issues we identified:
    1. En-dash characters (–) to regular dashes (-)
    2. Unescaped quotes within explanation strings
    """
    
    # Step 1: Replace en-dash characters
    print("Fixing en-dash characters...")
    original_content = content
    content = content.replace('\u2013', '-')  # En dash (–) to regular dash
    content = content.replace('\u2011', '-')  # Non-breaking hyphen
    content = content.replace('\u2012', '-')  # Figure dash
    content = content.replace('\u2014', '-')  # Em dash
    content = content.replace('\u2015', '-')  # Horizontal bar
    
    if content != original_content:
        print("  - Fixed dash characters")
    
    # Step 2: Fix the specific quote issue in explanations
    print("Fixing unescaped quotes in explanations...")
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if '"explanation":' in line and '"secured zones"' in line:
            # This is the specific problematic line we identified
            # Replace "secured zones" with \"secured zones\"
            line = line.replace('"secured zones"', '\\"secured zones\\"')
            line = line.replace('"micro‑segments"', '\\"micro-segments\\"')
            print(f"  - Fixed quotes in explanation line")
        
        # Handle other potential quote issues in explanations
        if '"explanation":' in line and line.count('"') > 2:
            # Check if there are unescaped quotes that aren't at string boundaries
            import re
            # Look for pattern: "explanation": "text with "quotes" text"
            match = re.search(r'("explanation":\s*"[^"]*)"([^"]+)"([^"]*")', line)
            if match:
                prefix = match.group(1)
                middle = match.group(2)
                suffix = match.group(3)
                # Escape the middle quotes
                line = prefix + '\\"' + middle + '\\"' + suffix
                print(f"  - Fixed quotes in explanation")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python simple_fix.py <json_file>")
        return
    
    file_path = sys.argv[1]
    
    try:
        print(f"Processing: {file_path}")
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        fixed_content = fix_specific_issues(content)
        
        # Test if it's valid JSON
        try:
            json.loads(fixed_content)
            print("SUCCESS: JSON is valid after fixes")
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"File updated: {file_path}")
            
        except json.JSONDecodeError as e:
            print(f"JSON still has issues: {e}")
            print(f"Error at line {e.lineno}, column {e.colno}")
            
            # Show the problematic area
            lines = fixed_content.split('\n')
            if e.lineno <= len(lines):
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                print("Context around error:")
                for i in range(start, end):
                    marker = " >>> " if i == e.lineno - 1 else "     "
                    print(f"{marker}Line {i+1}: {lines[i]}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
