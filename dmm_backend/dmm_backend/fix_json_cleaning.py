#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('routers/narrative_projects.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the section and add extra cleaning steps
old_cleaning = '''                # Match content inside quotes and replace newlines
                structure_json_cleaned = re.sub(r'"([^"]*)"', replace_inner_newlines, structure_json_cleaned, flags=re.DOTALL)
                
                # 1. Fix missing "name": before beat names'''

new_cleaning = '''                # Match content inside quotes and replace newlines
                structure_json_cleaned = re.sub(r'"([^"]*)"', replace_inner_newlines, structure_json_cleaned, flags=re.DOTALL)
                
                # 0.2 Fix missing closing quotes in content fields - Qwen2.5 sometimes forgets them
                # Pattern: "content": "text text},  →  "content": "text text"},
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]*?)\\s*},', r'\\1"},', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'("content"\\s*:\\s*"[^"]*?)\\s*}]', r'\\1"}]', structure_json_cleaned)
                
                # 0.3 Remove Chinese characters from Qwen2.5 (e.g., "250-350字")
                structure_json_cleaned = re.sub(r'[\\u4e00-\\u9fff]+', '', structure_json_cleaned)
                structure_json_cleaned = re.sub(r'：', ':', structure_json_cleaned)  # Fix Chinese colon
                
                # 0.4 Remove any non-JSON trailing content (e.g., "%")
                structure_json_cleaned = re.sub(r'\\]\\s*[^}\\]]*$', ']', structure_json_cleaned)
                
                # 1. Fix missing "name": before beat names'''

count = content.count(old_cleaning)
content = content.replace(old_cleaning, new_cleaning)

with open('routers/narrative_projects.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ เพิ่ม aggressive JSON cleaning สำเร็จ ({count} ตำแหน่ง)")
print("   - แก้ไข missing closing quotes")
print("   - ลบตัวอักษรจีนที่ Qwen2.5 สร้างมา")
print("   - ลบ trailing content ที่ไม่ใช่ JSON")
