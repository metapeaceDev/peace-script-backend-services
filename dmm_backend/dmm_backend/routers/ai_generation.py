"""
AI Generation Router for Peace Script

Provides AI-powered content generation for Step 2: Scope of Story
Uses Ollama API for local LLM generation

Author: Peace Script Team
Date: 8 November 2568
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import json

router = APIRouter(
    prefix="/api/ai",
    tags=["ai-generation"]
)


# =============================================================================
# Request/Response Schemas
# =============================================================================

class GenrePercentage(BaseModel):
    type: str
    percentage: int


class Step1Data(BaseModel):
    """Step 1 data for AI generation"""
    script_name: str
    genres: List[GenrePercentage]
    script_type: str
    concept_description: Optional[str] = None
    target_audience: Optional[str] = None
    tags: List[str] = []
    language: str = "th"  # Language code: th, en, ja, etc.


class GeneratedScope(BaseModel):
    """Generated Scope of Story response"""
    big_idea: Dict[str, str]
    premise: Dict[str, str]
    theme: Dict[str, str]
    logline: Dict[str, str]
    timeline: Dict[str, Any]
    synopsis: Dict[str, str]  # เรื่องย่อ


# =============================================================================
# AI Generation Endpoint
# =============================================================================

@router.post("/generate-scope", response_model=GeneratedScope)
async def generate_scope_of_story(data: Step1Data):
    """
    Generate Step 2: Scope of Story using AI (Ollama)
    
    Uses Step 1 data to generate:
    - Big Idea
    - Premise (Question & Answer)
    - Theme
    - Logline
    - Timeline contexts (social, economic, environment)
    
    Example request:
    ```json
    {
        "script_name": "เงาแค้น",
        "genres": [
            {"type": "drama", "percentage": 60},
            {"type": "thriller", "percentage": 40}
        ],
        "script_type": "movie",
        "concept_description": "เรื่องราวของการแก้แค้น",
        "target_audience": "ผู้ชม 25-40 ปี",
        "tags": ["revenge", "redemption", "family"]
    }
    ```
    """
    
    # Build prompt for Ollama
    genre_str = ", ".join([f"{g.type} ({g.percentage}%)" for g in data.genres])
    tags_str = ", ".join(data.tags) if data.tags else "ไม่มี"
    
    # Language mapping for instructions
    language_instructions = {
        "th": "Generate ALL content in THAI language (ภาษาไทย). Use Thai script for all text.",
        "en": "Generate ALL content in ENGLISH language.",
        "ja": "Generate ALL content in JAPANESE language (日本語).",
        "zh": "Generate ALL content in CHINESE language (中文).",
        "ko": "Generate ALL content in KOREAN language (한국어).",
    }
    
    language_instruction = language_instructions.get(
        data.language, 
        f"Generate ALL content in the language with code: {data.language}"
    )
    
    prompt = f"""You are a professional screenplay writer assistant. Based on the following project details, generate a comprehensive Scope of Story for Step 2.

IMPORTANT LANGUAGE REQUIREMENT:
{language_instruction}
All generated content (big_idea, premise, theme, logline, timeline contexts) MUST be in the specified language.

Project Details:
- Script Name: {data.script_name}
- Genres: {genre_str}
- Script Type: {data.script_type}
- Language: {data.language}
- Concept: {data.concept_description or 'Not specified'}
- Target Audience: {data.target_audience or 'General audience'}
- Tags: {tags_str}

Please generate a complete Scope of Story with:

1. BIG IDEA (choose prefix and content):
   - Prefix: either "what_will_happen_if" (preferred for high concept) or "is_the_story_of"
   - Content: Create a compelling, high-stakes concept (20-200 words).
     * MUST use Step 1 data (Concept: {data.concept_description}, Genres: {genre_str}, Tags: {tags_str}).
     * Focus on IRONIC or PARADOXICAL situations (e.g., a fire fighter who starts fires).
     * Highlight EXTREME CONFLICT or an IMPOSSIBLE GOAL.
     * Make it exciting and intriguing - something the audience MUST see the outcome of.
     * If 'what_will_happen_if': Ask a challenging question that combines two opposing forces.
     * If 'is_the_story_of': Describe a unique protagonist facing an overwhelming dilemma.
     * IN THE SPECIFIED LANGUAGE.

2. PREMISE:
   - Question: "What is this movie going to tell?" (20-100 words) - IN THE SPECIFIED LANGUAGE
   - Answer: The main message (20-100 words) - IN THE SPECIFIED LANGUAGE

3. THEME:
   - Lesson: The teaching/lesson (starting with "This tale teaches that...") (10-50 words) - IN THE SPECIFIED LANGUAGE

4. LOGLINE:
   - Premise: Story summary (20-100 words) - IN THE SPECIFIED LANGUAGE
   - Support Theme: How it supports the theme (20-100 words) - IN THE SPECIFIED LANGUAGE

5. TIMELINE CONTEXTS (Crucial for story world building):
   - Social Context: Describe the social structure, values, and cultural norms of the world (100-200 words, at least 200 characters) - IN THE SPECIFIED LANGUAGE
   - Economic Context: Describe the economic situation, wealth distribution, and class struggles (100-200 words, at least 200 characters) - IN THE SPECIFIED LANGUAGE
   - Environment Context: Describe the physical setting, geography, atmosphere, and weather (100-200 words, at least 200 characters) - IN THE SPECIFIED LANGUAGE

Return ONLY a valid JSON object with this exact structure:
{{
  "big_idea": {{
    "prefix": "what_will_happen_if",
    "content": "..."
  }},
  "premise": {{
    "question": "...",
    "answer": "..."
  }},
  "theme": {{
    "teaching": "This tale teaches that",
    "lesson": "..."
  }},
  "logline": {{
    "premise": "...",
    "support_theme": "..."
  }},
  "timeline": {{
    "movie_duration": 120,
    "seasons": "...",
    "date": "...",
    "social": "...",
    "economic": "...",
    "environment": "..."
  }}
}}

CRITICAL: All content fields MUST be in {data.language} language. Return ONLY the JSON object, no additional text or explanations."""

    # For languages that AI model doesn't support well (Chinese, Japanese, Korean),
    # skip AI generation and use fallback templates directly
    if data.language in ["zh", "ja", "ko"]:
        # Smart theme generation for CJK languages
        def generate_cjk_theme(lang: str, genres: List[GenrePercentage], tags: List[str]) -> str:
            dominant_genre = genres[0].type if genres else "drama"
            
            ja_themes = {
                "drama": "すべての選択には結果があり、私たちの運命を形作る",
                "comedy": "幸せは目的地ではなく、旅の中にある",
                "action": "正義には勇気と犠牲が必要である",
                "romance": "真実の愛には勇気と弱さが必要である"
            }
            zh_themes = {
                "drama": "每个选择都有后果，塑造我们的命运",
                "comedy": "幸福在旅程中，而非目的地",
                "action": "正义需要勇气和牺牲",
                "romance": "真爱需要勇气和脆弱"
            }
            ko_themes = {
                "drama": "모든 선택에는 결과가 있으며 우리의 운명을 형성한다",
                "comedy": "행복은 목적지가 아니라 여정 속에 있다",
                "action": "정의에는 용기와 희생이 필요하다",
                "romance": "진정한 사랑에는 용기와 취약함이 필요하다"
            }
            
            theme_map = {"ja": ja_themes, "zh": zh_themes, "ko": ko_themes}
            themes = theme_map.get(lang, ja_themes)
            return themes.get(dominant_genre, list(themes.values())[0])
        
        # Language-specific fallback templates
        fallback_templates = {
            "ja": {
                "big_idea_content": data.concept_description or f"{data.script_name}についての{data.script_type}",
                "premise_question": f"{data.script_name}では何が起こるのか？",
                "premise_answer": f"この物語は{', '.join(data.tags[:3]) if data.tags else '人間の経験'}のテーマを探求します。",
                "theme_teaching": "この物語が教えてくれること",
                "theme_lesson": generate_cjk_theme("ja", data.genres, data.tags),
                "logline_premise": f"困難に立ち向かう登場人物を追う魅力的な{data.script_type}",
                "logline_support": "彼らがどのように障害を乗り越え成長するかを示します。",
                "social": "現代的な価値観を持つ現代社会",
                "economic": "現実的な経済的圧力のある中流階級の設定",
                "environment": "自然の要素を持つ都市環境",
                "synopsis": f"""《{data.script_name}》は、{data.concept_description or f'{", ".join(data.tags[:3]) if data.tags else "人間の物語"}についての{data.script_type}'}です。

