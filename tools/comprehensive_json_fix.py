#!/usr/bin/env python3
"""
Comprehensive JSON file fixer for security exam questions.
Fixes Unicode characters, unescaped quotes, missing quotes, and control characters.
"""

import json
import re
import sys

def fix_all_json_issues(content):
    """
    Apply all necessary fixes to make JSON valid.
    """
    print("Step 1: Fixing Unicode characters...")
    content = fix_unicode_characters(content)
    
    print("Step 2: Fixing control characters...")
    content = fix_control_characters(content)
    
    print("Step 3: Fixing JSON structure issues...")
    content = fix_json_structure(content)
    
    return content

def fix_unicode_characters(text):
    """Replace problematic Unicode characters."""
    replacements = {
        '\u2011': '-',  # Non-breaking hyphen
        '\u2012': '-',  # Figure dash
        '\u2013': '-',  # En dash (–)
        '\u2014': '-',  # Em dash (—)
        '\u2015': '-',  # Horizontal bar
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u201A': "'",  # Single low-9 quotation mark
        '\u201B': "'",  # Single high-reversed-9 quotation mark
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u201E': '"',  # Double low-9 quotation mark
        '\u2026': '...', # Horizontal ellipsis
        '\u00A0': ' ',  # Non-breaking space
    }
    
    original_length = len(text)
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    if len(text) != original_length:
        print(f"  - Fixed {original_length - len(text)} Unicode characters")
    
    return text

def fix_control_characters(text):
    """Remove or replace invalid control characters."""
    # Remove control characters except for valid JSON whitespace
    cleaned = ""
    removed_count = 0
    
    for char in text:
        # Keep these control characters: tab (\t), newline (\n), carriage return (\r)
        if ord(char) < 32 and char not in ['\t', '\n', '\r']:
            removed_count += 1
            continue
        cleaned += char
    
    if removed_count > 0:
        print(f"  - Removed {removed_count} invalid control characters")
    
    return cleaned

def fix_json_structure(text):
    """Fix JSON structure issues like missing quotes, unescaped quotes."""
    lines = text.split('\n')
    fixed_lines = []
    fixes_made = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Fix explanation lines that have structural issues
        if '"explanation":' in line:
            line = fix_explanation_line(line)
        
        # Fix missing quotes around field names
        line = fix_field_names(line)
        
        # Fix trailing commas and other structural issues
        line = fix_structural_issues(line)
        
        if line != original_line:
            fixes_made += 1
        
        fixed_lines.append(line)
    
    if fixes_made > 0:
        print(f"  - Fixed {fixes_made} JSON structure issues")
    
    return '\n'.join(fixed_lines)

def fix_explanation_line(line):
    """Fix explanation lines with quote and structure issues."""
    if '"explanation":' not in line:
        return line
    
    # Handle the specific pattern we saw: missing closing quote
    if line.count('"') % 2 == 1:  # Odd number of quotes means missing closing quote
        # Check if line ends with comma or other JSON elements
        if re.search(r'[,\s]*$', line):
            # Add missing closing quote before comma/whitespace
            line = re.sub(r'([^"]+)([,\s]*)$', r'\1",\2', line)
    
    # Fix unescaped quotes within the explanation text
    # Pattern: "explanation": "text with "quotes" inside"
    match = re.match(r'^(\s*"explanation":\s*")(.*?)(".*?)$', line)
    if match:
        prefix = match.group(1)
        content = match.group(2)
        suffix = match.group(3)
        
        # Escape any unescaped quotes in the content
        content_fixed = content.replace('"', '\\"')
        line = prefix + content_fixed + suffix
    
    return line

def fix_field_names(line):
    """Fix field names that might be missing quotes."""
    # Fix common patterns like: type": instead of "type":
    line = re.sub(r'\b(\w+)":', r'"\1":', line)
    return line

def fix_structural_issues(line):
    """Fix other structural JSON issues."""
    # Remove duplicate commas
    line = re.sub(r',\s*,', ',', line)
    
    # Fix spacing around colons
    line = re.sub(r'"\s*:\s*', '": ', line)
    
    return line

def validate_and_fix_json(content, max_attempts=3):
    """
    Validate JSON and apply fixes iteratively.
    """
    for attempt in range(max_attempts):
        print(f"\nAttempt {attempt + 1}: Validating JSON...")
        
        try:
            json.loads(content)
            print("SUCCESS: JSON is now valid!")
            return content, True
        
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            
            if attempt < max_attempts - 1:
                print("Applying targeted fix...")
                content = apply_targeted_fix(content, e)
            else:
                print("Max attempts reached. Manual intervention may be needed.")
                return content, False
    
    return content, False

def apply_targeted_fix(content, error):
    """Apply a targeted fix based on the specific JSON error."""
    lines = content.split('\n')
    error_line_num = error.lineno - 1
    
    if error_line_num < len(lines):
        line = lines[error_line_num]
        print(f"Problematic line {error.lineno}: {line.strip()}")
        
        # Common fixes based on error types
        if "Expecting ',' delimiter" in str(error):
            # Usually missing quotes or commas
            if '"explanation":' in line and line.count('"') % 2 == 1:
                lines[error_line_num] = line.rstrip() + '",'
        
        elif "Invalid control character" in str(error):
            # Remove/replace invalid characters
            lines[error_line_num] = ''.join(c for c in line if ord(c) >= 32 or c in '\t\n\r')
        
        elif "Unterminated string" in str(error):
            # Add missing closing quote
            lines[error_line_num] = line.rstrip() + '"'
    
    return '\n'.join(lines)

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python comprehensive_json_fix.py <json_file>")
        return
    
    file_path = sys.argv[1]
    
    try:
        print(f"Processing: {file_path}")
        
        # Read original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup
        backup_path = file_path + '.backup2'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Backup created: {backup_path}")
        
        # Apply fixes
        fixed_content = fix_all_json_issues(original_content)
        
        # Validate and apply additional fixes if needed
        final_content, is_valid = validate_and_fix_json(fixed_content)
        
        if is_valid:
            # Write the fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"SUCCESS: File fixed and saved: {file_path}")
        else:
            print(f"WARNING: Could not fully fix JSON. Check the file manually.")
            print(f"Backup available at: {backup_path}")
    
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
