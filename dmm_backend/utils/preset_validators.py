"""
Preset Validation Utilities
============================
Comprehensive validation rules for preset data.

Validation Categories:
- Name validation (length, characters, uniqueness)
- Description validation (length, format)
- Parameter validation (types, ranges, options)
- Category validation (allowed values)
- Config validation (structure, completeness)
"""

import re
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status


class PresetValidator:
    """Comprehensive validator for preset data."""
    
    # Validation constants
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    
    ALLOWED_CATEGORIES = [
        "shot_composition",
        "lighting",
        "camera_movement",
        "genre_style",
        "emotion_focus",
        "technical",
        "creative"
    ]
    
    ALLOWED_VISIBILITIES = ["private", "team", "organization", "public", "system"]
    
    ALLOWED_PARAMETER_TYPES = ["range", "select", "boolean", "text", "color"]
    
    # Regex patterns
    NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_()ก-๙]+$')
    
    @staticmethod
    def validate_preset_name(name: str, field_name: str = "name") -> None:
        """
        Validate preset name.
        
        Rules:
        - Required (not empty)
        - Length: 3-100 characters
        - Allowed characters: letters, numbers, spaces, hyphens, underscores, Thai characters
        - No leading/trailing whitespace
        
        Args:
            name: Preset name to validate
            field_name: Name of field for error messages
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} is required"
            )
        
        name_stripped = name.strip()
        
        if len(name_stripped) < PresetValidator.MIN_NAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be at least {PresetValidator.MIN_NAME_LENGTH} characters"
            )
        
        if len(name_stripped) > PresetValidator.MAX_NAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must not exceed {PresetValidator.MAX_NAME_LENGTH} characters"
            )
        
        if name != name_stripped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} cannot have leading or trailing whitespace"
            )
        
        if not PresetValidator.NAME_PATTERN.match(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} contains invalid characters (allowed: letters, numbers, spaces, -, _, (), Thai)"
            )
    
    @staticmethod
    def validate_description(description: Optional[str]) -> None:
        """
        Validate preset description.
        
        Rules:
        - Optional
        - Max length: 500 characters
        
        Args:
            description: Description to validate
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if description and len(description) > PresetValidator.MAX_DESCRIPTION_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Description must not exceed {PresetValidator.MAX_DESCRIPTION_LENGTH} characters"
            )
    
    @staticmethod
    def validate_category(category: str) -> None:
        """
        Validate preset category.
        
        Rules:
        - Required
        - Must be in allowed list
        
        Args:
            category: Category to validate
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required"
            )
        
        if category not in PresetValidator.ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Allowed: {', '.join(PresetValidator.ALLOWED_CATEGORIES)}"
            )
    
    @staticmethod
    def validate_visibility(visibility: str) -> None:
        """
        Validate preset visibility.
        
        Rules:
        - Required
        - Must be in allowed list
        
        Args:
            visibility: Visibility to validate
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if not visibility:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Visibility is required"
            )
        
        if visibility not in PresetValidator.ALLOWED_VISIBILITIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid visibility. Allowed: {', '.join(PresetValidator.ALLOWED_VISIBILITIES)}"
            )
    
    @staticmethod
    def validate_parameter(param: Dict[str, Any], param_index: int) -> None:
        """
        Validate individual parameter configuration.
        
        Rules:
        - name: required, non-empty string
        - type: required, must be in allowed types
        - value: required (appropriate for type)
        - For range type: min_value and max_value required
        - For select type: options list required
        
        Args:
            param: Parameter dict to validate
            param_index: Index for error messages
            
        Raises:
            HTTPException: 400 if validation fails
        """
        # Validate name
        if "name" not in param or not param["name"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter {param_index}: name is required"
            )
        
        # Validate type
        if "type" not in param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter {param_index} ({param['name']}): type is required"
            )
        
        param_type = param["type"]
        if param_type not in PresetValidator.ALLOWED_PARAMETER_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter {param_index} ({param['name']}): invalid type '{param_type}'. Allowed: {', '.join(PresetValidator.ALLOWED_PARAMETER_TYPES)}"
            )
        
        # Validate value
        if "value" not in param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parameter {param_index} ({param['name']}): value is required"
            )
        
        # Type-specific validation
        if param_type == "range":
            # For range, value should be numeric
            if not isinstance(param["value"], (int, float)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parameter {param_index} ({param['name']}): range type requires numeric value"
                )
            
            # Check min/max if provided
            if "min_value" in param and param["value"] < param["min_value"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parameter {param_index} ({param['name']}): value below minimum"
                )
            
            if "max_value" in param and param["value"] > param["max_value"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parameter {param_index} ({param['name']}): value exceeds maximum"
                )
        
        elif param_type == "select":
            # For select, options must be provided
            if "options" not in param or not param["options"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parameter {param_index} ({param['name']}): select type requires options list"
                )
            
            # Value must be in options
            if param["value"] not in param["options"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parameter {param_index} ({param['name']}): value must be one of the options"
                )
        
        elif param_type == "boolean":
            # For boolean, value must be bool
            if not isinstance(param["value"], bool):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parameter {param_index} ({param['name']}): boolean type requires true/false value"
                )
    
    @staticmethod
    def validate_parameters(parameters: List[Dict[str, Any]]) -> None:
        """
        Validate list of parameters.
        
        Rules:
        - At least one parameter required
        - Each parameter must pass individual validation
        - Parameter names must be unique
        
        Args:
            parameters: List of parameter dicts
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if not parameters or len(parameters) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one parameter is required"
            )
        
        # Check for duplicate parameter names
        param_names = [p.get("name") for p in parameters if "name" in p]
        if len(param_names) != len(set(param_names)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameter names must be unique"
            )
        
        # Validate each parameter
        for idx, param in enumerate(parameters, 1):
            PresetValidator.validate_parameter(param, idx)
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """
        Validate preset config structure.
        
        Rules:
        - Must contain 'parameters' key
        - Parameters must be valid list
        
        Args:
            config: Config dict to validate
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Config is required"
            )
        
        if "parameters" not in config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Config must contain 'parameters' key"
            )
        
        parameters = config["parameters"]
        if not isinstance(parameters, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Config parameters must be a list"
            )
        
        PresetValidator.validate_parameters(parameters)
    
    @staticmethod
    def validate_preset_create(
        name: str,
        category: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        visibility: Optional[str] = "private"
    ) -> None:
        """
        Validate complete preset creation data.
        
        Validates:
        - Name
        - Category
        - Visibility
        - Description
        - Config
        
        Args:
            name: Preset name
            category: Preset category
            config: Preset configuration
            description: Optional description
            visibility: Visibility level
            
        Raises:
            HTTPException: 400 if any validation fails
        """
        PresetValidator.validate_preset_name(name)
        PresetValidator.validate_category(category)
        PresetValidator.validate_visibility(visibility or "private")
        PresetValidator.validate_description(description)
        PresetValidator.validate_config(config)
    
    @staticmethod
    def validate_preset_update(data: Dict[str, Any]) -> None:
        """
        Validate preset update data.
        
        Only validates fields that are present.
        
        Args:
            data: Update data dict
            
        Raises:
            HTTPException: 400 if validation fails
        """
        if "name" in data:
            PresetValidator.validate_preset_name(data["name"])
        
        if "category" in data:
            PresetValidator.validate_category(data["category"])
        
        if "visibility" in data:
            PresetValidator.validate_visibility(data["visibility"])
        
        if "description" in data:
            PresetValidator.validate_description(data["description"])
        
        if "config" in data:
            PresetValidator.validate_config(data["config"])