【物語の核心】
この作品の中心となるテーマは、{', '.join(data.tags[:3]) if data.tags else '人間の経験と成長'}です。登場人物たちは、現代的な価値観を持つ現代社会という舞台で、様々な困難に立ち向かいます。

【社会的背景】
物語は現代的な価値観を持つ現代社会を舞台に展開されます。登場人物たちは、現実的な経済的圧力のある中流階級の環境で生活し、日々の選択と決断を迫られます。

【物語の展開】
主人公たちは、困難な状況に直面しながらも、それぞれの信念と目標に向かって前進します。彼らの旅は、単なる外的な障害を乗り越えるだけでなく、内面的な成長と変化をもたらします。自然の要素を持つ都市環境という設定の中で、登場人物たちの人間関係や葛藤が描かれます。

【メッセージとテーマ】
この物語が観客に伝えたいのは、すべての選択には結果があるということです。登場人物たちの経験を通じて、視聴者は人生における重要な教訓を学び、自分自身の人生について考えるきっかけを得ることができます。彼らがどのように障害を乗り越え成長するかを見ることで、観客自身も勇気と希望を見出すことができるでしょう。"""
            },
            "zh": {
                "big_idea_content": data.concept_description or f"关于{data.script_name}的{data.script_type}",
                "premise_question": f"{data.script_name}讲述了什么？",
                "premise_answer": f"这个故事探讨了{', '.join(data.tags[:3]) if data.tags else '人类经验'}的主题。",
                "theme_teaching": "这个故事告诉我们",
                "theme_lesson": generate_cjk_theme("zh", data.genres, data.tags),
                "logline_premise": f"一个引人入胜的{data.script_type}，跟随角色面对挑战",
                "logline_support": "展示他们如何克服障碍并成长。",
                "social": "具有当代价值观的现代社会",
                "economic": "具有现实经济压力的中产阶级背景",
                "environment": "具有自然元素的城市环境",
                "synopsis": f"""《{data.script_name}》是一部{data.concept_description or f'关于{", ".join(data.tags[:3]) if data.tags else "人性"}的{data.script_type}'}。

【故事核心】
这部作品的核心主题围绕着{', '.join(data.tags[:3]) if data.tags else '人类经验与成长'}展开。角色们在具有当代价值观的现代社会这一舞台上，面对各种困难和挑战。

【社会背景】
故事设定在具有当代价值观的现代社会中。主人公们生活在具有现实经济压力的中产阶级背景下，每天都要面对各种选择和决定。这个真实的社会环境为故事的展开提供了丰富的戏剧张力。

【故事发展】
主角们在困境中不断前行，追求各自的信念和目标。他们的旅程不仅仅是克服外在的障碍，更重要的是实现内在的成长和转变。在具有自然元素的城市环境这一独特设定中，人物之间的关系和冲突得以深刻展现。

【核心信息与主题】
这个故事想要传达给观众的核心信息是：每个选择都有后果。通过角色们的经历，观众将学到人生中的重要教训，并有机会反思自己的生活。看到他们如何克服障碍并成长，观众也能从中获得勇气和希望，找到面对自己人生挑战的力量。"""
            },
            "ko": {
                "big_idea_content": data.concept_description or f"{data.script_name}에 대한 {data.script_type}",
                "premise_question": f"{data.script_name}에서 무슨 일이 일어나는가?",
                "premise_answer": f"이 이야기는 {', '.join(data.tags[:3]) if data.tags else '인간 경험'}의 주제를 탐구합니다.",
                "theme_teaching": "이 이야기가 가르쳐주는 것",
                "theme_lesson": generate_cjk_theme("ko", data.genres, data.tags),
                "logline_premise": f"도전에 직면한 캐릭터들을 따라가는 매력적인 {data.script_type}",
                "logline_support": "그들이 어떻게 장애물을 극복하고 성장하는지 보여줍니다.",
                "social": "현대적인 가치관을 가진 현대 사회",
                "economic": "현실적인 경제적 압박이 있는 중산층 배경",
                "environment": "자연 요소가 있는 도시 환경",
                "synopsis": f"""《{data.script_name}》는 {data.concept_description or f'{", ".join(data.tags[:3]) if data.tags else "인간성"}에 관한 {data.script_type}'}입니다.

【이야기의 시작】
이 작품의 핵심 주제는 {', '.join(data.tags[:3]) if data.tags else '인간 경험과 성장'}입니다. 주인공들은 현대적인 가치관을 가진 현대 사회라는 무대에서 다양한 어려움에 직면합니다.

【이야기 전개】
이야기는 현실적인 경제적 압박이 있는 중산층 배경에서 펼쳐집니다. 주인공들은 매일 여러 선택과 결정을 내려야 하는 상황에 놓입니다. 이러한 현실적인 사회 환경은 이야기 전개에 풍부한 극적 긴장감을 제공합니다.

주인공들은 어려운 상황 속에서도 각자의 신념과 목표를 향해 나아갑니다. 그들의 여정은 단순히 외적인 장애물을 극복하는 것뿐만 아니라, 내면적인 성장과 변화를 가져옵니다. 자연 요소가 있는 도시 환경이라는 독특한 설정 속에서 인물들 간의 관계와 갈등이 깊이 있게 그려집니다.

