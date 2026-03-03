"""
Mock Data Generator for Kamma-Vipāka Graph System

This module provides utilities to generate sample kamma data for testing
the Kamma-Vipāka Graph Explorer API endpoints.

Author: Digital Mind Model Team
Date: November 6, 2024
Version: 1.0
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
from uuid import uuid4

from kamma_engine import (
    KammaStorage, 
    KammaRecord, 
    KammaType,
    KammaTiming,
    KammaFunction,
    KammaStrength,
    VipakaType
)


# Predefined kamma scenarios with Buddhist accuracy
KUSALA_SCENARIOS = [
    {
        "citta_name": "KUSALA01_SOMANASSA_ÑANA",
        "description": "ทำบุญถวายภัตตาหารแก่พระสงฆ์",
        "potency_range": (0.7, 0.9),
        "timing": KammaTiming.DITTHADHAMMA_VEDANIYA,
        "strength": KammaStrength.ACINNA
    },
    {
        "citta_name": "KUSALA05_SOMANASSA_SASANKHARA",
        "description": "ปฏิบัติสมาธิภาวนา 1 ชั่วโมง",
        "potency_range": (0.8, 1.0),
        "timing": KammaTiming.UPAPAJJA_VEDANIYA,
        "strength": KammaStrength.GARUKA
    },
    {
        "citta_name": "KUSALA03_UPEKKHA_ÑANA",
        "description": "รักษาศีล 5 ตลอดวัน",
        "potency_range": (0.6, 0.8),
        "timing": KammaTiming.APARA_PARIYA_VEDANIYA,
        "strength": KammaStrength.ACINNA
    },
    {
        "citta_name": "KUSALA02_SOMANASSA_ASANKHARA",
        "description": "แบ่งปันความรู้ธรรมะแก่ผู้อื่น",
        "potency_range": (0.75, 0.95),
        "timing": KammaTiming.DITTHADHAMMA_VEDANIYA,
        "strength": KammaStrength.ASANNA
    },
    {
        "citta_name": "KUSALA06_UPEKKHA_SASANKHARA",
        "description": "ช่วยเหลือผู้ประสบภัยน้ำท่วม",
        "potency_range": (0.85, 1.0),
        "timing": KammaTiming.UPAPAJJA_VEDANIYA,
        "strength": KammaStrength.GARUKA
    },
]

AKUSALA_SCENARIOS = [
    {
        "citta_name": "DOSA02_DOMANASSA_PATIGHA_SASANKHARA",
        "description": "โกรธและด่าทอผู้อื่น",
        "potency_range": (0.6, 0.8),
        "timing": KammaTiming.DITTHADHAMMA_VEDANIYA,
        "strength": KammaStrength.ASANNA
    },
    {
        "citta_name": "LOBHA05_UPEKKHA_SASANKHARA",
        "description": "โลภอยากได้ของของผู้อื่น",
        "potency_range": (0.5, 0.7),
        "timing": KammaTiming.APARA_PARIYA_VEDANIYA,
        "strength": KammaStrength.ACINNA
    },
    {
        "citta_name": "MOHA02_UPEKKHA_VICIKICCHA",
        "description": "ประมาทไม่สนใจความรับผิดชอบ",
        "potency_range": (0.4, 0.6),
        "timing": KammaTiming.APARA_PARIYA_VEDANIYA,
        "strength": KammaStrength.KATATTA
    },
    {
        "citta_name": "LOBHA03_SOMANASSA_SASANKHARA",
        "description": "พูดโกหกเพื่อหลีกเลี่ยงความผิด",
        "potency_range": (0.7, 0.9),
        "timing": KammaTiming.DITTHADHAMMA_VEDANIYA,
        "strength": KammaStrength.ASANNA
    },
    {
        "citta_name": "DOSA01_DOMANASSA_PATIGHA_ASANKHARA",
        "description": "อิจฉาริษยาความสำเร็จของผู้อื่น",
        "potency_range": (0.6, 0.8),
        "timing": KammaTiming.APARA_PARIYA_VEDANIYA,
        "strength": KammaStrength.ACINNA
    },
]

VIPAKA_TYPES_KUSALA = [
    VipakaType.MENTAL_RESULT,
    VipakaType.HEALTH,
    VipakaType.WEALTH,
    VipakaType.WISDOM,
]

VIPAKA_TYPES_AKUSALA = [
    VipakaType.MENTAL_RESULT,
    VipakaType.HEALTH,
    VipakaType.BODY_QUALITY,
]


def generate_kamma_record(
    index: int,
    base_date: datetime,
    kamma_type: Optional[str] = None
) -> KammaRecord:
    """
    Generate a single kamma record with realistic Buddhist data.
    
    Args:
        index: Sequential index for the record
        base_date: Base datetime for record creation
        kamma_type: "kusala", "akusala", or None (random)
    
    Returns:
        KammaRecord with complete data
    """
    # Determine kamma type
    if kamma_type is None:
        kamma_type = random.choice(["kusala", "akusala"])
    
    # Select scenario
    scenarios = KUSALA_SCENARIOS if kamma_type == "kusala" else AKUSALA_SCENARIOS
    scenario = random.choice(scenarios)
    
    # Generate record ID
    kamma_id = f"kamma_{kamma_type}_{index:03d}_{uuid4().hex[:8]}"
    
    # Generate timestamp (within last 90 days for current life)
    days_ago = random.randint(0, 90)
    created_at = base_date - timedelta(days=days_ago)
    
    # Generate potency
    potency = random.uniform(*scenario["potency_range"])
    
    # Create kamma type enum
    kamma_enum = KammaType.KUSALA if kamma_type == "kusala" else KammaType.AKUSALA
    
    # Determine if ripened (30% chance)
    has_ripened = random.random() < 0.3
    ripened_at = None
    vipaka_type = None
    
    if has_ripened:
        ripened_at = created_at + timedelta(days=random.randint(1, 30))
        if kamma_type == "kusala":
            vipaka_type = random.choice(VIPAKA_TYPES_KUSALA)
        else:
            vipaka_type = random.choice(VIPAKA_TYPES_AKUSALA)
    
    # Create record
    record = KammaRecord(
        kamma_id=kamma_id,
        created_at=created_at,
        source_citta_id=f"citta_moment_{index}",
        source_citta_name=scenario["citta_name"],
        kamma_type=kamma_enum,
        potency=potency,
        timing=scenario["timing"],
        function=KammaFunction.JANAKA,
        strength=scenario["strength"],
        has_ripened=has_ripened,
        ripened_at=ripened_at,
        vipaka_type=vipaka_type,
        notes=scenario["description"]
    )
    
    return record


def generate_causality_chain(
    start_index: int,
    base_date: datetime,
    chain_length: int = 3
) -> List[KammaRecord]:
    """
    Generate a chain of related kamma records (cause-effect sequence).
    
    Args:
        start_index: Starting index for record IDs
        base_date: Base datetime
        chain_length: Number of records in chain (2-5)
    
    Returns:
        List of KammaRecord objects forming a causality chain
    """
    chain = []
    current_type = random.choice(["kusala", "akusala"])
    
    for i in range(chain_length):
        record = generate_kamma_record(
            index=start_index + i,
            base_date=base_date - timedelta(days=i*7),  # Weekly spacing
            kamma_type=current_type
        )
        
        # Add causality note
        if i > 0:
            prev_id = chain[i-1].kamma_id
            base_notes = record.notes or ""
            record.notes = f"{base_notes} | ผลจาก: {prev_id}"
        
        chain.append(record)
        
        # Occasionally switch type (transformation)
        if random.random() < 0.3:
            current_type = "kusala" if current_type == "akusala" else "akusala"
    
    return chain


def generate_mock_kamma_storage(
    character_id: str,
    num_records: int = 20,
    num_chains: int = 3
) -> KammaStorage:
    """
    Generate a complete KammaStorage with realistic test data.
    
    Args:
        character_id: Character/model ID
        num_records: Total number of individual records to generate
        num_chains: Number of causality chains to generate
    
    Returns:
        KammaStorage populated with mock data
    """
    storage = KammaStorage(character_id=character_id)
    base_date = datetime.now()
    record_index = 0
    
    # Generate causality chains (higher quality interconnected data)
    for _ in range(num_chains):
        chain = generate_causality_chain(
            start_index=record_index,
            base_date=base_date,
            chain_length=random.randint(3, 5)
        )
        
        for record in chain:
            storage.add_kamma(record)
            record_index += 1
    
    # Generate individual records to fill remaining quota
    remaining = num_records - record_index
    for _ in range(remaining):
        record = generate_kamma_record(
            index=record_index,
            base_date=base_date
        )
        storage.add_kamma(record)
        record_index += 1
    
    return storage


def get_sample_character_data() -> Dict[str, Any]:
    """
    Get a sample character profile for testing with embedded kamma storage.
    
    Returns:
        Dict with character data including kamma_storage field
    """
    character_id = f"test_char_{uuid4().hex[:8]}"
    storage = generate_mock_kamma_storage(
        character_id=character_id,
        num_records=20,
        num_chains=3
    )
    
    total_records = len(storage.active_kusala) + len(storage.active_akusala) + \
                   len(storage.ripened_kusala) + len(storage.ripened_akusala)
    
    return {
        "model_id": character_id,
        "name": "พระเทส เทสรังสี",
        "description": "Test character for Kamma-Vipāka Graph Explorer",
        "created_at": datetime.now(),
        "kamma_storage": storage.dict(),
        "test_metadata": {
            "generated_by": "kamma_mock_data.py",
            "total_records": total_records,
            "kusala_count": storage.total_kusala_created,
            "akusala_count": storage.total_akusala_created,
        }
    }


def print_storage_summary(storage: KammaStorage) -> None:
    """Print a human-readable summary of KammaStorage contents."""
    all_records = (storage.active_kusala + storage.active_akusala + 
                   storage.ripened_kusala + storage.ripened_akusala)
    
    print(f"\n{'='*60}")
    print(f"Kamma Storage Summary for: {storage.character_id}")
    print(f"{'='*60}")
    print(f"Total Records: {len(all_records)}")
    
    print(f"\nActive Kamma:")
    print(f"  Kusala: {len(storage.active_kusala)} records")
    print(f"  Akusala: {len(storage.active_akusala)} records")
    
    print(f"\nRipened Kamma:")
    print(f"  Kusala: {len(storage.ripened_kusala)} records")
    print(f"  Akusala: {len(storage.ripened_akusala)} records")
    
    print(f"\nStatistics:")
    print(f"  Total Kusala Created: {storage.total_kusala_created}")
    print(f"  Total Akusala Created: {storage.total_akusala_created}")
    print(f"  Total Kusala Ripened: {storage.total_kusala_ripened}")
    print(f"  Total Akusala Ripened: {storage.total_akusala_ripened}")
    
    print(f"\nSample Records:")
    for i, record in enumerate(all_records[:3]):
        status = "✓ Ripened" if record.has_ripened else "○ Active"
        print(f"\n  {i+1}. [{record.kamma_type.value}] {status}")
        print(f"     Citta: {record.source_citta_name}")
        print(f"     Potency: {record.potency:.2f} | Strength: {record.strength.value}")
        print(f"     Notes: {record.notes}")
        if record.has_ripened and record.vipaka_type:
            print(f"     Vipāka: {record.vipaka_type.value}")
    
    print(f"{'='*60}\n")


# Example usage for testing
if __name__ == "__main__":
    print("Kamma Mock Data Generator - Example Usage\n")
    
    # Generate storage
    storage = generate_mock_kamma_storage(
        character_id="demo_character_001",
        num_records=20,
        num_chains=3
    )
    
    # Print summary
    print_storage_summary(storage)
    
    # Show sample character data
    print("\nSample Character Data Structure:")
    char_data = get_sample_character_data()
    print(f"Model ID: {char_data['model_id']}")
    print(f"Name: {char_data['name']}")
    print(f"Kamma Records: {char_data['test_metadata']['total_records']}")
    print(f"  - Kusala: {char_data['test_metadata']['kusala_count']}")
    print(f"  - Akusala: {char_data['test_metadata']['akusala_count']}")
