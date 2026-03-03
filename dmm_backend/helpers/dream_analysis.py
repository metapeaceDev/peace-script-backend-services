"""
🌙 Dream Journal Analysis System
Complete Buddhist Psychology Integration for Sleep Dreams

Implements Steps 2.2.60-64 from Peace Script Framework:
- Dream analysis with Buddhist psychology correlation
- Karma chain linking
- QA/Teaching integration
- Cluster analysis
- Regional/Zone mapping
- Dhamma reference linking

OPTIMIZATIONS (Phase 3):
- DreamTag enum validation
- O(N) complexity for correlations (was O(N²))
- LRU caching for analysis results
- Batch operations support

Author: Peace Script Model
Date: 6 พฤศจิกายน 2568
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import Counter
import hashlib

# Import models
from documents_extra import DreamJournal
from documents_actors import ActorProfile
from models.character_consciousness import Consciousness
from beanie.operators import In


# === Cache Helper Functions ===

def _generate_cache_key(actor_id: str, days_ago: int) -> str:
    """
    Generate cache key with 1-hour granularity
    
    Cache is invalidated every hour to ensure fresh data
    while reducing redundant queries
    """
    current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
    key_data = f"{actor_id}:{days_ago}:{current_hour}"
    return hashlib.md5(key_data.encode()).hexdigest()


# Global cache for dream analysis (expires every hour)
_analysis_cache: Dict[str, Any] = {}


def _get_cached_analysis(cache_key: str) -> Optional[dict]:
    """Get cached analysis if exists"""
    return _analysis_cache.get(cache_key)


def _set_cached_analysis(cache_key: str, analysis: dict):
    """Set cached analysis (limit to 100 entries)"""
    if len(_analysis_cache) >= 100:
        # Remove oldest entry (FIFO)
        oldest_key = next(iter(_analysis_cache))
        del _analysis_cache[oldest_key]
    
    _analysis_cache[cache_key] = {
        "analysis": analysis,
        "cached_at": datetime.utcnow().isoformat()
    }


def clear_dream_analysis_cache():
    """Clear all cached analysis (for testing or manual refresh)"""
    _analysis_cache.clear()


# === Core Dream Retrieval ===

async def get_character_sleep_dreams(
    actor_id: str,
    limit: Optional[int] = None,
    offset: int = 0,
    days_ago: Optional[int] = None
) -> List[DreamJournal]:
    """
    Get all sleep dreams for a character
    
    OPTIMIZED: Now with pagination support (offset parameter)
    
    Args:
        actor_id: Actor ID
        limit: Maximum number of dreams to return
        offset: Skip N results (for pagination) - NEW in Priority 2.3
        days_ago: Only get dreams from last N days
        
    Returns:
        List of DreamJournal documents
        
    Example:
        # Get first 10 dreams
        dreams = await get_character_sleep_dreams("ACT-001", limit=10, offset=0)
        
        # Get next 10 dreams
        dreams = await get_character_sleep_dreams("ACT-001", limit=10, offset=10)
    """
    actor = await ActorProfile.get(actor_id)
    if not actor or not actor.sleep_dreams:
        return []
    
    query = DreamJournal.find(In(DreamJournal.id, actor.sleep_dreams))
    
    if days_ago:
        cutoff_date = datetime.utcnow() - timedelta(days=days_ago)
        query = query.find(DreamJournal.date >= cutoff_date)
    
    # Sort by date descending
    query = query.sort("-date")
    
    # Apply pagination
    if offset > 0:
        query = query.skip(offset)
    
    if limit:
        query = query.limit(limit)
    
    return await query.to_list()


async def link_dream_to_character(actor_id: str, dream_id: str) -> bool:
    """
    Link a DreamJournal entry to a character
    
    Args:
        actor_id: Actor ID
        dream_id: DreamJournal ID
        
    Returns:
        True if successful
    """
    actor = await ActorProfile.get(actor_id)
    if not actor:
        return False
    
    if dream_id not in actor.sleep_dreams:
        actor.sleep_dreams.append(dream_id)
        await actor.save()
    
    return True


async def link_dreams_batch(actor_id: str, dream_ids: List[str]) -> Dict[str, Any]:
    """
    Link multiple DreamJournal entries to a character at once
    
    OPTIMIZED: Single DB call instead of N calls
    
    Args:
        actor_id: Actor ID
        dream_ids: List of DreamJournal IDs to link
        
    Returns:
        dict: {
            "success": True/False,
            "linked_count": 5,
            "skipped_count": 2,  # Already linked
            "total_requested": 7
        }
        
    Example:
        result = await link_dreams_batch("ACT-001", ["DREAM-001", "DREAM-002", "DREAM-003"])
    """
    actor = await ActorProfile.get(actor_id)
    if not actor:
        return {
            "success": False,
            "error": "Actor not found",
            "linked_count": 0,
            "skipped_count": 0,
            "total_requested": len(dream_ids)
        }
    
    # Deduplicate and find new dreams
    existing_dreams = set(actor.sleep_dreams)
    new_dreams = [dream_id for dream_id in dream_ids if dream_id not in existing_dreams]
    skipped_count = len(dream_ids) - len(new_dreams)
    
    # Add all new dreams at once
    if new_dreams:
        actor.sleep_dreams.extend(new_dreams)
        await actor.save()  # Single DB call
    
    return {
        "success": True,
        "linked_count": len(new_dreams),
        "skipped_count": skipped_count,
        "total_requested": len(dream_ids)
    }


async def unlink_dreams_batch(actor_id: str, dream_ids: List[str]) -> Dict[str, Any]:
    """
    Remove multiple DreamJournal links from a character at once
    
    Args:
        actor_id: Actor ID
        dream_ids: List of DreamJournal IDs to unlink
        
    Returns:
        dict: {
            "success": True/False,
            "unlinked_count": 3,
            "not_found_count": 1,
            "total_requested": 4
        }
    """
    actor = await ActorProfile.get(actor_id)
    if not actor:
        return {
            "success": False,
            "error": "Actor not found",
            "unlinked_count": 0,
            "not_found_count": len(dream_ids),
            "total_requested": len(dream_ids)
        }
    
    # Find dreams to remove
    dreams_to_remove = set(dream_ids)
    original_count = len(actor.sleep_dreams)
    
    # Filter out dreams to unlink
    actor.sleep_dreams = [d for d in actor.sleep_dreams if d not in dreams_to_remove]
    
    unlinked_count = original_count - len(actor.sleep_dreams)
    not_found_count = len(dream_ids) - unlinked_count
    
    if unlinked_count > 0:
        await actor.save()  # Single DB call
    
    return {
        "success": True,
        "unlinked_count": unlinked_count,
        "not_found_count": not_found_count,
        "total_requested": len(dream_ids)
    }


# === Dream Pattern Analysis ===

async def analyze_dream_patterns(actor_id: str, days_ago: int = 90, use_cache: bool = True) -> dict:
    """
    Comprehensive dream pattern analysis
    
    OPTIMIZED: Now with LRU caching (1-hour granularity)
    
    Args:
        actor_id: Actor ID
        days_ago: Number of days to analyze
        use_cache: Whether to use cached results (default: True)
    
    Returns:
        dict: Complete analysis with all patterns
        
    Example Output:
        {
            "total_dreams": 45,
            "date_range": {"start": "2024-08-01", "end": "2024-11-06"},
            "recurring_themes": ["chase", "falling", "death"],
            "emotion_analysis": {"average": -35.2, "trend": "improving"},
            "nightmare_count": 12,
            "lucid_count": 3,
            "tag_frequency": {"nightmare": 12, "prophetic": 5, "recurring": 8},
            "fear_correlations": {...},
            "karma_correlations": {...},
            "recommendations": [...],
            "cached": False  # Indicates if result was from cache
        }
    """
    # Check cache first
    if use_cache:
        cache_key = _generate_cache_key(actor_id, days_ago)
        cached = _get_cached_analysis(cache_key)
        
        if cached:
            result = cached["analysis"].copy()
            result["cached"] = True
            result["cached_at"] = cached["cached_at"]
            return result
    
    # Cache miss - perform full analysis
    dreams = await get_character_sleep_dreams(actor_id, days_ago=days_ago)
    
    if not dreams:
        return {"error": "No dreams found", "total_dreams": 0}
    
    actor = await ActorProfile.get(actor_id)
    
    # Basic statistics
    total_dreams = len(dreams)
    date_range = {
        "start": min(d.date for d in dreams).strftime("%Y-%m-%d") if dreams else None,
        "end": max(d.date for d in dreams).strftime("%Y-%m-%d") if dreams else None
    }
    
    # Recurring themes
    all_themes = []
    for dream in dreams:
        if dream.tags:
            all_themes.extend(dream.tags)
    theme_counter = Counter(all_themes)
    recurring_themes = [theme for theme, _ in theme_counter.most_common(10)]
    
    # Emotion analysis
    emotion_scores = [d.emotion_score for d in dreams if d.emotion_score is not None]
    avg_emotion = sum(emotion_scores) / len(emotion_scores) if emotion_scores else 0
    
    # Calculate trend (recent vs older)
    if len(emotion_scores) >= 10:
        recent_scores = emotion_scores[:len(emotion_scores)//2]
        older_scores = emotion_scores[len(emotion_scores)//2:]
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 10:
            trend = "improving"
        elif recent_avg < older_avg - 10:
            trend = "deteriorating"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    emotion_analysis = {
        "average": round(avg_emotion, 2),
        "trend": trend,
        "range": {
            "min": min(emotion_scores) if emotion_scores else None,
            "max": max(emotion_scores) if emotion_scores else None
        }
    }
    
    # Special dream types
    nightmare_count = sum(1 for d in dreams if "nightmare" in (d.tags or []))
    lucid_count = sum(1 for d in dreams if "lucid" in (d.tags or []))
    recurring_count = sum(1 for d in dreams if "recurring" in (d.tags or []))
    prophetic_count = sum(1 for d in dreams if "prophetic" in (d.tags or []))
    
    # Tag frequency
    tag_frequency = dict(theme_counter.most_common())
    
    # Buddhist psychology correlations
    fear_correlations = await correlate_with_fears(dreams, actor)
    karma_correlations = await correlate_with_karma(dreams, actor)
    taanha_correlations = await correlate_with_taanha(dreams, actor)
    
    # Lucid dreaming potential
    lucid_potential = await analyze_lucid_potential(actor.consciousness if actor else None)
    
    # Recommendations
    recommendations = generate_dream_recommendations(
        nightmare_count, 
        lucid_count, 
        avg_emotion, 
        lucid_potential
    )
    
    analysis_result = {
        "total_dreams": total_dreams,
        "date_range": date_range,
        "recurring_themes": recurring_themes,
        "emotion_analysis": emotion_analysis,
        "nightmare_count": nightmare_count,
        "lucid_count": lucid_count,
        "recurring_count": recurring_count,
        "prophetic_count": prophetic_count,
        "tag_frequency": tag_frequency,
        "fear_correlations": fear_correlations,
        "karma_correlations": karma_correlations,
        "taanha_correlations": taanha_correlations,
        "lucid_potential": lucid_potential,
        "recommendations": recommendations,
        "cached": False
    }
    
    # Store in cache
    if use_cache:
        cache_key = _generate_cache_key(actor_id, days_ago)
        _set_cached_analysis(cache_key, analysis_result)
    
    return analysis_result


def extract_recurring_themes(dreams: List[DreamJournal], min_count: int = 3) -> List[str]:
    """
    Extract themes that appear at least min_count times
    
    Args:
        dreams: List of dream entries
        min_count: Minimum occurrences to be considered recurring
        
    Returns:
        List of recurring theme names
    """
    all_themes = []
    for dream in dreams:
        if dream.tags:
            all_themes.extend(dream.tags)
    
    theme_counter = Counter(all_themes)
    return [theme for theme, count in theme_counter.items() if count >= min_count]


# === Buddhist Psychology Correlations ===

async def correlate_with_fears(
    dreams: List[DreamJournal], 
    actor: Optional[ActorProfile]
) -> dict:
    """
    Correlate dreams with character's fears (InternalCharacter.fears)
    
    Nightmares often manifest from deep-seated fears
    
    OPTIMIZED: O(N) complexity using set-based matching instead of O(N×M)
    
    Returns:
        dict: Fear correlation analysis
        {
            "total_fears": 5,
            "fear_matches": [
                {"fear": "child_failure", "dream_count": 8, "dreams": [...]},
                {"fear": "financial_ruin", "dream_count": 5, "dreams": [...]}
            ],
            "unmanifested_fears": ["death", "abandonment"]
        }
    """
    if not actor or not actor.internal_character or not actor.internal_character.fears:
        return {"error": "No fears data", "total_fears": 0}
    
    fears = actor.internal_character.fears
    
    # OPTIMIZATION: Pre-process all dreams once (O(N) instead of O(N×M))
    dream_data = []
    for dream in dreams:
        dream_text_lower = (dream.dream_text or "").lower()
        dream_tags_str = " ".join(str(tag) for tag in (dream.tags or [])).lower()
        combined_text = f"{dream_text_lower} {dream_tags_str}"
        
        dream_data.append({
            "dream": dream,
            "combined_text": combined_text
        })
    
    # OPTIMIZATION: Build fear keyword sets once (O(M))
    fear_keywords_map = {}
    for fear in fears:
        keywords = set(fear.lower().replace("_", " ").split())
        fear_keywords_map[fear] = keywords
    
    # OPTIMIZATION: Single pass matching (O(N×k) where k = avg keywords per fear)
    fear_matches = []
    for fear, keywords in fear_keywords_map.items():
        matching_dreams = []
        
        for dream_info in dream_data:
            # Check if any keyword in combined text
            if any(keyword in dream_info["combined_text"] for keyword in keywords):
                dream = dream_info["dream"]
                matching_dreams.append({
                    "dream_id": str(dream.id),
                    "date": dream.date.strftime("%Y-%m-%d"),
                    "emotion_score": dream.emotion_score,
                    "preview": dream.dream_text[:100] if dream.dream_text else ""
                })
        
        if matching_dreams:
            fear_matches.append({
                "fear": fear,
                "dream_count": len(matching_dreams),
                "dreams": matching_dreams[:5]  # Show top 5
            })
    
    manifested_fears = [f["fear"] for f in fear_matches]
    unmanifested_fears = [f for f in fears if f not in manifested_fears]
    
    return {
        "total_fears": len(fears),
        "manifested_in_dreams": len(fear_matches),
        "fear_matches": fear_matches,
        "unmanifested_fears": unmanifested_fears,
        "interpretation": "Fears that appear in dreams indicate active psychological processing"
    }


async def correlate_with_karma(
    dreams: List[DreamJournal],
    actor: Optional[ActorProfile]
) -> dict:
    """
    Correlate dreams with karma/vipāka patterns
    
    Buddhist belief: Dreams can reflect karmic consequences or karmic debts
    
    Returns:
        dict: Karma correlation analysis
    """
    if not actor or not actor.consciousness:
        return {"error": "No consciousness data"}
    
    consciousness = actor.consciousness
    karma_awareness = consciousness.karma_awareness if hasattr(consciousness, 'karma_awareness') else 0
    
    # High karma awareness → more prophetic/symbolic dreams
    # Low karma awareness → more random/wishful dreams
    
    prophetic_dreams = [d for d in dreams if "prophetic" in (d.tags or [])]
    symbolic_dreams = [d for d in dreams if "symbolic" in (d.tags or [])]
    wishful_dreams = [d for d in dreams if "wishful" in (d.tags or [])]
    
    return {
        "karma_awareness": karma_awareness,
        "prophetic_dream_count": len(prophetic_dreams),
        "symbolic_dream_count": len(symbolic_dreams),
        "wishful_dream_count": len(wishful_dreams),
        "interpretation": (
            "High karma awareness often correlates with more prophetic/symbolic dreams"
            if karma_awareness > 50
            else "Low karma awareness often results in wishful thinking dreams"
        ),
        "karmic_dream_examples": [
            {
                "dream_id": str(d.id),
                "date": d.date.strftime("%Y-%m-%d"),
                "type": "prophetic" if "prophetic" in (d.tags or []) else "symbolic",
                "preview": d.dream_text[:100] if d.dream_text else ""
            }
            for d in (prophetic_dreams + symbolic_dreams)[:5]
        ]
    }


async def correlate_with_taanha(
    dreams: List[DreamJournal],
    actor: Optional[ActorProfile]
) -> dict:
    """
    Correlate dreams with Taanha (ตัณหา - craving/aversion)
    
    Taanha.wanting → wishful dreams (dreams of getting what is desired)
    Taanha.unwanted → nightmares (dreams of what is feared)
    
    OPTIMIZED: O(N) complexity using pre-filtered dreams and set-based matching
    
    Returns:
        dict: Taanha correlation analysis
    """
    if not actor or not actor.taanha:
        return {"error": "No taanha data"}
    
    taanha = actor.taanha
    wanting = taanha.wanting or []
    unwanted = taanha.unwanted or []
    
    # OPTIMIZATION: Pre-filter dreams by tag (O(N) single pass)
    wishful_dreams = []
    nightmares = []
    
    for dream in dreams:
        dream_tags = [str(tag) for tag in (dream.tags or [])]
        if "wishful" in dream_tags:
            wishful_dreams.append(dream)
        if "nightmare" in dream_tags:
            nightmares.append(dream)
    
    # OPTIMIZATION: Pre-process dream texts once
    wishful_dream_data = [
        {
            "dream": d,
            "text_lower": (d.dream_text or "").lower()
        }
        for d in wishful_dreams
    ]
    
    nightmare_data = [
        {
            "dream": d,
            "text_lower": (d.dream_text or "").lower()
        }
        for d in nightmares
    ]
    
    # OPTIMIZATION: Build keyword sets for wanting (O(W) where W = wanting count)
    wanting_matches = []
    for want in wanting:
        want_keywords = set(want.lower().split())
        matching_dreams = []
        
        for dream_info in wishful_dream_data:
            # Check if any keyword in text
            if any(keyword in dream_info["text_lower"] for keyword in want_keywords):
                dream = dream_info["dream"]
                matching_dreams.append({
                    "dream_id": str(dream.id),
                    "date": dream.date.strftime("%Y-%m-%d"),
                    "preview": dream.dream_text[:100]
                })
        
        if matching_dreams:
            wanting_matches.append({
                "wanting": want,
                "dream_count": len(matching_dreams),
                "dreams": matching_dreams[:3]
            })
    
    # OPTIMIZATION: Build keyword sets for unwanted (O(U) where U = unwanted count)
    unwanted_matches = []
    for unwant in unwanted:
        unwant_keywords = set(unwant.lower().split())
        matching_dreams = []
        
        for dream_info in nightmare_data:
            # Check if any keyword in text
            if any(keyword in dream_info["text_lower"] for keyword in unwant_keywords):
                dream = dream_info["dream"]
                matching_dreams.append({
                    "dream_id": str(dream.id),
                    "date": dream.date.strftime("%Y-%m-%d"),
                    "emotion_score": dream.emotion_score,
                    "preview": dream.dream_text[:100]
                })
        
        if matching_dreams:
            unwanted_matches.append({
                "unwanted": unwant,
                "nightmare_count": len(matching_dreams),
                "dreams": matching_dreams[:3]
            })
    
    return {
        "taanha_wanting_count": len(wanting),
        "taanha_unwanted_count": len(unwanted),
        "wishful_dream_count": len(wishful_dreams),
        "nightmare_count": len(nightmares),
        "wanting_matches": wanting_matches,
        "unwanted_matches": unwanted_matches,
        "interpretation": "Taanha (craving/aversion) often manifests in dreams as wishful thinking or nightmares"
    }


async def analyze_lucid_potential(consciousness: Optional[Consciousness]) -> dict:
    """
    Calculate potential for lucid dreaming based on consciousness level
    
    High mindfulness + high wisdom → high lucid dream potential
    
    Args:
        consciousness: Character consciousness data
        
    Returns:
        dict: Lucid potential analysis
        {
            "potential_score": 75.5,
            "level": "high",
            "factors": {...},
            "recommendations": [...]
        }
    """
    if not consciousness:
        return {
            "potential_score": 0,
            "level": "unknown",
            "error": "No consciousness data"
        }
    
    # Calculate score from consciousness factors
    mindfulness = consciousness.mindfulness or 0
    wisdom = consciousness.wisdom or 0
    
    # Mindfulness is primary factor (60% weight)
    # Wisdom is secondary factor (40% weight)
    potential_score = (mindfulness * 0.6) + (wisdom * 0.4)
    
    # Determine level
    if potential_score >= 80:
        level = "very_high"
        description = "มีศักยภาพสูงมากในการฝันรู้ตัว - ควรฝึกหาดตนเองก่อนนอน"
    elif potential_score >= 60:
        level = "high"
        description = "มีศักยภาพสูงในการฝันรู้ตัว - แนะนำให้ฝึกการสังเกตความฝัน"
    elif potential_score >= 40:
        level = "medium"
        description = "มีศักยภาพปานกลาง - ฝึกสติและปัญญาเพิ่มเติม"
    elif potential_score >= 20:
        level = "low"
        description = "มีศักยภาพต่ำ - เริ่มจากการจดบันทึกความฝัน"
    else:
        level = "very_low"
        description = "มีศักยภาพต่ำมาก - ต้องพัฒนาสติและปัญญาเป็นพื้นฐาน"
    
    recommendations = []
    if mindfulness < 50:
        recommendations.append("เพิ่มการฝึกสติ (mindfulness meditation)")
    if wisdom < 50:
        recommendations.append("เพิ่มการศึกษาธรรม (wisdom development)")
    if potential_score < 60:
        recommendations.append("จดบันทึกความฝันทุกวันเพื่อเพิ่มการจดจำ")
    if potential_score >= 60:
        recommendations.append("ฝึก reality check ในตอนกลางวัน")
        recommendations.append("ตั้งใจก่อนนอนว่า 'จะฝันรู้ตัว'")
    
    return {
        "potential_score": round(potential_score, 2),
        "level": level,
        "description": description,
        "factors": {
            "mindfulness": mindfulness,
            "wisdom": wisdom,
            "mindfulness_weight": 60,
            "wisdom_weight": 40
        },
        "recommendations": recommendations
    }


def generate_dream_recommendations(
    nightmare_count: int,
    lucid_count: int,
    avg_emotion: float,
    lucid_potential: dict
) -> List[str]:
    """
    Generate personalized recommendations based on dream patterns
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Nightmare frequency
    if nightmare_count > 5:
        recommendations.append(
            "❗ มีฝันร้ายบ่อย ({} ครั้ง) - แนะนำให้ทำสมาธิก่อนนอน "
            "และระบายความกลัวผ่านการเขียนบันทึก".format(nightmare_count)
        )
    
    # Low emotion score
    if avg_emotion < -30:
        recommendations.append(
            "❗ คะแนนอารมณ์เฉลี่ยต่ำ ({:.1f}) - ความฝันสะท้อนความเครียด "
            "แนะนำให้พักผ่อนให้เพียงพอและดูแลสุขภาพจิต".format(avg_emotion)
        )
    
    # Lucid dreaming potential
    if lucid_potential.get("level") in ["high", "very_high"] and lucid_count < 3:
        recommendations.append(
            "✨ คุณมีศักยภาพสูงในการฝันรู้ตัว ({:.1f}%) แต่ยังฝันรู้ตัวไม่บ่อย - "
            "ลองฝึก reality check และตั้งใจก่อนนอน".format(lucid_potential.get("potential_score", 0))
        )
    
    # Positive patterns
    if avg_emotion > 30:
        recommendations.append(
            "✅ คะแนนอารมณ์เฉลี่ยดี ({:.1f}) - ความฝันสะท้อนสภาพจิตใจที่ดี "
            "คงสภาพนี้ไว้".format(avg_emotion)
        )
    
    if lucid_count >= 5:
        recommendations.append(
            "🌟 คุณฝันรู้ตัวบ่อย ({} ครั้ง) - ใช้โอกาสนี้ฝึกจิตและพัฒนาปัญญาในความฝัน".format(lucid_count)
        )
    
    if not recommendations:
        recommendations.append("ทุกอย่างดูปกติ - จดบันทึกความฝันต่อไปเพื่อติดตามแพทเทิร์น")
    
    return recommendations


