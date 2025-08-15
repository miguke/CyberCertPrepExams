#!/usr/bin/env python3
"""
Script to fix Unicode character issues in JSON files that prevent proper parsing.
Specifically targets en-dash characters and other problematic Unicode characters.
"""

import json
import sys
import os

def clean_unicode_characters(text):
    """
    Replace problematic Unicode characters with standard ASCII equivalents.
    """
    # Dictionary of Unicode characters to replace
    replacements = {
        '\u2011': '-',  # Non-breaking hyphen
        '\u2012': '-',  # Figure dash
        '\u2013': '-',  # En dash (–)
        '\u2014': '-',  # Em dash (—)
        '\u2015': '-',  # Horizontal bar
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark (smart apostrophe)
        '\u201A': "'",  # Single low-9 quotation mark
        '\u201B': "'",  # Single high-reversed-9 quotation mark
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u201E': '"',  # Double low-9 quotation mark
        '\u2026': '...', # Horizontal ellipsis
        '\u00A0': ' ',  # Non-breaking space
    }
    
    # Apply replacements
    cleaned_text = text
    for unicode_char, replacement in replacements.items():
        cleaned_text = cleaned_text.replace(unicode_char, replacement)
    
    return cleaned_text

def fix_json_quotes(text):
    """
    Fix unescaped quotes within JSON string values.
    This is a targeted fix for the specific issue found.
    """
    import re
    
    # Pattern to find JSON string values that contain unescaped quotes
    # This looks for "key": "value with "unescaped quotes" inside"
    pattern = r'("explanation":\s*"[^"]*)"([^"]*)"([^"]*")'
    
    def replace_quotes(match):
        prefix = match.group(1)  # "explanation": "text before
        middle = match.group(2)  # text inside quotes
        suffix = match.group(3)  # text after"
        
        # Replace the inner quotes with escaped quotes or alternative
        middle_fixed = middle.replace('"', '\\"')
        return prefix + middle_fixed + suffix
    
    # Apply the fix
    fixed_text = re.sub(pattern, replace_quotes, text)
    
    # Also handle any remaining quote issues in explanations
    lines = fixed_text.split('\n')
    fixed_lines = []
    
    for line in lines:
        if '"explanation":' in line:
            # Look for patterns like: "secured zones" within the explanation
            # Replace them with: \"secured zones\"
            if line.count('"') > 2:  # More than just the key and value quotes
                # Find the explanation content
                parts = line.split('"explanation":', 1)
                if len(parts) == 2:
                    prefix = parts[0] + '"explanation":'
                    explanation_part = parts[1]
                    
                    # Fix quotes within the explanation value
                    # Look for the pattern: "text with "quotes" inside",
                    match = re.search(r'^\s*"([^"]*"[^"]*"[^"]*)",?\s*$', explanation_part)
                    if match:
                        content = match.group(1)
                        # Replace internal quotes with escaped quotes
                        fixed_content = re.sub(r'(?<!\\)"(?!$)', '\\"', content)
                        # Reconstruct the line
                        line = prefix + ' "' + fixed_content + '"' + explanation_part[match.end()-1:]
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_json_file(file_path):
    """
    Fix Unicode character issues in a JSON file.
    """
    print(f"Processing: {file_path}")
    
    # Create backup
    backup_path = file_path + '.backup'
    
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Backup created: {backup_path}")
        
        # Clean the content - first Unicode, then quotes
        cleaned_content = clean_unicode_characters(original_content)
        cleaned_content = fix_json_quotes(cleaned_content)
        
        # Verify it's valid JSON
        try:
            json.loads(cleaned_content)
            print("SUCCESS: Cleaned content is valid JSON")
        except json.JSONDecodeError as e:
            print(f"ERROR: Cleaned content is not valid JSON: {e}")
            print("Attempting to identify and fix the JSON structure issue...")
            
            # Try to identify the issue around the error location
            lines = cleaned_content.split('\n')
            error_line = e.lineno - 1 if e.lineno <= len(lines) else len(lines) - 1
            
            print(f"Error near line {e.lineno}:")
            start_line = max(0, error_line - 2)
            end_line = min(len(lines), error_line + 3)
            
            for i in range(start_line, end_line):
                marker = " >>> " if i == error_line else "     "
                print(f"{marker}Line {i+1}: {lines[i]}")
            
            return False
        
        # Write the cleaned file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"SUCCESS: File successfully cleaned: {file_path}")
        
        # Show what was changed
        if original_content != cleaned_content:
            print("Changes made:")
            lines_original = original_content.split('\n')
            lines_cleaned = cleaned_content.split('\n')
            
            changes_count = 0
            for i, (orig, clean) in enumerate(zip(lines_original, lines_cleaned)):
                if orig != clean:
                    changes_count += 1
                    if changes_count <= 5:  # Show first 5 changes
                        print(f"  Line {i+1}: {repr(orig)} -> {repr(clean)}")
            
            if changes_count > 5:
                print(f"  ... and {changes_count - 5} more changes")
            print(f"Total lines changed: {changes_count}")
        else:
            print("No changes needed - file was already clean")
        
        return True
        
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return False
    except Exception as e:
        print(f"ERROR: Error processing file: {e}")
        return False

def main():
    """Main function to process command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python fix_unicode_chars.py <json_file_path> [additional_files...]")
        print("Example: python fix_unicode_chars.py security-architecture.json")
        return
    
    success_count = 0
    total_files = len(sys.argv) - 1
    
    for file_path in sys.argv[1:]:
        if fix_json_file(file_path):
            success_count += 1
        print("-" * 50)
    
    print(f"Summary: {success_count}/{total_files} files processed successfully")

if __name__ == "__main__":
    main()