【메시지와 결말】
이 이야기가 관객에게 전달하고자 하는 핵심 메시지는 모든 선택에는 결과가 있다는 것입니다. 등장인물들의 경험을 통해 관객은 인생의 중요한 교훈을 배우고 자신의 삶을 되돌아볼 기회를 갖게 됩니다. 그들이 어떻게 장애물을 극복하고 성장하는지 보면서, 관객 역시 용기와 희망을 얻고 자신의 인생 과제에 맞설 힘을 찾을 수 있을 것입니다."""
            }
        }
        
        # Get templates for user's language
        templates = fallback_templates.get(data.language, fallback_templates["zh"])
        
        return GeneratedScope(
            big_idea={
                "prefix": "is_the_story_of",
                "content": templates["big_idea_content"]
            },
            premise={
                "question": templates["premise_question"],
                "answer": templates["premise_answer"]
            },
            theme={
                "teaching": templates["theme_teaching"],
                "lesson": templates["theme_lesson"]
            },
            logline={
                "premise": templates["logline_premise"],
                "support_theme": templates["logline_support"]
            },
            timeline={
                "movie_duration": 120,
                "seasons": "ฤดูใดก็ได้",
                "date": "ปัจจุบัน",
                "social": templates["social"],
                "economic": templates["economic"],
                "environment": templates["environment"]
            },
            synopsis={
                "content": templates["synopsis"]
            }
        )
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",  # Upgraded to Qwen2.5 (better Thai support)
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Ollama API error: {response.text}"
                )
            
            result = response.json()
            generated_text = result.get("response", "")
            
            # Parse JSON from response
            try:
                # Try to find JSON in the response
                start_idx = generated_text.find('{')
                end_idx = generated_text.rfind('}') + 1
                
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON found in response")
                
                json_str = generated_text[start_idx:end_idx]
                generated_data = json.loads(json_str)
                
                # Validate structure
                required_keys = ["big_idea", "premise", "theme", "logline", "timeline"]
                for key in required_keys:
                    if key not in generated_data:
                        raise ValueError(f"Missing required key: {key}")
                
                # Check if any field is empty and use fallback
                has_empty_fields = False
                
                # Check big_idea
                if not generated_data.get("big_idea", {}).get("content", "").strip():
                    has_empty_fields = True
                
                # Check premise
                if not generated_data.get("premise", {}).get("question", "").strip() or \
                   not generated_data.get("premise", {}).get("answer", "").strip():
                    has_empty_fields = True
                
                # Check theme
                if not generated_data.get("theme", {}).get("lesson", "").strip():
                    has_empty_fields = True
                
                # Check logline
                if not generated_data.get("logline", {}).get("premise", "").strip() or \
                   not generated_data.get("logline", {}).get("support_theme", "").strip():
                    has_empty_fields = True
                
                # Check timeline
                timeline = generated_data.get("timeline", {})
                if not timeline.get("social", "").strip() or \
                   not timeline.get("economic", "").strip() or \
                   not timeline.get("environment", "").strip():
                    has_empty_fields = True
                
                # If has empty fields, use fallback to fill them
                if has_empty_fields:
                    raise ValueError("Some fields are empty, using fallback")
                
                return GeneratedScope(**generated_data)
                
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback: Return template with concept description in user's language
                
                # 🎯 Smart Theme Generation based on genres and tags
                def generate_smart_theme(language: str, genres: List[GenrePercentage], tags: List[str], concept: Optional[str]) -> str:
                    """Generate theme based on project context instead of using hardcoded text"""
                    
                    # Extract dominant genre
                    dominant_genre = genres[0].type if genres else "drama"
                    
                    # Theme templates by genre (Thai) - Extended to meet 50 char minimum
                    genre_themes_th = {
                        "drama": [
                            "ทุกการเลือกมีผลที่ตามมาและกำหนดอนาคตของเราในทุกย่างก้าว",
                            "ความกล้าที่จะเผชิญหน้ากับความจริงคือจุดเริ่มต้นของการเปลี่ยนแปลงชีวิต",
                            "การยอมรับความอ่อนแอของตนเองคือความแข็งแกร่งที่แท้จริงของหัวใจ",
                            "ความรักและการให้อภัยมีพลังเปลี่ยนแปลงชีวิตและรักษาบาดแผลได้"
                        ],
                        "comedy": [
                            "ความสุขไม่ได้อยู่ที่ปลายทาง แต่อยู่ที่การเดินทางและประสบการณ์",
                            "เสียงหัวเราะคือยาวิเศษที่รักษาบาดแผลของหัวใจและจิตวิญญาณ",
                            "บางครั้งสิ่งที่เราต้องการไม่ใช่สิ่งที่เราจำเป็นต้องมีในชีวิต",
                            "ความผิดพลาดคือโอกาสในการเรียนรู้และเติบโตไปสู่ความสำเร็จ"
                        ],
                        "action": [
                            "ความยุติธรรมต้องการความกล้าหาญและการเสียสละเพื่อสิ่งที่ถูกต้อง",
                            "พลังที่แท้จริงมาจากการปกป้องคนที่เรารักและสิ่งที่เราเชื่อ",
                            "วีรบุรุษไม่ได้เกิดมา แต่ถูกหล่อหลอมจากการทดสอบและความยากลำบาก",
                            "การต่อสู้เพื่อสิ่งที่ถูกต้องคุ้มค่ากับการเสียสละและความพยายาม"
                        ],
                        "horror": [
                            "ความกลัวที่ยิ่งใหญ่ที่สุดคือความกลัวในใจเรา",
                            "อดีตที่ถูกปิดบังจะกลับมาหลอกหลอน",
                            "ความชั่วมักซ่อนอยู่ในรูปลักษณ์ที่ไร้เดียงสา",
                            "การเผชิญหน้ากับความมืดคือทางเดียวที่จะพบแสงสว่าง"
                        ],
                        "romance": [
                            "ความรักที่แท้จริงต้องการความกล้าและความเปราะบาง",
                            "หัวใจที่เปิดรับคือหัวใจที่เติบโตได้",
                            "บางครั้งการปล่อยวางคือการรักที่ยิ่งใหญ่ที่สุด",
                            "ความรักไม่ได้สมบูรณ์แบบ แต่มันแท้จริงและจริงใจ"
                        ],
                        "thriller": [
                            "ความลับทุกอย่างมีราคาที่ต้องจ่าย",
                            "ความไว้วางใจคือของขวัญที่ล้ำค่าและเปราะบาง",
                            "ความจริงมักซ่อนอยู่ในที่ที่เราไม่มองหา",
                            "การหลอกลวงมักนำมาซึ่งการล่มสลายในที่สุด"
                        ],
                        "sci-fi": [
                            "ความก้าวหน้าทางเทคโนโลยีต้องมาพร้อมความรับผิดชอบ",
                            "อนาคตถูกสร้างจากการเลือกในวันนี้",
                            "มนุษยชาติคือสิ่งที่กำหนดเรา ไม่ใช่เทคโนโลยี",
                            "การค้นพบความจริงอาจเปลี่ยนโลกตลอดกาล"
                        ],
                        "fantasy": [
                            "พลังที่แท้จริงมาจากภายในไม่ใช่จากเวทมนตร์",
                            "ทุกคนมีโชคชตาของตนเอง แต่ความกล้าคือที่จะเลือก",
                            "ความดีและความชั่วอยู่ในทุกหัวใจ ขึ้นอยู่กับการเลือก",
                            "การเดินทางที่ยิ่งใหญ่เริ่มต้นด้วยก้าวเล็กๆ"
                        ],
                        "mystery": [
                            "ความจริงมักซับซ้อนกว่าที่ปรากฏ",
                            "ทุกคนมีความลับ และทุกความลับมีเหตุผล",
                            "การค้นหาความจริงต้องแลกด้วยความกล้าเผชิญหน้า",
                            "บางครั้งคำตอบอยู่ตรงหน้าเราตลอดมา"
                        ]
                    }
                    
                    # Theme templates by genre (English)
                    genre_themes_en = {
                        "drama": [
                            "every choice has consequences that shape our destiny",
                            "the courage to face truth is the beginning of transformation",
                            "accepting our vulnerabilities is true strength",
                            "love and forgiveness have the power to change lives"
                        ],
                        "comedy": [
                            "happiness is found in the journey, not the destination",
                            "laughter is the medicine that heals the heart",
                            "sometimes what we want isn't what we need",
                            "mistakes are opportunities for growth and learning"
                        ],
                        "action": [
                            "justice requires courage and sacrifice",
                            "true power comes from protecting those we love",
                            "heroes are forged through trials, not born",
                            "fighting for what's right is worth the sacrifice"
                        ],
                        "horror": [
                            "the greatest fear is the one within ourselves",
                            "buried past always comes back to haunt us",
                            "evil often hides behind innocent facades",
                            "facing darkness is the only way to find light"
                        ],
                        "romance": [
                            "true love requires courage and vulnerability",
                            "an open heart is a growing heart",
                            "sometimes letting go is the greatest act of love",
                            "love isn't perfect, but it's real and honest"
                        ],
                        "thriller": [
                            "every secret has a price to pay",
                            "trust is a precious and fragile gift",
                            "truth often hides where we don't look",
                            "deception ultimately leads to downfall"
                        ],
                        "sci-fi": [
                            "technological advancement requires responsibility",
                            "the future is built from today's choices",
                            "our humanity defines us, not technology",
                            "discovering truth can change the world forever"
                        ],
                        "fantasy": [
                            "true power comes from within, not magic",
                            "everyone has their destiny, but courage is choosing it",
                            "good and evil exist in every heart - it's about choices",
                            "great journeys begin with small steps"
                        ],
                        "mystery": [
                            "truth is often more complex than it appears",
                            "everyone has secrets, and every secret has a reason",
                            "finding truth requires courage to confront it",
                            "sometimes answers are right in front of us"
                        ]
                    }
                    
                    # Select theme templates by language
                    if language == "th":
                        theme_options = genre_themes_th.get(dominant_genre, genre_themes_th["drama"])
                    else:
                        theme_options = genre_themes_en.get(dominant_genre, genre_themes_en["drama"])
                    
                    # Use tags to select most relevant theme
                    if tags:
                        # Check if any tag relates to specific themes
                        tag_lower = [t.lower() for t in tags]
                        
                        if any(word in tag_lower for word in ["revenge", "แค้น", "ล้างแค้น"]):
                            return theme_options[0] if len(theme_options) > 0 else theme_options[0]
                        elif any(word in tag_lower for word in ["love", "รัก", "ความรัก"]):
                            return theme_options[-1] if len(theme_options) > 1 else theme_options[0]
                        elif any(word in tag_lower for word in ["family", "ครอบครัว", "พ่อแม่"]):
                            return theme_options[1] if len(theme_options) > 1 else theme_options[0]
                        elif any(word in tag_lower for word in ["truth", "ความจริง", "เปิดเผย"]):
                            return theme_options[2] if len(theme_options) > 2 else theme_options[0]
                    
                    # Default: use first theme option for the genre
                    return theme_options[0]
                
                # Language-specific fallback templates
                fallback_templates = {
                    "th": {
                        "big_idea_content": data.concept_description or f"{data.script_type} เกี่ยวกับ {data.script_name}",
                        "premise_question": f"เรื่องราวใน {data.script_name} พูดถึงอะไร และเรื่องนี้จะสื่อสารอะไรให้กับผู้ชม?",
                        "premise_answer": f"เรื่องนี้สำรวจและเจาะลึกถึงธีมของ {', '.join(data.tags[:3]) if data.tags else 'ประสบการณ์ของมนุษย์'} ที่สะท้อนให้เห็นถึงความเป็นมนุษย์ การเติบโต และการค้นหาความหมายของชีวิตผ่านการเดินทางของตัวละคร",
                        "theme_teaching": "เรื่องนี้สอนให้รู้ว่า",
                        "theme_lesson": generate_smart_theme("th", data.genres, data.tags, data.concept_description),
                        "logline_premise": f"{data.script_type} ที่น่าติดตามเกี่ยวกับตัวละครที่เผชิญกับความท้าทายและอุปสรรคต่างๆ ที่เข้ามาขัดขวางกับความเชื่อและค่านิยมของตนเอง",
                        "logline_support": "แสดงให้เห็นว่าพวกเขาเอาชนะอุปสรรคและเติบโตได้อย่างไรผ่านการเรียนรู้และการยอมรับ",
                        "social": "สังคมในเรื่องราวนี้เป็นภาพสะท้อนของสังคมสมัยใหม่ที่มีความซับซ้อนและหลากหลาย โดยมีค่านิยมร่วมสมัยที่ผสมผสานระหว่างประเพณีดั้งเดิมและความก้าวหน้าทางเทคโนโลยี ผู้คนในสังคมต่างดิ้นรนเพื่อความสำเร็จและการยอมรับ ท่ามกลางกระแสการเปลี่ยนแปลงที่รวดเร็ว ความสัมพันธ์ระหว่างบุคคลมีความเปราะบางแต่ก็ยังคงมีความผูกพันที่ลึกซึ้งในระดับครอบครัวและชุมชน การแบ่งแยกทางความคิดและความเชื่อเป็นสิ่งที่เห็นได้ชัดเจน แต่ในขณะเดียวกันก็มีความพยายามที่จะหาจุดร่วมเพื่ออยู่ร่วมกันอย่างสันติ โครงสร้างทางสังคมเปิดโอกาสให้มีการเลื่อนสถานะแต่ก็ยังมีความเหลื่อมล้ำที่ซ่อนอยู่ ซึ่งส่งผลต่อการตัดสินใจและวิถีชีวิตของตัวละครอย่างมีนัยสำคัญ",
                        "economic": "ฉากหลังทางเศรษฐกิจของเรื่องราวนี้ตั้งอยู่ในสภาวะที่มีความผันผวนและความกดดันที่สมจริง โดยเน้นไปที่ชีวิตของชนชั้นกลางที่ต้องแบกรับภาระค่าใช้จ่ายและความคาดหวังทางสังคม การกระจายความมั่งคั่งยังคงมีความไม่เท่าเทียม ซึ่งสร้างแรงกดดันให้ตัวละครต้องดิ้นรนและแข่งขันเพื่อความอยู่รอดและความมั่นคงในชีวิต โอกาสทางธุรกิจและการงานมีทั้งความเสี่ยงและความท้าทาย ทำให้การตัดสินใจทางการเงินกลายเป็นเรื่องสำคัญที่มีผลต่อความสัมพันธ์และอนาคต สภาพเศรษฐกิจนี้ไม่ได้เป็นเพียงแค่ฉากหลัง แต่เป็นปัจจัยขับเคลื่อนที่สร้างความขัดแย้งและแรงจูงใจให้กับตัวละครในการกระทำสิ่งต่างๆ เพื่อให้หลุดพ้นจากข้อจำกัดหรือเพื่อรักษาเสถียรภาพของครอบครัว",
                        "environment": "สภาพแวดล้อมในเรื่องราวนี้ถูกกำหนดให้เป็นพื้นที่เมืองที่มีชีวิตชีวาแต่ก็แฝงไปด้วยความวุ่นวาย โดยมีการผสมผสานระหว่างตึกสูงระฟ้าและพื้นที่สีเขียวที่แทรกตัวอยู่อย่างจำกัด บรรยากาศโดยรวมสะท้อนถึงความเร่งรีบของชีวิตในเมืองใหญ่ แต่ก็ยังมีมุมสงบที่ตัวละครใช้เป็นที่หลบภัยทางใจ สภาพอากาศมีการเปลี่ยนแปลงตามฤดูกาลที่มีผลต่ออารมณ์และโทนของเรื่อง ตั้งแต่แสงแดดที่สดใสไปจนถึงฝนที่ตกหนักซึ่งสื่อถึงความขัดแย้งภายในใจ รายละเอียดของสถานที่ต่างๆ ไม่ว่าจะเป็นที่พักอาศัย ที่ทำงาน หรือพื้นที่สาธารณะ ถูกออกแบบมาเพื่อสะท้อนสถานะและตัวตนของตัวละคร รวมถึงเป็นกระจกเงาที่สะท้อนถึงสภาวะจิตใจและการเปลี่ยนแปลงที่เกิดขึ้นตลอดการเดินทางของเรื่องราว",
                        "synopsis": f"""{data.script_name} เป็น{data.script_type}ที่เกี่ยวกับ{data.concept_description or f"เรื่องราวของ {', '.join(data.tags[:3]) if data.tags else 'มนุษย์'}"}

