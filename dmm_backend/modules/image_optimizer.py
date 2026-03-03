"""
Image Optimization Service
Handles multi-resolution thumbnail generation and compression for character images

Features:
- Generate multiple thumbnail sizes (256x256, 512x512)
- Optimize image quality while reducing file size
- Maintain aspect ratio with smart cropping
- Support PNG and JPEG formats
- Comprehensive error handling

Author: Peace Script Development Team
Created: 2025-11-11
"""

from PIL import Image
import io
import base64
from typing import Dict, Tuple, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    Image optimization and thumbnail generation service
    
    Generates optimized thumbnails for different use cases:
    - Small (256x256): Actor cards, profile avatars
    - Medium (512x512): Gallery grid preview
    - Large (1024x1024): Detail view (optional)
    
    Example:
        >>> optimizer = ImageOptimizer()
        >>> thumbnails = optimizer.create_thumbnails(
        ...     image_base64="iVBORw0KGgo...",
        ...     sizes=['small', 'medium']
        ... )
        >>> print(f"Small: {thumbnails['size_small_kb']:.1f} KB")
        >>> print(f"Medium: {thumbnails['size_medium_kb']:.1f} KB")
    """
    
    # Predefined thumbnail sizes
    THUMBNAIL_SIZES = {
        'small': (256, 256),     # Actor cards, avatars
        'medium': (512, 512),    # Gallery grid
        'large': (1024, 1024)    # Detail view
    }
    
    # Quality settings for different formats
    QUALITY_SETTINGS = {
        'PNG': {
            'optimize': False,    # ✨ DISABLE optimization to preserve quality
            'compress_level': 1   # ✨ MINIMAL compression (1 = fastest, least compression)
        },
        'JPEG': {
            'quality': 100,       # ✨ MAXIMUM quality (no lossy compression)
            'optimize': False,    # ✨ DISABLE optimization
            'subsampling': 0      # ✨ 4:4:4 chroma subsampling (highest quality)
        }
    }
    
    def __init__(self):
        """Initialize image optimizer"""
        logger.info("🎨 ImageOptimizer initialized")
    
    def create_thumbnails(
        self,
        image_base64: str,
        sizes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple thumbnail sizes from base64 image
        
        Args:
            image_base64: Original image in base64 format (without data URI prefix)
            sizes: List of sizes to generate ['small', 'medium', 'large']
                   Default: ['small', 'medium']
        
        Returns:
            Dictionary containing:
            {
                'thumbnail_small_base64': str,
                'thumbnail_medium_base64': str,
                'size_small_kb': float,
                'size_medium_kb': float,
                'original_size_kb': float,
                'original_dimensions': tuple
            }
        
        Raises:
            ValueError: If image_base64 is invalid
            IOError: If image cannot be decoded
        
        Example:
            >>> result = optimizer.create_thumbnails(
            ...     image_base64="iVBORw0KGgo...",
            ...     sizes=['small', 'medium']
            ... )
            >>> # Result contains optimized thumbnails
        """
        if sizes is None:
            sizes = ['small', 'medium']
        
        try:
            # Decode base64 to image
            image_data = base64.b64decode(image_base64)
            original_size_kb = len(image_data) / 1024
            
            image = Image.open(io.BytesIO(image_data))
            original_dimensions = image.size
            
            logger.info(f"📊 Original image: {original_dimensions[0]}x{original_dimensions[1]} ({original_size_kb:.1f} KB)")
            
            result = {
                'original_size_kb': round(original_size_kb, 2),
                'original_dimensions': original_dimensions
            }
            
            # Generate each requested thumbnail size
            for size_name in sizes:
                if size_name not in self.THUMBNAIL_SIZES:
                    logger.warning(f"⚠️ Unknown size '{size_name}', skipping")
                    continue
                
                target_size = self.THUMBNAIL_SIZES[size_name]
                
                # Create thumbnail
                thumbnail = self._create_single_thumbnail(
                    image=image,
                    target_size=target_size,
                    format='PNG'
                )
                
                # Convert to base64
                thumbnail_base64, thumbnail_size_kb = self._image_to_base64(
                    thumbnail,
                    format='PNG'
                )
                
                # Store in result
                result[f'thumbnail_{size_name}_base64'] = thumbnail_base64
                result[f'size_{size_name}_kb'] = round(thumbnail_size_kb, 2)
                
                logger.info(f"  ✅ {size_name.capitalize()}: {target_size[0]}x{target_size[1]} ({thumbnail_size_kb:.1f} KB)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creating thumbnails: {e}")
            raise ValueError(f"Failed to create thumbnails: {str(e)}")
    
    def _create_single_thumbnail(
        self,
        image: Image.Image,
        target_size: Tuple[int, int],
        format: str = 'PNG'
    ) -> Image.Image:
        """
        Create a single thumbnail with smart resizing
        
        Args:
            image: PIL Image object
            target_size: Target size (width, height)
            format: Output format ('PNG' or 'JPEG')
        
        Returns:
            Resized PIL Image
        
        Strategy:
        1. Calculate aspect ratios
        2. Resize to fit target while maintaining aspect ratio
        3. Center crop to exact target size if needed
        """
        # Make a copy to avoid modifying original
        img = image.copy()
        
        # Convert RGBA to RGB if saving as JPEG
        if format == 'JPEG' and img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha as mask
            img = background
        
        # Calculate aspect ratios
        original_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        
        # Resize strategy: thumbnail() maintains aspect ratio
        # We use LANCZOS for high-quality downsampling
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # If aspect ratios differ significantly, we might need to crop
        # For square thumbnails, center crop to exact size
        if abs(original_ratio - target_ratio) > 0.1:
            img = self._center_crop(img, target_size)
        
        return img
    
    def _center_crop(
        self,
        image: Image.Image,
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Center crop image to exact target size
        
        Args:
            image: PIL Image object
            target_size: Target size (width, height)
        
        Returns:
            Cropped PIL Image
        """
        current_width, current_height = image.size
        target_width, target_height = target_size
        
        # Calculate crop box (left, top, right, bottom)
        left = (current_width - target_width) // 2
        top = (current_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # Ensure we don't exceed image bounds
        left = max(0, left)
        top = max(0, top)
        right = min(current_width, right)
        bottom = min(current_height, bottom)
        
        return image.crop((left, top, right, bottom))
    
    def _image_to_base64(
        self,
        image: Image.Image,
        format: str = 'PNG',
        quality: Optional[int] = None
    ) -> Tuple[str, float]:
        """
        Convert PIL Image to base64 string
        
        Args:
            image: PIL Image object
            format: Output format ('PNG' or 'JPEG')
            quality: Quality setting (for JPEG, 0-100)
        
        Returns:
            Tuple of (base64_string, size_in_kb)
        """
        buffer = io.BytesIO()
        
        # Get quality settings
        save_kwargs = self.QUALITY_SETTINGS.get(format, {}).copy()
        if quality is not None and format == 'JPEG':
            save_kwargs['quality'] = quality
        
        # Save image to buffer
        image.save(buffer, format=format, **save_kwargs)
        
        # Get base64
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        size_kb = len(image_bytes) / 1024
        
        return image_base64, size_kb
    
    def optimize_quality(
        self,
        image_base64: str,
        quality: int = 85,
        format: str = 'PNG'
    ) -> Tuple[str, float, float]:
        """
        Optimize image quality and compression
        
        Args:
            image_base64: Base64 encoded image
            quality: Quality level (0-100 for JPEG, ignored for PNG)
            format: Target format ('PNG' or 'JPEG')
        
        Returns:
            Tuple of (optimized_base64, original_size_kb, optimized_size_kb)
        
        Example:
            >>> optimized, orig_size, new_size = optimizer.optimize_quality(
            ...     image_base64="iVBORw0...",
            ...     quality=85,
            ...     format='PNG'
            ... )
            >>> reduction = ((orig_size - new_size) / orig_size) * 100
            >>> print(f"Reduced by {reduction:.1f}%")
        """
        try:
            # Decode image
            image_data = base64.b64decode(image_base64)
            original_size_kb = len(image_data) / 1024
            
            image = Image.open(io.BytesIO(image_data))
            
            # Optimize
            optimized_base64, optimized_size_kb = self._image_to_base64(
                image=image,
                format=format,
                quality=quality
            )
            
            reduction = ((original_size_kb - optimized_size_kb) / original_size_kb) * 100
            logger.info(f"📉 Optimized: {original_size_kb:.1f} KB → {optimized_size_kb:.1f} KB ({reduction:.1f}% reduction)")
            
            return optimized_base64, original_size_kb, optimized_size_kb
            
        except Exception as e:
            logger.error(f"❌ Error optimizing image: {e}")
            raise ValueError(f"Failed to optimize image: {str(e)}")
    
    def get_image_info(
        self,
        image_base64: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive image information
        
        Args:
            image_base64: Base64 encoded image
        
        Returns:
            {
                'format': str,           # PNG, JPEG, etc.
                'mode': str,             # RGB, RGBA, etc.
                'width': int,
                'height': int,
                'size_kb': float,
                'aspect_ratio': float
            }
        
        Example:
            >>> info = optimizer.get_image_info("iVBORw0...")
            >>> print(f"{info['width']}x{info['height']} {info['format']}")
        """
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            size_kb = len(image_data) / 1024
            aspect_ratio = image.width / image.height
            
            info = {
                'format': image.format or 'Unknown',
                'mode': image.mode,
                'width': image.width,
                'height': image.height,
                'size_kb': round(size_kb, 2),
                'aspect_ratio': round(aspect_ratio, 3)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error getting image info: {e}")
            raise ValueError(f"Failed to get image info: {str(e)}")
    
    def validate_image(
        self,
        image_base64: str,
        max_size_kb: int = 5000,
        allowed_formats: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Validate image meets requirements
        
        Args:
            image_base64: Base64 encoded image
            max_size_kb: Maximum allowed size in KB
            allowed_formats: List of allowed formats (e.g., ['PNG', 'JPEG'])
        
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error description") if invalid
        
        Example:
            >>> is_valid, error = optimizer.validate_image(
            ...     image_base64="iVBORw0...",
            ...     max_size_kb=2000,
            ...     allowed_formats=['PNG']
            ... )
            >>> if not is_valid:
            ...     print(f"Invalid: {error}")
        """
        if allowed_formats is None:
            allowed_formats = ['PNG', 'JPEG', 'JPG']
        
        try:
            info = self.get_image_info(image_base64)
            
            # Check format
            if info['format'] not in allowed_formats:
                return False, f"Format '{info['format']}' not allowed. Allowed: {allowed_formats}"
            
            # Check size
            if info['size_kb'] > max_size_kb:
                return False, f"Image too large: {info['size_kb']:.1f} KB (max: {max_size_kb} KB)"
            
            # Check dimensions (reasonable limits)
            if info['width'] < 10 or info['height'] < 10:
                return False, f"Image too small: {info['width']}x{info['height']} (min: 10x10)"
            
            if info['width'] > 4096 or info['height'] > 4096:
                return False, f"Image too large: {info['width']}x{info['height']} (max: 4096x4096)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Convenience function for quick usage
def create_thumbnails_quick(
    image_base64: str,
    small: bool = True,
    medium: bool = True
) -> Dict[str, Any]:
    """
    Quick thumbnail generation function
    
    Args:
        image_base64: Base64 encoded image
        small: Generate 256x256 thumbnail
        medium: Generate 512x512 thumbnail
    
    Returns:
        Dictionary with thumbnails
    
    Example:
        >>> thumbs = create_thumbnails_quick("iVBORw0...")
        >>> small_thumb = thumbs['thumbnail_small_base64']
    """
    sizes = []
    if small:
        sizes.append('small')
    if medium:
        sizes.append('medium')
    
    optimizer = ImageOptimizer()
    return optimizer.create_thumbnails(image_base64, sizes=sizes)


if __name__ == "__main__":
    # Example usage and testing
    print("🎨 Image Optimizer Service")
    print("=" * 60)
    
    # Create a test image (simple colored square)
    test_image = Image.new('RGB', (1024, 768), color='blue')
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    test_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Test optimizer
    optimizer = ImageOptimizer()
    
    # Get info
    info = optimizer.get_image_info(test_base64)
    print(f"\n📊 Image Info:")
    print(f"   Format: {info['format']}")
    print(f"   Size: {info['width']}x{info['height']}")
    print(f"   File Size: {info['size_kb']:.1f} KB")
    
    # Create thumbnails
    print(f"\n🔄 Creating thumbnails...")
    result = optimizer.create_thumbnails(test_base64, sizes=['small', 'medium'])
    
    print(f"\n✅ Results:")
    print(f"   Original: {result['original_size_kb']:.1f} KB")
    print(f"   Small (256x256): {result['size_small_kb']:.1f} KB")
    print(f"   Medium (512x512): {result['size_medium_kb']:.1f} KB")
    
    total_reduction = ((result['original_size_kb'] - result['size_small_kb']) / result['original_size_kb']) * 100
    print(f"\n📉 Small thumbnail reduces size by {total_reduction:.1f}%")
    
    # Validate
    is_valid, error = optimizer.validate_image(test_base64, max_size_kb=1000)
    print(f"\n🔍 Validation: {'✅ Valid' if is_valid else f'❌ {error}'}")
    
    print("\n" + "=" * 60)
    print("✅ Image Optimizer Service ready!")
