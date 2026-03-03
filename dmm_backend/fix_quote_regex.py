#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

with open('routers/narrative_projects.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the regex patterns for fixing missing quotes
old_pattern = '''                # 0.2 Fix missing closing quotes in content fields - Qwen2.5 sometimes forgets them
                # Pattern: "content": "text text},  →  "content": "text text"},
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]*?)\\s*},', r'\\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]*?)\\s*}]', r'\\1"}]', structure_json_cleaned)'''

new_pattern = '''                # 0.2 Fix missing closing quotes in content fields - Qwen2.5 sometimes forgets them
                # Pattern: "content": "text text},  →  "content": "text text"},
                # First, fix all instances where } or }] appear without closing quote
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]+)},', r'\\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]+)}]', r'\\1"}]', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]+)}\\s*,', r'\\1"},', structure_json_cleaned)
                
                # Fix cases where content ends abruptly with }, or }]
                # Pattern: ...ใจ},  →  ...ใจ"},
                structure_json_cleaned = re.sub(r'([^"]})(},)', r'\\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'([^"}])}]', r'\\1"}]', structure_json_cleaned)'''

count = content.count(old_pattern)
content = content.replace(old_pattern, new_pattern)

with open('routers/narrative_projects.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ ปรับปรุง JSON quote fixing regex สำเร็จ ({count} ตำแหน่ง)")
print("   - เพิ่ม pattern สำหรับ }, และ }]")
print("   - แก้ไข pattern ให้ match ได้หลากหลายกว่าเดิม")