【เปิดเรื่อง】
ธีมหลักของผลงานชิ้นนี้คือ {', '.join(data.tags[:3]) if data.tags else 'การเติบโตและการเรียนรู้'} ที่สะท้อนให้เห็นถึงความท้าทายและการต่อสู้ของตัวละครหลักในการค้นหาคำตอบและความหมายของชีวิต โดยเรื่องราวดำเนินไปท่ามกลางบริบทของสังคมสมัยใหม่ที่มีค่านิยมร่วมสมัย ซึ่งทำให้ผู้ชมสามารถเชื่อมโยงกับประสบการณ์และความรู้สึกของตัวละครได้อย่างลึกซึ้ง

【เนื้อหา】
เรื่องราวเกิดขึ้นในฉากหลังของชนชั้นกลางที่มีความกดดันทางเศรษฐกิจที่สมจริง ทำให้ตัวละครต้องเผชิญกับปัญหาและอุปสรรคที่หลากหลาย ตลอดการเดินทางของเรื่อง พวกเขาจะได้พบกับสถานการณ์ที่ท้าทายความเชื่อและค่านิยมเดิมๆ ของตนเอง นำไปสู่การเปลี่ยนแปลงและการเติบโตทางจิตใจอย่างมีนัยสำคัญ สภาพแวดล้อมในเมืองที่มีองค์ประกอบของธรรมชาติ ยังช่วยเสริมบรรยากาศและสร้างความลึกซึ้งให้กับเรื่องราว โดยแต่ละฉากถูกออกแบบมาเพื่อสะท้อนสภาวะจิตใจและการพัฒนาของตัวละคร

