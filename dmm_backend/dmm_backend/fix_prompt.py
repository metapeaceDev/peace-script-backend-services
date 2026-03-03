#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

with open('routers/narrative_projects.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace "Generate now:" with strict length enforcement
old_text = '''Generate now:"""'''

new_text = '''⚠️⚠️⚠️ CRITICAL LENGTH ENFORCEMENT ⚠️⚠️⚠️
EACH beat MUST be MINIMUM 250 Thai characters. NO EXCEPTIONS.
If a beat is shorter than 250 characters, ADD MORE DETAILS:
- Add specific dialogue with quotation marks
- Describe emotions in detail (facial expressions, body language)
- Include internal thoughts of the character
- Describe the setting/environment
- Add sensory details (sights, sounds, feelings)
- Explain character motivations and conflicts

Example of TOO SHORT (WRONG - only 100 characters):
"อาทิตย์นั่งมองท้องฟ้า ดวงตาเศร้า เขาคิดถึงคนรัก ความทรงจำในอดีตทำให้เขาเสียใจ"

Example of CORRECT LENGTH (300+ characters):
"เช้าวันนั้น อาทิตย์นั่งอยู่บนชั้นดาดฟ้าของอาคารคอนโด มองดูท้องฟ้าสีส้มแดงที่กำลังเปลี่ยนเป็นสีน้ำเงินเข้ม ลมพัดโชยผ่านใบหน้าที่เต็มไปด้วยความเหนื่อยล้า เขาหยิบรูปถ่ายครอบครัวที่พกติดตัวมาตลอดขึ้นมาดู น้ำตาไหลริน 'ทำไมชีวิตถึงโหดร้ายขนาดนี้' เขาพูดกับตัวเองด้วยเสียงสั่นเครือ ความทรงจำในอดีตที่สดใสกลับมาหลอกหลอน ทำให้เขารู้สึกโดดเดี่ยวและสิ้นหวัง ในหัวใจลึกๆ เขาเริ่มตั้งคำถามว่า ความรักที่เขาเชื่อถือมาตลอดนั้น ยังมีความหมายอีกหรือไม่"

NOW Generate 15 beats with MINIMUM 250 characters EACH:"""'''

content = content.replace(old_text, new_text)

with open('routers/narrative_projects.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ เพิ่ม CRITICAL LENGTH ENFORCEMENT สำเร็จ")
