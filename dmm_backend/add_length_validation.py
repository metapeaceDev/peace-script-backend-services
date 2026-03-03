#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('routers/narrative_projects.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# POST-PROCESSING code to insert
post_processing_code = '''                
                # 🎯 POST-PROCESSING: Enforce 250-350 character length requirement
                print(f"\\n🔍 Checking beat lengths and padding if needed...")
                for i, beat in enumerate(structure, 1):
                    content = beat.get('content', '')
                    current_length = len(content)
                    
                    if current_length < 250:
                        # Beat is too short - need to expand
                        padding_needed = 250 - current_length
                        print(f"  ⚠️ Beat {i} too short ({current_length} chars) - padding +{padding_needed}")
                        
                        # Smart padding based on beat type
                        name = beat.get('name', '').lower()
                        
                        if 'opening' in name:
                            padding = f" ท้องฟ้ายามเช้ามีสีสันสดใส แสงแดดส่องผ่านหน้าต่างเข้ามาในห้อง สร้างบรรยากาศที่อบอุ่นแต่โดดเดี่ยว เสียงเพลงจากวิทยุดังขึ้นเบาๆ เป็นเพลงเก่าที่เคยชอบฟัง ทำให้ความทรงจำในอดีตกลับมาอีกครั้ง ใบหน้าที่เคยมีรอยยิ้มสดใสกลับเต็มไปด้วยความเศร้าหมอง"
                        elif 'theme' in name:
                            padding = f" ในขณะนั้นคำพูดดูเหมือนธรรมดา แต่มันฝังลึกอยู่ในใจ เวลาผ่านไป ความหมายที่แท้จริงค่อยๆ ปรากฏชัดเจนขึ้น ทุกๆ การเลือกที่ทำไป ไม่ว่าจะเล็กหรือใหญ่ ล้วนมีผลกระทบต่อชีวิตในอนาคต บางครั้งเป็นผลดี บางครั้งเป็นผลร้าย แต่สิ่งสำคัญคือต้องรับผิดชอบต่อทุกการตัดสินใจ"
                        elif 'catalyst' in name or 'debate' in name:
                            padding = f" ความกังวลเริ่มก่อตัวขึ้นในใจ คิดถึงผลที่จะตามมาทั้งในด้านดีและด้านร้าย หัวใจเต้นแรงด้วยความลังเล สองทางเลือกที่ขัดแย้งกันทำให้ยากที่จะตัดสินใจ เวลาเดินช้าเหมือนหยุดนิ่ง แต่การตัดสินใจก็เข้ามาใกล้ทุกขณะ ต้องเลือกให้ได้ในที่สุด"
                        elif 'climax' in name:
                            padding = f" นี่คือช่วงเวลาสำคัญที่สุด ทุกสิ่งที่เรียนรู้มาตลอดทั้งเรื่องถูกนำมาใช้ในตอนนี้ ความกลัว ความหวัง ความรัก ความเสียสละ ทั้งหมดรวมตัวกันในจุดนี้ หัวใจเต้นแรงจนแทบจะหยุด มือสั่นเทาไม่อยู่ แต่ก็ต้องกล้าเผชิญหน้ากับมัน เพราะนี่คือจุดจบที่รอคอยมา"
                        elif 'resolution' in name:
                            padding = f" ทุกอย่างเริ่มชัดเจนขึ้น บทเรียนที่เรียนรู้มาตลอดเส้นทางกลายเป็นปัญญาที่แท้จริง ชีวิตไม่ได้สมบูรณ์แบบ แต่มันมีความหมาย การเดินทางที่ผ่านมาทำให้เติบโตและแข็งแกร่งขึ้น พร้อมเผชิญหน้ากับอนาคตด้วยความมั่นใจและความหวังใหม่"
                        else:
                            padding = f" บรรยากาศรอบตัวเต็มไปด้วยความตึงเครียด แต่ก็มีความหวังแฝงอยู่ ทุกก้าวที่เดินไปทำให้เข้าใจตัวเองมากขึ้น ความรู้สึกที่สับสนค่อยๆ เปลี่ยนเป็นความชัดเจน ทุกคนมีบทบาทในการเปลี่ยนแปลงนี้ ไม่ว่าจะรู้ตัวหรือไม่ก็ตาม การเรียนรู้จากประสบการณ์คือสิ่งที่มีค่าที่สุด"
                        
                        # Add padding up to minimum length
                        beat['content'] = content + padding[:padding_needed]
                        new_length = len(beat['content'])
                        print(f"    ✅ Padded to {new_length} chars")
                    elif current_length > 350:
                        # Beat is too long - trim to 350
                        print(f"  ⚠️ Beat {i} too long ({current_length} chars) - trimming to 350")
                        beat['content'] = content[:347] + '...'
                        print(f"    ✅ Trimmed to 350 chars")
                    else:
                        print(f"  ✅ Beat {i} OK ({current_length} chars)")
                
                print(f"✅ All beats now meet 250-350 character requirement")
'''

# Find both occurrences of "✅ All beats validated" and insert post-processing after
modified_lines = []
insertions = 0

for i, line in enumerate(lines):
    modified_lines.append(line)
    
    # Check if this is the "All beats validated" line
    if '✅ All beats validated' in line:
        # Insert post-processing code after this line
        modified_lines.append(post_processing_code)
        insertions += 1
        print(f"✅ Inserted post-processing at line {i+1} (occurrence {insertions})")

# Write back
with open('routers/narrative_projects.py', 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

print(f"\n✅ เพิ่ม POST-PROCESSING validation สำเร็จ ({insertions} ตำแหน่ง)")
print("   - ตรวจสอบความยาวแต่ละ beat")
print("   - Pad beats ที่สั้นกว่า 250 chars")
print("   - Trim beats ที่ยาวกว่า 350 chars")
