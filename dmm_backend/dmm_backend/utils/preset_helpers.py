"""
Helper utilities for Custom Presets System
Sprint 2: Days 9-16
Created: 28 ตุลาคม 2568
"""

from typing import Any, Dict, List, Union
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId


def to_dict_deep(obj: Any) -> Any:
    """
    Recursively convert Pydantic models to dictionaries
    Handles nested models, lists, datetime objects, and ObjectId
    """
    # Handle None
    if obj is None:
        return None
    
    # Handle ObjectId
    if isinstance(obj, ObjectId):
        return str(obj)
    
    # Handle Pydantic models
    if hasattr(obj, 'model_dump'):
        data = obj.model_dump()
        return {k: to_dict_deep(v) for k, v in data.items()}
    
    # Handle BaseModel (older Pydantic versions)
    if isinstance(obj, BaseModel):
        data = obj.dict() if hasattr(obj, 'dict') else obj.model_dump()
        return {k: to_dict_deep(v) for k, v in data.items()}
    
    # Handle dictionaries
    if isinstance(obj, dict):
        return {k: to_dict_deep(v) for k, v in obj.items()}
    
    # Handle lists
    if isinstance(obj, list):
        return [to_dict_deep(item) for item in obj]
    
    # Handle datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    # Return primitive types as-is
    return obj


def serialize_document(doc: Any) -> Dict[str, Any]:
    """
    Serialize Beanie document to JSON-compatible dict
    Handles nested models and special types
    """
    if doc is None:
        return None
    
    # Convert to dict first
    if hasattr(doc, 'model_dump'):
        data = doc.model_dump()
    elif hasattr(doc, 'dict'):
        data = doc.dict()
    else:
        data = dict(doc)
    
    # Deep convert all nested objects
    return to_dict_deep(data)


def serialize_documents(docs: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize list of Beanie documents
    """
    return [serialize_document(doc) for doc in docs]


def safe_model_validate(model_class: type, data: Any) -> Any:
    """
    Safely validate data with Pydantic model
    Handles both objects and dicts
    """
    if data is None:
        return None
    
    # If already the right type, return as-is
    if isinstance(data, model_class):
        return data
    
    # Convert to dict if it's a Pydantic model
    if hasattr(data, 'model_dump'):
        data = data.model_dump()
    elif hasattr(data, 'dict'):
        data = data.dict()
    
    # Deep convert to handle nested models
    data = to_dict_deep(data)
    
    # Validate with model
    return model_class.model_validate(data)


# Backward compatibility
def to_response(doc: Any, response_class: type) -> Any:
    """
    Convert Beanie document to response model
    Uses deep serialization to handle nested models
    """
    if doc is None:
        return None
    
    # Serialize to clean dict
    data = serialize_document(doc)
    
    # Validate with response model
    return response_class.model_validate(data)


def to_response_list(docs: List[Any], response_class: type) -> List[Any]:
    """
    Convert list of Beanie documents to response models
    """
    return [to_response(doc, response_class) for doc in docs]
