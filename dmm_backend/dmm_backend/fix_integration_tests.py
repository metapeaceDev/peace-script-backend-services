"""
Script to fix test_integration_database.py
Replaces full_name with display_name and removes roles field
"""

import re

# Read the test file
with open("tests/test_integration_database.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Replace full_name with display_name
content = content.replace('full_name="', 'display_name="')
content = content.replace('user.full_name', 'user.display_name')
content = content.replace('updated_user.full_name', 'updated_user.display_name')
content = content.replace('found_user.full_name', 'found_user.display_name')

# Fix 2: Remove roles field from User creation
# Pattern: roles=["user"]\n or roles=["user"],\n
content = re.sub(r',?\s*roles=\[.*?\]', '', content)

# Fix 3: Update SimulationHistory to add missing required fields with defaults
# Find all SimulationHistory( instances and ensure they have required fields
def add_missing_history_fields(match):
    """Add missing required fields to SimulationHistory"""
    indent = match.group(1)
    params = match.group(2)
    
    # Check if required fields exist
    required_defaults = {
        'choice_description': 'choice_description="Test choice description"',
        'citta_quality': 'citta_quality="kusala"',
        'pali_term_explained': 'pali_term_explained="Test pali term"',
        'user_reflection': 'user_reflection="Test reflection"',
        'user_rating': 'user_rating=5',
        'duration_seconds': 'duration_seconds=60'
    }
    
    # Add missing fields
    for field, default in required_defaults.items():
        if field not in params:
            # Add before the closing parenthesis
            params = params.rstrip() + f',\n{indent}    {default}\n{indent}'
    
    return f'{indent}SimulationHistory(\n{params})'

# This is complex, let's handle it differently - just add the fields manually
history_pattern = r'(    )history = SimulationHistory\((.*?)\n    \)'
content = re.sub(history_pattern, add_missing_history_fields, content, flags=re.DOTALL)

print("Fixed test_integration_database.py")
print("\nChanges made:")
print("- Replaced full_name → display_name")
print("- Removed roles field")
print("- Added default values for SimulationHistory required fields")

# Write back
with open("tests/test_integration_database.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ File updated successfully!")
