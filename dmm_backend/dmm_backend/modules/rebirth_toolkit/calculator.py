"""
Rebirth Calculator
==================
Calculate probable rebirth realm based on character's kamma ledger.

IMPORTANT: This is ADVISORY only - Creator makes the final decision.
This is NOT an automatic system.
"""

from typing import List
from .realms_reference import (
    THIRTY_ONE_REALMS,
    Realm,
    search_realms_by_kamma_score
)


class RebirthCalculator:
    """
    Calculate rebirth probability based on kamma
    
    This is a HELPER TOOL for Peace Script creators.
    NOT an automatic Samsara Cycle engine.
    """
    
    def __init__(self):
        self.realms = THIRTY_ONE_REALMS
    
    def calculate_kamma_score(self, kamma_ledger: dict) -> dict:
        """
        Calculate total kamma score from kamma ledger
        
        Returns:
        {
            "total_score": 25.5,
            "wholesome_score": 45.0,
            "unwholesome_score": -19.5,
            "breakdown": {...}
        }
        """
        # Wholesome kamma (positive scores)
        wholesome_breakdown = {}
        
        # Dana (Generosity)
        dana_score = self._calculate_dana_score(kamma_ledger)
        wholesome_breakdown["dana"] = dana_score
        
        # Sila (Morality)
        sila_score = self._calculate_sila_score(kamma_ledger)
        wholesome_breakdown["sila"] = sila_score
        
        # Bhavana (Mental Development)
        bhavana_score = self._calculate_bhavana_score(kamma_ledger)
        wholesome_breakdown["bhavana"] = bhavana_score
        
        # Metta/Karuna (Loving-kindness/Compassion)
        metta_score = self._calculate_metta_score(kamma_ledger)
        wholesome_breakdown["metta_karuna"] = metta_score
        
        wholesome_total = sum(wholesome_breakdown.values())
        
        # Unwholesome kamma (negative scores)
        unwholesome_breakdown = {}
        
        # Panatipata (Killing)
        panatipata_score = self._calculate_panatipata_score(kamma_ledger)
        unwholesome_breakdown["panatipata"] = panatipata_score
        
        # Adinnadana (Stealing)
        stealing_score = self._calculate_stealing_score(kamma_ledger)
        unwholesome_breakdown["adinnadana"] = stealing_score
        
        # Kamesu Micchacara (Sexual misconduct)
        sexual_misconduct_score = self._calculate_sexual_misconduct_score(kamma_ledger)
        unwholesome_breakdown["kamesu_micchacara"] = sexual_misconduct_score
        
        # Musavada (Lying)
        lying_score = self._calculate_lying_score(kamma_ledger)
        unwholesome_breakdown["musavada"] = lying_score
        
        # Lobha (Greed)
        lobha_score = self._calculate_lobha_score(kamma_ledger)
        unwholesome_breakdown["lobha"] = lobha_score
        
        # Dosa (Hatred)
        dosa_score = self._calculate_dosa_score(kamma_ledger)
        unwholesome_breakdown["dosa"] = dosa_score
        
        # Moha (Delusion)
        moha_score = self._calculate_moha_score(kamma_ledger)
        unwholesome_breakdown["moha"] = moha_score
        
        unwholesome_total = sum(unwholesome_breakdown.values())
        
        total_score = wholesome_total + unwholesome_total
        
        return {
            "total_score": round(total_score, 2),
            "wholesome_score": round(wholesome_total, 2),
            "unwholesome_score": round(unwholesome_total, 2),
            "wholesome_breakdown": wholesome_breakdown,
            "unwholesome_breakdown": unwholesome_breakdown,
        }
    
    def suggest_rebirth_realms(
        self,
        kamma_ledger: dict,
        top_n: int = 5
    ) -> List[dict]:
        """
        Suggest top N probable rebirth realms based on kamma
        
        Returns:
        [
            {
                "rank": 1,
                "realm_id": 6,
                "realm_name": "มนุษย์",
                "probability": 75.5,
                "kamma_match": "excellent",
                "description": "...",
                "recommendation": "แนะนำสูง"
            },
            ...
        ]
        """
        # Calculate kamma score
        kamma_result = self.calculate_kamma_score(kamma_ledger)
        total_score = kamma_result["total_score"]
        
        # Find matching realms
        matching_realms = search_realms_by_kamma_score(total_score)
        
        # Format results
        suggestions = []
        for idx, match in enumerate(matching_realms[:top_n], 1):
            # Extract realm and probability from match dict
            realm = match.get("realm")
            probability = match.get("probability", 0.0)
            
            # Skip if realm is None
            if not realm:
                continue
            
            # Determine match quality
            if probability >= 90:
                kamma_match = "excellent"
                recommendation = "แนะนำสูงสุด"
            elif probability >= 70:
                kamma_match = "good"
                recommendation = "แนะนำ"
            elif probability >= 50:
                kamma_match = "fair"
                recommendation = "พอใช้"
            else:
                kamma_match = "weak"
                recommendation = "ไม่แนะนำ"
            
            suggestions.append({
                "rank": idx,
                "realm_id": realm.id,
                "realm_name_th": realm.name_th,
                "realm_name_en": realm.name_en,
                "realm_name_pali": realm.name_pali,
                "category": realm.category.value,
                "category_name_th": realm.category_name_th,
                "probability": round(probability, 2),
                "kamma_match": kamma_match,
                "kamma_score": total_score,
                "realm_score_range": {
                    "min": realm.min_kamma_score,
                    "max": realm.max_kamma_score
                },
                "description_th": realm.description_th,
                "description_en": realm.description_en,
                "lifespan_years": realm.lifespan_years,
                "suffering_level": realm.suffering_level,
                "happiness_level": realm.happiness_level,
                "buddhist_reference": realm.buddhist_reference,
                "recommendation": recommendation,
                "special_notes": self._get_special_notes(realm, total_score)
            })
        
        return suggestions
    
    def explain_kamma_impact(self, kamma_ledger: dict) -> dict:
        """
        Explain how each kamma type impacts rebirth
        
        Educational feature for users to understand Buddhist cosmology
        """
        kamma_result = self.calculate_kamma_score(kamma_ledger)
        
        explanations = []
        
        # Wholesome explanations
        for kamma_type, score in kamma_result["wholesome_breakdown"].items():
            if score > 0:
                explanations.append({
                    "kamma_type": kamma_type,
                    "score": score,
                    "impact": "positive",
                    "explanation_th": self._get_wholesome_explanation(kamma_type, score),
                    "realm_tendency": self._get_realm_tendency(score)
                })
        
        # Unwholesome explanations
        for kamma_type, score in kamma_result["unwholesome_breakdown"].items():
            if score < 0:
                explanations.append({
                    "kamma_type": kamma_type,
                    "score": score,
                    "impact": "negative",
                    "explanation_th": self._get_unwholesome_explanation(kamma_type, score),
                    "realm_tendency": self._get_realm_tendency(score)
                })
        
        return {
            "total_kamma_score": kamma_result["total_score"],
            "impact_analysis": explanations,
            "overall_tendency": self._get_overall_tendency(kamma_result["total_score"]),
            "advice": self._get_dhamma_advice(kamma_result)
        }
    
    # ========================================
    # PRIVATE HELPER METHODS
    # ========================================
    
    def _calculate_dana_score(self, ledger: dict) -> float:
        """Calculate score from generosity (Dana)"""
        dana_count = ledger.get("dana", {}).get("count", 0)
        dana_intensity = ledger.get("dana", {}).get("average_intensity", 0)
        return dana_count * 10 * (1 + dana_intensity / 100)
    
    def _calculate_sila_score(self, ledger: dict) -> float:
        """Calculate score from morality (Sila)"""
        # Count abstentions from unwholesome acts
        panatipata_virati = ledger.get("panatipata_virati", {}).get("count", 0)
        adinnadana_virati = ledger.get("adinnadana_virati", {}).get("count", 0)
        
        return (panatipata_virati * 15) + (adinnadana_virati * 12)
    
    def _calculate_bhavana_score(self, ledger: dict) -> float:
        """Calculate score from mental development (meditation)"""
        meditation_count = ledger.get("meditation", {}).get("count", 0)
        meditation_duration = ledger.get("meditation", {}).get("total_hours", 0)
        
        return (meditation_count * 8) + (meditation_duration * 2)
    
    def _calculate_metta_score(self, ledger: dict) -> float:
        """Calculate score from loving-kindness"""
        metta_count = ledger.get("metta", {}).get("count", 0)
        karuna_count = ledger.get("karuna", {}).get("count", 0)
        
        return (metta_count * 12) + (karuna_count * 12)
    
    def _calculate_panatipata_score(self, ledger: dict) -> float:
        """Calculate score from killing (negative)"""
        panatipata_count = ledger.get("panatipata", {}).get("count", 0)
        severity = ledger.get("panatipata", {}).get("severity", 1.0)
        
        return -1 * panatipata_count * 15 * severity
    
    def _calculate_stealing_score(self, ledger: dict) -> float:
        """Calculate score from stealing (negative)"""
        stealing_count = ledger.get("adinnadana", {}).get("count", 0)
        return -1 * stealing_count * 10
    
    def _calculate_sexual_misconduct_score(self, ledger: dict) -> float:
        """Calculate score from sexual misconduct (negative)"""
        misconduct_count = ledger.get("kamesu_micchacara", {}).get("count", 0)
        return -1 * misconduct_count * 12
    
    def _calculate_lying_score(self, ledger: dict) -> float:
        """Calculate score from lying (negative)"""
        lying_count = ledger.get("musavada", {}).get("count", 0)
        return -1 * lying_count * 8
    
    def _calculate_lobha_score(self, ledger: dict) -> float:
        """Calculate score from greed (negative)"""
        lobha_count = ledger.get("lobha_actions", {}).get("count", 0)
        return -1 * lobha_count * 7
    
    def _calculate_dosa_score(self, ledger: dict) -> float:
        """Calculate score from hatred (negative)"""
        dosa_count = ledger.get("dosa_actions", {}).get("count", 0)
        return -1 * dosa_count * 9
    
    def _calculate_moha_score(self, ledger: dict) -> float:
        """Calculate score from delusion (negative)"""
        moha_count = ledger.get("moha_actions", {}).get("count", 0)
        return -1 * moha_count * 6
    
    def _get_special_notes(self, realm: Realm, kamma_score: float) -> List[str]:
        """Get special notes about the realm"""
        notes = []
        
        # Human realm special note
        if realm.id == 6:
            notes.append("⭐ ภพมนุษย์เป็นภพที่ดีที่สุดสำหรับการบรรลุธรรม")
        
        # Pure Abodes note
        if realm.id >= 24 and realm.id <= 28:
            notes.append("⚠️ สุทธาวาสภูมิเฉพาะพระอนาคามีเท่านั้น")
        
        # Asannasatta note
        if realm.id == 23:
            notes.append("⚠️ ภพนี้ไม่มีจิต ไม่สามารถบรรลุธรรมได้")
        
        # Hell realms note
        if realm.id <= 2:
            notes.append("⚠️ นรกมีทุกข์มาก ต้องใช้กาลนานกว่าจะหลุดพ้น")
        
        return notes
    
    def _get_wholesome_explanation(self, kamma_type: str, score: float) -> str:
        """Get Thai explanation for wholesome kamma"""
        explanations = {
            "dana": f"การให้ทาน (+{score:.1f} คะแนน) ช่วยให้เกิดในภพที่ดี มีทรัพย์สมบัติ",
            "sila": f"การรักษาศีล (+{score:.1f} คะแนน) ช่วยให้เกิดในสุคติภูมิ",
            "bhavana": f"การเจริญภาวนา (+{score:.1f} คะแนน) ช่วยให้เกิดในพรหมโลก",
            "metta_karuna": f"การมีเมตตากรุณา (+{score:.1f} คะแนน) ช่วยให้เกิดในเทวโลก"
        }
        return explanations.get(kamma_type, f"กุศลกรรม (+{score:.1f} คะแนน)")
    
    def _get_unwholesome_explanation(self, kamma_type: str, score: float) -> str:
        """Get Thai explanation for unwholesome kamma"""
        explanations = {
            "panatipata": f"การฆ่าสัตว์ ({score:.1f} คะแนน) เสี่ยงต่อการเกิดในอบายภูมิ",
            "adinnadana": f"การลักขโมย ({score:.1f} คะแนน) ทำให้ยากจน ลำบาก",
            "kamesu_micchacara": f"การประพฤติผิดในกาม ({score:.1f} คะแนน) เสี่ยงต่อทุคติ",
            "musavada": f"การโกหก ({score:.1f} คะแนน) ทำให้ขาดความน่าเชื่อถือ",
            "lobha": f"ความโลภ ({score:.1f} คะแนน) เสี่ยงต่อเปรตภูมิ",
            "dosa": f"ความโกรธ ({score:.1f} คะแนน) เสี่ยงต่ออสุรกาย",
            "moha": f"ความหลง ({score:.1f} คะแนน) เสี่ยงต่อดิรัจฉานภูมิ"
        }
        return explanations.get(kamma_type, f"อกุศลกรรม ({score:.1f} คะแนน)")
    
    def _get_realm_tendency(self, score: float) -> str:
        """Get realm tendency based on score"""
        if score >= 100:
            return "รูปพรหมภูมิ"
        elif score >= 50:
            return "เทวภูมิ"
        elif score >= 10:
            return "มนุษย์"
        elif score >= -10:
            return "อสุรกาย"
        elif score >= -40:
            return "ดิรัจฉาน"
        elif score >= -70:
            return "เปรต"
        else:
            return "นรก"
    
    def _get_overall_tendency(self, total_score: float) -> dict:
        """Get overall rebirth tendency"""
        if total_score >= 90:
            return {
                "tendency": "รูปพรหมภูมิ",
                "description": "มีแนวโน้มสูงที่จะเกิดเป็นพรหม เนื่องจากมีกรรมดีมาก"
            }
        elif total_score >= 50:
            return {
                "tendency": "เทวภูมิ",
                "description": "มีแนวโน้มที่จะเกิดเป็นเทวดา เนื่องจากมีกรรมดี"
            }
        elif total_score >= 10:
            return {
                "tendency": "มนุษย์",
                "description": "มีแนวโน้มที่จะเกิดเป็นมนุษย์อีก เนื่องจากมีกรรมดีปานกลาง"
            }
        elif total_score >= -10:
            return {
                "tendency": "อสุรกาย",
                "description": "เสี่ยงต่อการเกิดเป็นอสูรกาย เนื่องจากมีความโกรธและอิจฉา"
            }
        elif total_score >= -40:
            return {
                "tendency": "ดิรัจฉาน",
                "description": "เสี่ยงต่อการเกิดเป็นสัตว์เดรัจฉาน เนื่องจากมีความโง่เขลา"
            }
        elif total_score >= -70:
            return {
                "tendency": "เปรต",
                "description": "เสี่ยงสูงต่อการเกิดเป็นเปรต เนื่องจากความโลภและตระหนี่"
            }
        else:
            return {
                "tendency": "นรก",
                "description": "เสี่ยงสูงมากต่อการเกิดในนรก เนื่องจากกระทำอกุศลกรรมหนัก"
            }
    
    def _get_dhamma_advice(self, kamma_result: dict) -> str:
        """Get Dhamma advice based on kamma analysis"""
        total_score = kamma_result["total_score"]
        
        if total_score >= 50:
            return "กรรมดีของท่านเป็นกุศลมาก แต่อย่าลืมว่าเป้าหมายสูงสุดคือพระนิพพาน ควรเจริญวิปัสสนาต่อไป"
        elif total_score >= 10:
            return "กรรมของท่านดีพอสมควร แนะนำให้ทำบุญเพิ่มเติม และเจริญสมถภาวนา"
        elif total_score >= -10:
            return "ควรระวังอกุศลกรรม โดยเฉพาะความโกรธและอิจฉา ควรเจริญเมตตาภาวนา"
        elif total_score >= -40:
            return "อกุศลกรรมค่อนข้างมาก ควรรักษาศีล ให้ทาน และเจริญสติ"
        else:
            return "อกุศลกรรมหนักมาก ควรสำนึกผิด รักษาศีล 5 อย่างเคร่งครัด และให้ทานเพื่อบรรเทาอกุศล"


# ========================================
# CONVENIENCE FUNCTION
# ========================================

def quick_calculate_rebirth(kamma_ledger: dict) -> dict:
    """
    Quick calculation for API endpoints
    Returns kamma score + top 3 realm suggestions
    """
    calculator = RebirthCalculator()
    
    kamma_result = calculator.calculate_kamma_score(kamma_ledger)
    suggestions = calculator.suggest_rebirth_realms(kamma_ledger, top_n=3)
    impact_analysis = calculator.explain_kamma_impact(kamma_ledger)
    
    return {
        "kamma_analysis": kamma_result,
        "top_realms": suggestions,
        "impact_explanation": impact_analysis,
        "disclaimer": "⚠️ นี่เป็นคำแนะนำเท่านั้น Creator ตัดสินใจเองได้เสมอ"
    }
