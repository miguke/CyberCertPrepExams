import json
import os

# Mapping from question ID to target category (topic key)
ID_TO_TOPIC = {
    1: 'hardware',
    2: 'troubleshooting',
    3: 'networking',
    4: 'hardware',
    5: 'troubleshooting',
    6: 'mobile-devices',
    7: 'mobile-devices',
    8: 'mobile-devices',
    9: 'troubleshooting',
    10: 'networking',
    11: 'troubleshooting',
    12: 'mobile-devices',
    13: 'mobile-devices',
    14: 'mobile-devices',
    15: 'hardware',
    16: 'troubleshooting',
    17: 'troubleshooting',
    18: 'mobile-devices',
    19: 'troubleshooting',
    20: 'hardware',
    21: 'troubleshooting',
    22: 'hardware',
    23: 'hardware',
    24: 'hardware',
    25: 'troubleshooting',
    26: 'troubleshooting',
    27: 'networking',
    28: 'networking',
    29: 'troubleshooting',
    30: 'troubleshooting',
    31: 'networking',
    32: 'troubleshooting',
    33: 'troubleshooting',
    34: 'hardware',
    35: 'hardware',
    36: 'troubleshooting',
    37: 'troubleshooting',
    38: 'hardware',
    39: 'troubleshooting',
    40: 'networking',
    41: 'networking',
}

DATA_DIR = os.path.join('..', 'data', '1101')
MISC_PATH = os.path.join(DATA_DIR, 'miscellaneous.json')
CATEGORY_FILES = {
    'hardware': 'hardware.json',
    'networking': 'networking.json',
    'troubleshooting': 'troubleshooting.json',
    'mobile-devices': 'mobile-devices.json',
}

def main():
    # Load miscellaneous questions
    with open(MISC_PATH, encoding='utf-8') as f:
        misc_qs = json.load(f)

    # Load all category files
    category_data = {}
    for cat, fname in CATEGORY_FILES.items():
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                category_data[cat] = json.load(f)
        else:
            category_data[cat] = []

    # Partition misc questions by ID
    to_remove = []
    for q in misc_qs:
        qid = q.get('id')
        target = ID_TO_TOPIC.get(qid)
        if target:
            category_data[target].append(q)
            to_remove.append(q)
            print(f"Moved ID {qid} to {target}")
        else:
            print(f"ID {qid} not mapped, left in miscellaneous.")

    # Remove moved questions from miscellaneous
    misc_qs = [q for q in misc_qs if q not in to_remove]

    # Write updated files
    with open(MISC_PATH, 'w', encoding='utf-8') as f:
        json.dump(misc_qs, f, indent=2, ensure_ascii=False)
    for cat, fname in CATEGORY_FILES.items():
        path = os.path.join(DATA_DIR, fname)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(category_data[cat], f, indent=2, ensure_ascii=False)
    print("All mapped questions moved. Files updated.")

if __name__ == '__main__':
    main()
