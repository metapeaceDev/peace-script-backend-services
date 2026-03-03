"""
Rebirth Toolkit Module
======================
Optional helper tools for cross-lifetime character creation in Peace Script.

This module provides:
- 31 Realms Reference (Educational)
- Rebirth Calculator (Advisory)
- Template Generator (Helper)

NOT a full automatic Samsara Cycle (that's for VistraPeace Phase 2).
"""

from .realms_reference import (
    Realm,
    RealmCategory,
    THIRTY_ONE_REALMS,
    get_realm_by_id,
    get_realms_by_category,
    search_realms_by_kamma_score
)

from .calculator import RebirthCalculator
from .template import (
    RebirthTemplate,
    RebirthTemplateGenerator,
    quick_create_template,
    create_flashback_characters
)

__all__ = [
    "Realm",
    "RealmCategory",
    "THIRTY_ONE_REALMS",
    "get_realm_by_id",
    "get_realms_by_category",
    "search_realms_by_kamma_score",
    "RebirthCalculator",
    "RebirthTemplate",
    "RebirthTemplateGenerator",
    "quick_create_template",
    "create_flashback_characters",
]