【บทสรุป】
ข้อความหลักที่ผลงานต้องการสื่อสารคือ ทุกการเลือกมีผลที่ตามมา และการกล้าเผชิญหน้ากับความจริงเป็นจุดเริ่มต้นของการเปลี่ยนแปลง ผู้ชมจะได้เห็นว่าตัวละครเอาชนะอุปสรรคและเติบโตได้อย่างไร ผ่านการตัดสินใจที่กล้าหาญและการยอมรับความอ่อนแอของตนเอง นำไปสู่การค้นพบความแข็งแกร่งภายในที่แท้จริง เรื่องนี้จึงเป็นมากกว่าแค่{data.script_type} แต่เป็นการสะท้อนให้เห็นถึงการเดินทางของชีวิตที่ทุกคนต้องเผชิญ และบทเรียนอันมีค่าที่จะอยู่กับผู้ชมไปอีกนาน"""
                    },
                    "en": {
                        "big_idea_content": data.concept_description or f"A {data.script_type} about {data.script_name}",
                        "premise_question": f"What happens in {data.script_name}?",
                        "premise_answer": f"This story explores themes of {', '.join(data.tags[:3]) if data.tags else 'human experience'}.",
                        "theme_teaching": "This tale teaches that",
                        "theme_lesson": generate_smart_theme("en", data.genres, data.tags, data.concept_description),
                        "logline_premise": f"A compelling {data.script_type} that follows characters through challenges",
                        "logline_support": "showing how they overcome obstacles and grow.",
                        "social": "Modern society with contemporary values",
                        "economic": "Middle-class setting with realistic economic pressures",
                        "environment": "Urban environment with natural elements",
                        "synopsis": f"""{data.script_name} is a {data.script_type} about {data.concept_description or f"the story of {', '.join(data.tags[:3]) if data.tags else 'human nature'}"}.

【OPENING】
The core theme of this work revolves around {', '.join(data.tags[:3]) if data.tags else 'growth and self-discovery'}, reflecting the challenges and struggles of the main characters as they search for answers and meaning in their lives. The narrative unfolds against the backdrop of modern society with contemporary values, allowing the audience to deeply connect with the characters' experiences and emotions through relatable situations and universal human conditions.

【STORY DEVELOPMENT】
The story takes place in a middle-class setting with realistic economic pressures, forcing the characters to confront various problems and obstacles. Throughout their journey, they encounter situations that challenge their existing beliefs and values, leading to significant transformation and psychological growth. The urban environment with natural elements enhances the atmosphere and adds depth to the narrative, with each scene carefully designed to reflect the characters' mental states and development as they navigate through both internal and external conflicts.

【MESSAGE & CONCLUSION】
The central message this work conveys is that every choice has consequences, and the courage to face the truth is the beginning of transformation. The audience will witness how the characters overcome obstacles and grow through brave decisions and acceptance of their own vulnerabilities, leading to the discovery of their true inner strength. This is more than just a {data.script_type}—it is a reflection of life's journey that everyone must face, offering valuable lessons that will resonate with the audience long after the story ends."""
                    },
                    "ja": {
                        "big_idea_content": data.concept_description or f"{data.script_name}についての{data.script_type}",
                        "premise_question": f"{data.script_name}では何が起こるのか？",
                        "premise_answer": f"この物語は{', '.join(data.tags[:3]) if data.tags else '人間の経験'}のテーマを探求します。",
                        "theme_teaching": "この物語が教えてくれること",
                        "theme_lesson": "すべての選択には結果がある。",
                        "logline_premise": f"困難に立ち向かう登場人物を追う魅力的な{data.script_type}",
                        "logline_support": "彼らがどのように障害を乗り越え成長するかを示します。",
                        "social": "現代的な価値観を持つ現代社会",
                        "economic": "現実的な経済的圧力のある中流階級の設定",
                        "environment": "自然の要素を持つ都市環境",
                        "synopsis": f"{data.script_name}は、{', '.join(data.tags[:3]) if data.tags else '人間の物語'}についての{data.script_type}です。登場人物たちが直面する課題を通じて、人生の重要な教訓を学びます。"
                    },
                    "zh": {
                        "big_idea_content": data.concept_description or f"关于{data.script_name}的{data.script_type}",
                        "premise_question": f"{data.script_name}讲述了什么？",
                        "premise_answer": f"这个故事探讨了{', '.join(data.tags[:3]) if data.tags else '人类经验'}的主题。",
                        "theme_teaching": "这个故事告诉我们",
                        "theme_lesson": "每个选择都有后果。",
                        "logline_premise": f"一个引人入胜的{data.script_type}，跟随角色面对挑战",
                        "logline_support": "展示他们如何克服障碍并成长。",
                        "social": "具有当代价值观的现代社会",
                        "economic": "具有现实经济压力的中产阶级背景",
                        "environment": "具有自然元素的城市环境",
                        "synopsis": f"{data.script_name}是一部关于{', '.join(data.tags[:3]) if data.tags else '人性'}的{data.script_type}。通过角色面对的挑战，观众将看到生活中重要的教训。"
                    },
                    "ko": {
                        "big_idea_content": data.concept_description or f"{data.script_name}에 대한 {data.script_type}",
                        "premise_question": f"{data.script_name}에서 무슨 일이 일어나는가?",
                        "premise_answer": f"이 이야기는 {', '.join(data.tags[:3]) if data.tags else '인간 경험'}의 주제를 탐구합니다.",
                        "theme_teaching": "이 이야기가 가르쳐주는 것",
                        "theme_lesson": "모든 선택에는 결과가 있다.",
                        "logline_premise": f"도전에 직면한 캐릭터들을 따라가는 매력적인 {data.script_type}",
                        "logline_support": "그들이 어떻게 장애물을 극복하고 성장하는지 보여줍니다.",
                        "social": "현대적인 가치관을 가진 현대 사회",
                        "economic": "현실적인 경제적 압박이 있는 중산층 배경",
                        "environment": "자연 요소가 있는 도시 환경",
                        "synopsis": f"{data.script_name}는 {', '.join(data.tags[:3]) if data.tags else '인간성'}에 관한 {data.script_type}입니다. 등장인물들이 직면한 도전을 통해 인생의 중요한 교훈을 배웁니다."
                    }
                }
                
                # Get templates for user's language, fallback to English
                templates = fallback_templates.get(data.language, fallback_templates["en"])
                
                return GeneratedScope(
                    big_idea={
                        "prefix": "is_the_story_of",
                        "content": templates["big_idea_content"]
                    },
                    premise={
                        "question": templates["premise_question"],
                        "answer": templates["premise_answer"]
                    },
                    theme={
                        "teaching": templates["theme_teaching"],
                        "lesson": templates["theme_lesson"]
                    },
                    logline={
                        "premise": templates["logline_premise"],
                        "support_theme": templates["logline_support"]
                    },
                    timeline={
                        "movie_duration": 120,
                        "seasons": "ฤดูใดก็ได้",
                        "date": "ปัจจุบัน",
                        "social": templates["social"],
                        "economic": templates["economic"],
                        "environment": templates["environment"]
                    },
                    synopsis={
                        "content": templates["synopsis"]
                    }
                )
    
    except ValueError as e:
        # Fallback triggered (for unsupported languages or empty fields)
        # The fallback logic is already handled above in the except block
        # This shouldn't be reached, but just in case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation error: {str(e)}"
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI generation timed out. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation error: {str(e)}"
        )


