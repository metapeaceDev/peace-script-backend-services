#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('routers/narrative_projects.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Ollama parameters - BOTH occurrences
old_params = '''                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 8000  # Increase max tokens for longer beats
                }'''

new_params = '''                "options": {
                    "temperature": 1.0,  # Increase for more creative, longer output
                    "top_p": 0.95,
                    "num_predict": 12000,  # Further increased for longer beats
                    "num_ctx": 32768,  # Large context window
                    "repeat_penalty": 1.1  # Reduce repetition
                }'''

# Count and replace
count = content.count(old_params)
content = content.replace(old_params, new_params)

with open('routers/narrative_projects.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ อัพเดท Ollama parameters สำเร็จ ({count} ตำแหน่ง)")
print("   - temperature: 0.7 → 1.0")
print("   - top_p: 0.9 → 0.95")
print("   - num_predict: 8000 → 12000")
print("   - num_ctx: เพิ่ม 32768")
print("   - repeat_penalty: เพิ่ม 1.1")