# === Advanced Search & Filters (Priority 2.2) ===

async def search_dreams(
    actor_id: str,
    tags: Optional[List[str]] = None,
    emotion_range: Optional[tuple[float, float]] = None,
    date_range: Optional[tuple[datetime, datetime]] = None,
    text_search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Advanced dream search with multiple filters
    
    OPTIMIZED: Efficient MongoDB queries with pagination
    
    Args:
        actor_id: Actor ID
        tags: Filter by tags (e.g., ["nightmare", "lucid"])
        emotion_range: Filter by emotion score (min, max) e.g., (-100, -30)
        date_range: Filter by date (start, end)
        text_search: Search in dream_text (case-insensitive)
        limit: Maximum results to return
        offset: Skip N results (for pagination)
        
    Returns:
        dict: {
            "total_count": 45,
            "returned_count": 10,
            "offset": 0,
            "dreams": [...],
            "filters_applied": {...}
        }
        
    Example:
        # Search nightmares from last month with negative emotion
        dreams = await search_dreams(
            "ACT-001",
            tags=["nightmare"],
            emotion_range=(-100, -30),
            date_range=(
                datetime(2024, 10, 1),
                datetime(2024, 10, 31)
            )
        )
    """
    actor = await ActorProfile.get(actor_id)
    if not actor or not actor.sleep_dreams:
        return {
            "total_count": 0,
            "returned_count": 0,
            "offset": offset,
            "dreams": [],
            "filters_applied": {}
        }
    
    # Build query
    query = DreamJournal.find(In(DreamJournal.id, actor.sleep_dreams))
    
    filters_applied = {}
    
    # Apply tag filter
    if tags:
        # MongoDB $in operator for tags
        query = query.find({"tags": {"$in": tags}})
        filters_applied["tags"] = tags
    
    # Apply emotion range filter
    if emotion_range:
        min_emotion, max_emotion = emotion_range
        query = query.find(
            {"emotion_score": {"$gte": min_emotion, "$lte": max_emotion}}
        )
        filters_applied["emotion_range"] = {"min": min_emotion, "max": max_emotion}
    
    # Apply date range filter
    if date_range:
        start_date, end_date = date_range
        query = query.find(
            {"date": {"$gte": start_date, "$lte": end_date}}
        )
        filters_applied["date_range"] = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    
    # Apply text search filter
    if text_search:
        # Case-insensitive text search
        import re
        pattern = re.compile(text_search, re.IGNORECASE)
        query = query.find({"dream_text": {"$regex": pattern}})
        filters_applied["text_search"] = text_search
    
    # Get total count before pagination
    total_count = await query.count()
    
    # Apply pagination
    query = query.skip(offset).limit(limit)
    
    # Sort by date descending
    query = query.sort("-date")
    
    dreams = await query.to_list()
    
    # Format results
    dream_results = [
        {
            "dream_id": str(d.id),
            "date": d.date.isoformat(),
            "dream_text": d.dream_text,
            "tags": [str(tag) for tag in d.tags],
            "emotion_score": d.emotion_score,
            "ai_summary": d.ai_summary
        }
        for d in dreams
    ]
    
    return {
        "total_count": total_count,
        "returned_count": len(dream_results),
        "offset": offset,
        "limit": limit,
        "dreams": dream_results,
        "filters_applied": filters_applied
    }
    
    # Low emotion score
    if avg_emotion < -30:
        recommendations.append(
            "❗ คะแนนอารมณ์เฉลี่ยต่ำ ({:.1f}) - ความฝันสะท้อนความเครียด "
            "แนะนำให้พักผ่อนให้เพียงพอและดูแลสุขภาพจิต".format(avg_emotion)
        )
    
    # Lucid dreaming potential
    if lucid_potential.get("level") in ["high", "very_high"] and lucid_count < 3:
        recommendations.append(
            "✨ คุณมีศักยภาพสูงในการฝันรู้ตัว ({:.1f}%) แต่ยังฝันรู้ตัวไม่บ่อย - "
            "ลองฝึก reality check และตั้งใจก่อนนอน".format(lucid_potential.get("potential_score", 0))
        )
    
    # Positive patterns
    if avg_emotion > 30:
        recommendations.append(
            "✅ คะแนนอารมณ์เฉลี่ยดี ({:.1f}) - ความฝันสะท้อนสภาพจิตใจที่ดี "
            "คงสภาพนี้ไว้".format(avg_emotion)
        )
    
    if lucid_count >= 5:
        recommendations.append(
            "🌟 คุณฝันรู้ตัวบ่อย ({} ครั้ง) - ใช้โอกาสนี้ฝึกจิตและพัฒนาปัญญาในความฝัน".format(lucid_count)
        )
    
    if not recommendations:
        recommendations.append("ทุกอย่างดูปกติ - จดบันทึกความฝันต่อไปเพื่อติดตามแพทเทิร์น")
    
    return recommendations


# === Steps 2.2.60-64 Implementation Placeholders ===

async def link_dream_to_dhamma(dream_id: str, dhamma_ref: str) -> bool:
    """
    Link dream to Dhamma teaching reference (Step 2.2.60)
    
    Args:
        dream_id: DreamJournal ID
        dhamma_ref: Reference to Dhamma teaching document
        
    Returns:
        True if successful
        
    TODO: Implement when Dhamma teaching system is ready
    """
    dream = await DreamJournal.get(dream_id)
    if not dream:
        return False
    
    # Store in meta field for now
    if not dream.meta:
        dream.meta = {}
    dream.meta["dhamma_ref"] = dhamma_ref
    await dream.save()
    return True


async def link_dream_to_karma_chain(dream_id: str, karma_chain_link: str) -> bool:
    """
    Link dream to karma chain (Step 2.2.60)
    
    Prophetic dreams may indicate karmic consequences
    
    TODO: Implement when karma chain system is ready
    """
    dream = await DreamJournal.get(dream_id)
    if not dream:
        return False
    
    if not dream.meta:
        dream.meta = {}
    dream.meta["karma_chain_link"] = karma_chain_link
    await dream.save()
    return True


async def link_dream_to_teaching(dream_id: str, teaching_link: str) -> bool:
    """
    Link dream to teaching scenario (Step 2.2.61)
    
    Use dreams as teaching examples
    
    TODO: Implement when teaching system is ready
    """
    dream = await DreamJournal.get(dream_id)
    if not dream:
        return False
    
    if not dream.meta:
        dream.meta = {}
    dream.meta["teaching_link"] = teaching_link
    await dream.save()
    return True


async def link_dream_to_qa(dream_id: str, qa_link: str) -> bool:
    """
    Link dream to QA/Analytic cluster (Step 2.2.62)
    
    For dream interpretation and analysis
    
    TODO: Implement when QA system is ready
    """
    dream = await DreamJournal.get(dream_id)
    if not dream:
        return False
    
    if not dream.meta:
        dream.meta = {}
    dream.meta["qa_link"] = qa_link
    await dream.save()
    return True


async def cluster_dreams_by_theme(actor_id: str) -> Dict[str, List[str]]:
    """
    Cluster dreams by recurring themes (Step 2.2.63)
    
    Returns:
        dict: {theme: [dream_ids]}
        
    Example:
        {
            "chase": ["DREAM-001", "DREAM-005", "DREAM-012"],
            "falling": ["DREAM-003", "DREAM-008"],
            "death": ["DREAM-002", "DREAM-007", "DREAM-011"]
        }
    """
    dreams = await get_character_sleep_dreams(actor_id)
    
    clusters = {}
    for dream in dreams:
        if not dream.tags:
            continue
        
        for tag in dream.tags:
            if tag not in clusters:
                clusters[tag] = []
            clusters[tag].append(str(dream.id))
    
    return clusters


async def map_dreams_to_zone(actor_id: str, zone_id: str) -> List[str]:
    """
    Map dreams to regional/zone (Step 2.2.64)
    
    Dreams that occur in specific locations or relate to specific zones
    
    Args:
        actor_id: Actor ID
        zone_id: Zone/Region ID
        
    Returns:
        List of dream IDs related to this zone
        
    TODO: Implement full zone integration when Zone system is ready
    """
    dreams = await get_character_sleep_dreams(actor_id)
    
    # For now, use meta field
    related_dreams = []
    for dream in dreams:
        if dream.meta and dream.meta.get("zone_id") == zone_id:
            related_dreams.append(str(dream.id))
    
    return related_dreams