@router.get("/health")
async def check_ollama_health():
    """Check if Ollama service is available"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "healthy",
                    "available_models": [m.get("name") for m in models]
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Ollama responded with error"
                }
    
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "message": "Please start Ollama: brew services start ollama"
        }


# =============================================================================
# CHARACTER GENERATION FROM SCOPE
# =============================================================================

async def generate_characters_from_scope(scope, project, character_count=5):
    """
    🤖 Generate characters from StoryScope data (Step 1-2)
    
    Uses AI to analyze the story scope (plot, theme, setting) and generate
    appropriate characters with genders, roles, and backgrounds that fit the narrative.
    
    Parameters:
    - scope: StoryScope document
    - project: Project document
    - character_count: Number of characters to generate (1-20, default=5)
    
    Returns:
    - List of character dictionaries
    """
    import random
    import json
    from documents_narrative import CharacterRole
    from documents_actors import ActorRoleType, ActorImportance, CharacterArcType
    
    # 1. Extract Context from Scope & Project
    concept = scope.big_idea.get("content", "") if isinstance(scope.big_idea, dict) else str(scope.big_idea)
    theme = scope.theme.get("lesson", "") if isinstance(scope.theme, dict) else str(scope.theme)
    logline = scope.logline.get("premise", "") if isinstance(scope.logline, dict) else str(scope.logline)
    
    # Timeline contexts
    timeline = scope.timeline if isinstance(scope.timeline, dict) else {}
    social_context = timeline.get("social", "") or timeline.get("social_context", "")
    economic_context = timeline.get("economic", "") or timeline.get("economic_context", "")
    environment_context = timeline.get("environment", "") or timeline.get("environment_context", "")
    
    # Extract tags and genres
    tags = project.tags if hasattr(project, 'tags') and project.tags else []
    tags_str = ", ".join(tags) if tags else "None"
    genres = project.genres if hasattr(project, 'genres') else []
    genre_text = ", ".join([g.get("type", "") for g in genres if isinstance(g, dict)]) if genres else "General"
    
    print(f"🎯 AI Character Generation for '{project.script_name}'")
    print(f"   Genre: {genre_text}")
    print(f"   Theme: {theme[:50]}...")
    
    # 2. Build AI Prompt
    prompt = f"""You are a professional casting director and screenwriter.
Analyze the following story details to create {character_count} main characters.
Determine their GENDER, AGE, and ROLE based on the plot requirements.
Do NOT default to male protagonists unless it fits the genre/plot.
Ensure a balanced and inclusive cast appropriate for the story.

Story Details:
- Title: {project.script_name}
- Genre: {genre_text}
- Tags: {tags_str}
- Concept: {concept}
- Theme: {theme}
- Logline: {logline}
- Setting: {social_context}, {economic_context}, {environment_context}

Requirements:
1. Create exactly {character_count} characters.
2. Assign roles: 
   - 1 Protagonist (Lead)
   - 1 Antagonist (Lead) - ONLY if the story needs one, otherwise another Main character.
   - Remaining are Supporting characters (Friend, Mentor, Love Interest, etc.)
3. Determine Gender (Male/Female/Non-binary) based on the story logic.
4. Generate Thai names with 3 parts: Firstname, Lastname, and Nickname.
5. Define Personality, Appearance, and Goals.

