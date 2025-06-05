import json
import sys
import os

def minify_json_file(file_path):
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"Error: File {file_path} does not exist or is empty.")
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Use separators=(',', ':') for the most compact representation
            # indent=None is default when separators are specified but explicitly stating it is fine.
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
        
        print(f"Successfully minified {file_path}.")
        return True

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. File may not be valid JSON.")
        return False
    except Exception as e:
        print(f"An error occurred while minifying {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python minify_json.py <file_path>")
        sys.exit(1)
    
    file_path_arg = sys.argv[1]
    
    if not minify_json_file(file_path_arg):
        sys.exit(1)
