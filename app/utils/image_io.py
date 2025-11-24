"""
图像 I/O 工具函数
提供图像的读取、保存、编码、解码等功能
"""
import base64
import io
from pathlib import Path
from typing import Optional, Tuple, Union
from PIL import Image


def load_image(image_path: str) -> Image.Image:
    """
    加载图片
    
    Args:
        image_path: 图片路径
        
    Returns:
        Image.Image: PIL Image 对象
    """
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        raise ValueError(f"加载图片失败: {image_path}, 错误: {e}")


def save_image(image: Image.Image, output_path: str, format: str = "JPEG", quality: int = 95):
    """
    保存图片
    
    Args:
        image: PIL Image 对象
        output_path: 输出路径
        format: 图片格式（JPEG, PNG, WEBP）
        quality: 质量（1-100）
    """
    try:
        # 确保输出目录存在
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果是 JPEG 格式且有 alpha 通道，转换为 RGB
        if format.upper() in ["JPEG", "JPG"] and image.mode in ["RGBA", "LA", "P"]:
            # 创建白色背景
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode in ["RGBA", "LA"] else None)
            image = background
        
        # 保存图片
        image.save(output_path, format=format, quality=quality)
        
    except Exception as e:
        raise ValueError(f"保存图片失败: {output_path}, 错误: {e}")


def image_to_base64(image: Union[Image.Image, str], format: str = "JPEG", quality: int = 95) -> str:
    """
    将图片转换为 base64 编码字符串
    
    Args:
        image: PIL Image 对象或图片路径
        format: 图片格式
        quality: 质量
        
    Returns:
        str: base64 编码字符串
    """
    try:
        # 如果是路径，先加载
        if isinstance(image, str):
            image = load_image(image)
        
        # 转换为 bytes
        buffer = io.BytesIO()
        
        # 处理 JPEG 格式的 alpha 通道
        if format.upper() in ["JPEG", "JPG"] and image.mode in ["RGBA", "LA", "P"]:
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode in ["RGBA", "LA"] else None)
            image = background
        
        image.save(buffer, format=format, quality=quality)
        image_bytes = buffer.getvalue()
        
        # 编码为 base64
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        return base64_str
        
    except Exception as e:
        raise ValueError(f"图片转 base64 失败: {e}")


def base64_to_image(base64_str: str) -> Image.Image:
    """
    将 base64 字符串转换为图片
    
    Args:
        base64_str: base64 编码字符串
        
    Returns:
        Image.Image: PIL Image 对象
    """
    try:
        # 移除可能的前缀（如 data:image/jpeg;base64,）
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]
        
        # 解码 base64
        image_bytes = base64.b64decode(base64_str)
        
        # 转换为 Image
        image = Image.open(io.BytesIO(image_bytes))
        
        return image
        
    except Exception as e:
        raise ValueError(f"base64 转图片失败: {e}")


def resize_image(
    image: Image.Image, 
    max_width: Optional[int] = None, 
    max_height: Optional[int] = None,
    maintain_aspect: bool = True
) -> Image.Image:
    """
    调整图片大小
    
    Args:
        image: PIL Image 对象
        max_width: 最大宽度
        max_height: 最大高度
        maintain_aspect: 保持宽高比
        
    Returns:
        Image.Image: 调整后的图片
    """
    width, height = image.size
    
    if not max_width and not max_height:
        return image
    
    if maintain_aspect:
        # 保持宽高比
        if max_width and max_height:
            ratio = min(max_width / width, max_height / height)
        elif max_width:
            ratio = max_width / width
        else:
            ratio = max_height / height
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
    else:
        # 不保持宽高比
        new_width = max_width or width
        new_height = max_height or height
    
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized


def create_thumbnail(image: Union[Image.Image, str], size: Tuple[int, int] = (256, 256)) -> Image.Image:
    """
    创建缩略图
    
    Args:
        image: PIL Image 对象或图片路径
        size: 缩略图尺寸
        
    Returns:
        Image.Image: 缩略图
    """
    # 如果是路径，先加载
    if isinstance(image, str):
        image = load_image(image)
    
    # 创建缩略图（保持宽高比）
    image_copy = image.copy()
    image_copy.thumbnail(size, Image.Resampling.LANCZOS)
    
    return image_copy


def get_image_info(image: Union[Image.Image, str]) -> dict:
    """
    获取图片信息
    
    Args:
        image: PIL Image 对象或图片路径
        
    Returns:
        dict: 图片信息
    """
    # 如果是路径，先加载
    if isinstance(image, str):
        image = load_image(image)
    
    return {
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "format": image.format or "Unknown",
        "size_bytes": len(image.tobytes()) if image.mode else 0
    }


def convert_format(image: Union[Image.Image, str], target_format: str) -> Image.Image:
    """
    转换图片格式
    
    Args:
        image: PIL Image 对象或图片路径
        target_format: 目标格式（JPEG, PNG, WEBP）
        
    Returns:
        Image.Image: 转换后的图片
    """
    # 如果是路径，先加载
    if isinstance(image, str):
        image = load_image(image)
    
    # 处理不同格式的颜色模式
    if target_format.upper() in ["JPEG", "JPG"]:
        if image.mode in ["RGBA", "LA", "P"]:
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode in ["RGBA", "LA"] else None)
            image = background
        elif image.mode not in ["RGB", "L"]:
            image = image.convert("RGB")
    elif target_format.upper() == "PNG":
        if image.mode not in ["RGBA", "RGB", "L", "LA"]:
            image = image.convert("RGBA")
    
    return image