Return ONLY a JSON array with this structure:
[
  {{
    "firstname": "Thai Firstname",
    "lastname": "Thai Lastname",
    "nickname": "Thai Nickname",
    "role": "protagonist|antagonist|main|support",
    "gender": "male|female|non-binary",
    "age": 25,
    "personality": "Detailed personality description in Thai",
    "appearance": "Physical appearance description in Thai",
    "goals": {{
      "objective": "What they want (External Goal) in Thai",
      "need": "What they need (Internal Need) in Thai",
      "action": "What they do to achieve it in Thai",
      "conflict": "What stands in their way in Thai",
      "backstory": "Brief backstory in Thai"
    }}
  }}
]
"""

    generated_characters = []
    
    # 3. Call AI Model
    try:
        print("🤖 Calling Ollama API for character generation...")
        print(f"   Model: qwen2.5:7b")
        print(f"   Characters requested: {character_count}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:  # 🔥 Increase timeout to 120s
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "num_predict": 2000  # Allow longer responses
                    }
                }
            )
            
            print(f"   Ollama response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                
                print(f"   Generated text length: {len(generated_text)} chars")
                print(f"   First 200 chars: {generated_text[:200]}")
                
                # Parse JSON
                try:
                    start_idx = generated_text.find('[')
                    end_idx = generated_text.rfind(']') + 1
                    if start_idx != -1 and end_idx > 0:
                        json_str = generated_text[start_idx:end_idx]
                        print(f"   Extracted JSON length: {len(json_str)} chars")
                        ai_data = json.loads(json_str)
                        print(f"   ✅ Parsed {len(ai_data)} characters from AI")
                        
                        # Validate and Map Data
                        for char_data in ai_data:
                            # Map Role string to Enum
                            role_str = char_data.get("role", "support").lower()
                            if "protagonist" in role_str:
                                role = CharacterRole.PROTAGONIST
                                actor_role = ActorRoleType.LEAD
                                importance = ActorImportance.CRITICAL
                                arc = CharacterArcType.TRANSFORMATION
                            elif "antagonist" in role_str:
                                role = CharacterRole.ANTAGONIST
                                actor_role = ActorRoleType.LEAD
                                importance = ActorImportance.CRITICAL
                                arc = CharacterArcType.NEGATIVE
                            elif "main" in role_str:
                                role = CharacterRole.MAIN
                                actor_role = ActorRoleType.SUPPORTING
                                importance = ActorImportance.HIGH
                                arc = CharacterArcType.POSITIVE
                            else:
                                role = CharacterRole.SUPPORT
                                actor_role = ActorRoleType.SUPPORTING
                                importance = ActorImportance.MEDIUM
                                arc = CharacterArcType.FLAT
                            
                            # Map Goals
                            goals = char_data.get("goals", {})
                            if not isinstance(goals, dict):
                                # Fallback if goals is string or missing
                                goals = {
                                    "objective": "ไม่ระบุ",
                                    "need": "ไม่ระบุ",
                                    "action": "ไม่ระบุ",
                                    "conflict": "ไม่ระบุ",
                                    "backstory": "ไม่ระบุ"
                                }
                            
                            # Construct Name
                            firstname = char_data.get("firstname", "")
                            lastname = char_data.get("lastname", "")
                            nickname = char_data.get("nickname", "")
                            
                            if firstname and lastname:
                                if nickname:
                                    full_name = f"{firstname} {lastname} ({nickname})"
                                else:
                                    full_name = f"{firstname} {lastname}"
                            else:
                                # Fallback to "name" field if AI used old format
                                full_name = char_data.get("name", "Unknown")
                            
                            # Construct Character Object
                            character = {
                                "name": full_name,
                                "role": role,
                                "actor_role_type": actor_role,
                                "actor_importance": importance,
                                "arc_type": arc,
                                "arc_name": arc.value,
                                "narrative_function": role_str,
                                "age": char_data.get("age", 30),
                                "gender": char_data.get("gender", "unknown"),
                                "personality": char_data.get("personality", ""),
                                "appearance": char_data.get("appearance", ""),
                                "goals": {
                                    "objective": goals.get("objective", "ไม่ระบุ"),
                                    "need": goals.get("need", "ไม่ระบุ"),
                                    "action": goals.get("action", "ไม่ระบุ"),
                                    "conflict": goals.get("conflict", "ไม่ระบุ"),
                                    "backstory": goals.get("backstory", "ไม่ระบุ")
                                },
                                # Backward compatibility
                                "motivation": goals.get("objective", ""),
                                "conflict": goals.get("conflict", ""),
                                "background": goals.get("backstory", "")
                            }
                            generated_characters.append(character)
                        
                        print(f"✅ AI successfully generated {len(generated_characters)} characters")
                        
                    else:
                        print("⚠️ No JSON array found in AI response")
                        print(f"   Response text: {generated_text[:500]}")
                except Exception as parse_err:
                    print(f"⚠️ JSON parsing failed: {parse_err}")
                    print(f"   Raw response: {generated_text[:500]}")
            else:
                print(f"⚠️ Ollama API returned status {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                
    except Exception as e:
        print(f"⚠️ AI character generation failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

    # 4. Fallback Logic (if AI failed or returned empty)
    if not generated_characters:
        print("📝 Using ENHANCED fallback templates with Step 1-2 data (AI failed)")
        print(f"   Building characters from: Theme='{theme[:50]}...', Logline='{logline[:50]}...'")
        
        # 🔥 ENHANCED: Build character details from actual Step 1-2 data
        genre_names = [g.get("type", "").lower() for g in genres if isinstance(g, dict)]
        dominant_genre = genre_names[0] if genre_names else "drama"
        
        # Extract key elements from theme and logline for character building
        theme_lower = theme.lower() if theme else ""
        logline_lower = logline.lower() if logline else ""
        concept_lower = concept.lower() if concept else ""
        
        # Character personality based on story theme
        protag_personality_traits = []
        if "รัก" in theme_lower or "love" in tags_str.lower():
            protag_personality_traits.append("อ่อนโยนและเปิดใจ")
        if "แค้น" in theme_lower or "revenge" in tags_str.lower():
            protag_personality_traits.append("มีความมุ่งมั่นแรงกล้า")
        if "ครอบครัว" in theme_lower or "family" in tags_str.lower():
            protag_personality_traits.append("ห่วงใยครอบครัวอย่างลึกซึ้ง")
        if "ความจริง" in theme_lower or "truth" in tags_str.lower():
            protag_personality_traits.append("มีความกล้าหาญและซื่อสัตย์")
        
        # Add genre-specific traits
        if dominant_genre in ["action", "thriller"]:
            protag_personality_traits.extend(["กล้าตัดสินใจ", "มีสติปัญญาและวางแผนได้ดี"])
        elif dominant_genre in ["romance", "drama"]:
            protag_personality_traits.extend(["มีอารมณ์ที่ละเอียดอ่อน", "เข้าใจความรู้สึกผู้อื่น"])
        elif dominant_genre in ["comedy"]:
            protag_personality_traits.extend(["มีอารมณ์ขัน", "มองโลกในแง่ดี"])
        else:
            protag_personality_traits.extend(["มุ่งมั่น", "เรียนรู้จากความผิดพลาด"])
        
        protag_personality = " เป็นคนที่" + " และ".join(protag_personality_traits) + f" โดยมีเป้าหมายสำคัญในชีวิตที่เกี่ยวข้องกับ {tags_str} ซึ่งขับเคลื่อนการกระทำของตัวละครตลอดเรื่อง"
        
        # Antagonist personality (opposite traits)
        antag_personality_traits = []
        if "แค้น" in theme_lower or "revenge" in tags_str.lower():
            antag_personality_traits.append("เย็นชา คำนวณ")
        if "อำนาจ" in theme_lower or "power" in tags_str.lower():
            antag_personality_traits.append("ต้องการควบคุมและครอบงำ")
        else:
            antag_personality_traits.append("ฉลาดเจ้าเล่ห์และมีเหตุผลในการกระทำ")
        
        antag_personality = " เป็นคนที่" + " และ".join(antag_personality_traits) + f" โดยมีจุดประสงค์ที่ขัดแย้งกับตัวเอกอย่างรุนแรง ซึ่งสะท้อนถึงความขัดแย้งหลักของเรื่องราวในธีม '{theme[:100]}'"
        
        # Goals based on actual story data
        protag_objective = f"ต้องการ{tags_str.split(',')[0] if tags_str else 'บรรลุเป้าหมาย'} และเอาชนะอุปสรรคที่ขัดขวางไว้ โดยเฉพาะ{concept[:150] if len(concept) > 10 else 'สถานการณ์ที่ท้าทายซึ่งต้องใช้ทั้งกำลังกายและกำลังใจ'} ซึ่งเป็นสิ่งที่จะทำให้ชีวิตของตัวละครเปลี่ยนแปลงไปตลอดกาล"
        
        protag_need = f"ต้องการการยอมรับและความเข้าใจจากผู้อื่น โดยเฉพาะในเรื่องของ{theme[:150] if len(theme) > 10 else 'ความเชื่อและค่านิยมส่วนตัว'} ซึ่งเป็นแรงขับภายในที่แท้จริงที่อยู่เบื้องหลังการกระทำทั้งหมด และเป็นสิ่งที่ตัวละครค้นพบเมื่อเรื่องราวดำเนินไป"
        
        protag_action = f"จะดำเนินการด้วยความมุ่งมั่นและกล้าหาญ โดยใช้ทั้ง{', '.join(protag_personality_traits[:2])} เพื่อเผชิญหน้ากับอุปสรรคในสภาพแวดล้อมที่{environment_context[:100] if len(environment_context) > 10 else 'ท้าทายและเต็มไปด้วยความไม่แน่นอน'} และสร้างเส้นทางของตนเองท่ามกลางความขัดแย้ง"
        
        protag_conflict = f"ต้องเผชิญกับ{antag_personality_traits[0] if antag_personality_traits else 'ศัตรูที่แข็งแกร่ง'} และความขัดแย้งภายในใจที่เกิดจาก{theme[:100] if len(theme) > 10 else 'ความกลัวและความไม่มั่นใจ'} ซึ่งทำให้การตัดสินใจแต่ละครั้งกลายเป็นการทดสอบจิตใจที่แท้จริง ท่ามกลางสภาพสังคมที่{social_context[:100] if len(social_context) > 10 else 'มีความซับซ้อนและความกดดัน'}"
        
        protag_backstory = f"เติบโตมาในสภาพแวดล้อมที่{social_context[:200] if len(social_context) > 20 else 'มีความท้าทายและหลากหลาย'} โดยมีประสบการณ์ในอดีตที่เกี่ยวข้องกับ{tags_str} ซึ่งหล่อหลอมบุคลิกภาพและมุมมองต่อโลก ทำให้มีความเชื่อมั่นใน{theme[:100] if len(theme) > 10 else 'คุณค่าและหลักการของตนเอง'} อย่างแน่วแน่ และมุ่งมั่นที่จะพิสูจน์ตัวเองท่ามกลางบริบททางเศรษฐกิจที่{economic_context[:150] if len(economic_context) > 10 else 'มีความผันผวนและแข่งขัน'} ซึ่งกลายเป็นแรงผลักดันสำคัญในการดำเนินชีวิต"
        
        male_names = [
            "ธนวัฒน์", "ภัทรพล", "วิศรุต", "ชัยวัฒน์", "สมชาย", "วิชัย", "ประสิทธิ์", 
            "อนุชา", "ธนากร", "รัชชานนท์", "กิตติพงศ์", "เจริญ", "พีระพล", "สุรศักดิ์"
        ]
        female_names = [
            "ปานรดา", "สมหญิง", "สุดา", "นันทนา", "วารุณี", "พิมพ์ใจ", "จันทร์จิรา",
            "ชญานิษ", "วรรณภา", "สิริพร", "ณัฐริกา", "พรรณนิภา", "อรอุมา", "เบญจมาศ"
        ]
        
        random.shuffle(male_names)
        random.shuffle(female_names)
        
        # Helper to get name
        m_idx, f_idx = 0, 0
        def get_name(g):
            nonlocal m_idx, f_idx
            if g == "male":
                n = male_names[m_idx % len(male_names)]; m_idx += 1; return n
            else:
                n = female_names[f_idx % len(female_names)]; f_idx += 1; return n

        # Randomize Protagonist Gender based on Genre?
        # Romance -> 50/50
        # Action -> 70/30 Male?
        # Let's just do 50/50 for Protagonist in fallback
        protag_gender = random.choice(["male", "female"])
        antag_gender = random.choice(["male", "female"])
        
        # Protagonist
        generated_characters.append({
            "name": get_name(protag_gender),
            "role": CharacterRole.PROTAGONIST,
            "actor_role_type": ActorRoleType.LEAD,
            "actor_importance": ActorImportance.CRITICAL,
            "arc_type": CharacterArcType.TRANSFORMATION,
            "arc_name": "transformation",
            "narrative_function": "protagonist",
            "age": 25 + random.randint(0, 10),
            "gender": protag_gender,
            "personality": protag_personality,  # 🔥 Use enhanced personality
            "appearance": f"รูปร่างสมส่วน มีบุคลิกที่โดดเด่นและเข้ากับบทบาทใน{dominant_genre} แต่งกายสะท้อนถึงสถานะและตัวตนที่{economic_context[:80] if len(economic_context) > 10 else 'เหมาะสมกับบริบทเรื่องราว'}",
            "goals": {
                "objective": protag_objective,  # 🔥 Use enhanced objective
                "need": protag_need,  # 🔥 Use enhanced need
                "action": protag_action,  # 🔥 Use enhanced action
                "conflict": protag_conflict,  # 🔥 Use enhanced conflict
                "backstory": protag_backstory  # 🔥 Use enhanced backstory
            },
            "motivation": protag_objective[:100],
            "conflict": protag_conflict[:100],
            "background": protag_backstory[:100]
        })
        
        # Antagonist (if needed)
        if character_count > 1:
            antag_objective = f"ต้องการขัดขวาง{tags_str.split(',')[0] if tags_str else 'เป้าหมายของตัวเอก'} เพราะมีความเชื่อและแรงจูงใจที่แตกต่างอย่างสิ้นเชิง โดยเฉพาะในเรื่องของ{theme[:100] if len(theme) > 10 else 'อำนาจและการควบคุม'} ซึ่งทำให้เกิดความขัดแย้งที่รุนแรงและซับซ้อน"
            
            antag_need = f"ต้องการการพิสูจน์และการยืนยันว่าวิธีการและความเชื่อของตนถูกต้อง แม้จะต้องเผชิญกับการต่อต้านจากตัวเอก โดยแรงขับเคลื่อนนี้มาจากประสบการณ์ในอดีตที่{social_context[:100] if len(social_context) > 10 else 'สร้างบาดแผลทางใจ'} และทำให้มุมมองต่อโลกเปลี่ยนไป"
            
            antag_backstory = f"มีประวัติที่เกี่ยวข้องกับ{tags_str} แต่ในทางตรงข้าม โดยเติบโตมาในสภาพแวดล้อมที่{social_context[:150] if len(social_context) > 20 else 'มีความขัดแย้งและความไม่ยุติธรรม'} ซึ่งหล่อหลอมให้กลายเป็นบุคคลที่มีมุมมองแบบนี้ และมีเหตุผลที่สมเหตุสมผลในการกระทำ ท่ามกลางบริบททางเศรษฐกิจที่{economic_context[:120] if len(economic_context) > 10 else 'สร้างความกดดันและการแข่งขัน'}"
            
            generated_characters.append({
                "name": get_name(antag_gender),
                "role": CharacterRole.ANTAGONIST,
                "actor_role_type": ActorRoleType.LEAD,
                "actor_importance": ActorImportance.CRITICAL,
                "arc_type": CharacterArcType.NEGATIVE,
                "arc_name": "negative",
                "narrative_function": "antagonist",
                "age": 35 + random.randint(0, 15),
                "gender": antag_gender,
                "personality": antag_personality,  # 🔥 Use enhanced personality
                "appearance": f"มีบุคลิกที่น่าเกรงขามและสร้างความประทับใจ สะท้อนถึงอำนาจและความมั่นใจในตัวเอง แต่งกายและท่าทางที่แสดงถึงสถานะที่{economic_context[:80] if len(economic_context) > 10 else 'สูงกว่าหรือเทียบเท่าตัวเอก'}",
                "goals": {
                    "objective": antag_objective,
                    "need": antag_need,
                    "action": f"ใช้อุบายและกลยุทธ์ที่{', '.join(antag_personality_traits)} เพื่อบรรลุเป้าหมาย โดยใช้ประโยชน์จากสภาพแวดล้อมและสถานการณ์ที่{environment_context[:100] if len(environment_context) > 10 else 'เอื้ออำนวย'}",
                    "conflict": f"ตัวเอกที่มีความมุ่งมั่นและพัฒนาตัวเองอย่างต่อเนื่อง ซึ่งท้าทายความเชื่อและแผนการที่วางไว้ ท่ามกลางการเปลี่ยนแปลงของสังคมที่{social_context[:100] if len(social_context) > 10 else 'ไม่เอื้อต่อวิธีการเดิมๆ'}",
                    "backstory": antag_backstory
                },
                "motivation": antag_objective[:100],
                "conflict": "ตัวเอกและการเปลี่ยนแปลง",
                "background": antag_backstory[:100]
            })
            
        # Fill the rest - Supporting Characters
        support_roles = ["เพื่อนสนิท", "พี่เลี้ยง/ผู้ให้คำปรึกษา", "คู่รัก/ความรักในอดีต", "คนในครอบครัว", "เพื่อนร่วมงาน", "คู่แข่ง"]
        while len(generated_characters) < character_count:
            g = random.choice(["male", "female"])
            role_name = support_roles[len(generated_characters) - 2] if len(generated_characters) - 2 < len(support_roles) else "ผู้สนับสนุน"
            
            support_personality = f"เป็นคนที่มีความสัมพันธ์ใกล้ชิดกับตัวเอกในฐานะ{role_name} โดยมีบุคลิกที่เป็นมิตรและให้การสนับสนุนในด้านต่างๆ แม้จะมีความกังวลและความกลัวบ้าง แต่ก็พร้อมที่จะยืนเคียงข้างเมื่อจำเป็น สะท้อนถึงค่านิยมของสังคมที่{social_context[:100] if len(social_context) > 10 else 'เน้นความสัมพันธ์และการช่วยเหลือกัน'}"
            
            support_objective = f"ช่วยเหลือและสนับสนุนตัวเอกในการบรรลุเป้าหมาย โดยเฉพาะในเรื่องของ{tags_str.split(',')[1] if ',' in tags_str else tags_str} ซึ่งเป็นสิ่งที่ตัวละครนี้มีความเชี่ยวชาญหรือประสบการณ์ และเชื่อว่าเป็นสิ่งที่ถูกต้อง"
            
            support_backstory = f"มีความสัมพันธ์ที่ยาวนานกับตัวเอก โดยเคยผ่านเหตุการณ์สำคัญร่วมกันในอดีต ซึ่งสร้างความผูกพันที่ลึกซึ้ง เติบโตมาในสภาพแวดล้อมที่{social_context[:120] if len(social_context) > 20 else 'มีความคล้ายคลึงหรือตรงข้ามกับตัวเอก'} ทำให้มีมุมมองที่เสริมหรือสร้างสมดุลให้กับทัศนคติของตัวเอก"
            
            generated_characters.append({
                "name": get_name(g),
                "role": CharacterRole.SUPPORT,
                "actor_role_type": ActorRoleType.SUPPORTING,
                "actor_importance": ActorImportance.MEDIUM,
                "arc_type": CharacterArcType.FLAT,
                "arc_name": "flat",
                "narrative_function": "supporter",
                "age": 20 + random.randint(0, 40),
                "gender": g,
                "personality": support_personality,  # 🔥 Use enhanced personality
                "appearance": f"มีรูปลักษณ์ที่เข้ากับบทบาทของ{role_name} แต่งกายและท่าทางสะท้อนถึงความสัมพันธ์กับตัวเอก รวมถึงบริบททางเศรษฐกิจที่{economic_context[:80] if len(economic_context) > 10 else 'เหมาะสมกับตัวตน'}",
                "goals": {
                    "objective": support_objective,
                    "need": f"การมีความสัมพันธ์ที่มั่นคงและได้รับความไว้วางใจ โดยเฉพาะจากตัวเอก ซึ่งเป็นแรงจูงใจสำคัญในการกระทำและการตัดสินใจ",
                    "action": f"ให้คำแนะนำ สนับสนุนทั้งด้านจิตใจและการกระทำ และพร้อมเสียสละเมื่อจำเป็น ท่ามกลางสถานการณ์ที่{environment_context[:80] if len(environment_context) > 10 else 'ท้าทาย'}",
                    "conflict": f"ความกลัวที่จะสูญเสียตัวเอกหรือความสัมพันธ์ที่มี รวมถึงความกังวลเกี่ยวกับผลที่ตามมาจากการกระทำของตัวเอก ซึ่งอาจส่งผลต่อทั้งสองฝ่าย",
                    "backstory": support_backstory
                },
                "motivation": support_objective[:100],
                "conflict": "ความกลัวการสูญเสีย",
                "background": support_backstory[:100]
            })

    return generated_characters[:character_count]
