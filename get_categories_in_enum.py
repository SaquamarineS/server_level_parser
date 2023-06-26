import json

# Load the JSON file
with open('dataExample.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create the enum string
enum_str = 'from enum import Enum\n\nclass Keys(Enum):\n    ' + '\n    '.join([k.upper() + ' = "' + k + '"' for k in data.keys()])

# Write the enum string to a file
with open('places_result_categories.py', 'w') as f:
    f.write(enum_str)