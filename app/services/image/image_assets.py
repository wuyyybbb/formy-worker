"""
图像资源辅助方法
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

from app.core.config import settings

RESULTS_DIR = Path(settings.RESULT_DIR)
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_SUBDIRS = ("source", "reference", "other")


def resolve_uploaded_file(file_id: str) -> Path:
    """
    根据 file_id 定位上传图片
    Args:
        file_id: 上传接口返回的 file_id
    Returns:
        Path: 真实文件路径
    """
    if not file_id:
        raise ValueError("file_id 不能为空")
    if not UPLOAD_DIR.exists():
        raise FileNotFoundError("上传目录不存在")

    search_patterns = [UPLOAD_DIR / sub for sub in UPLOAD_SUBDIRS if (UPLOAD_DIR / sub).exists()]
    candidates: list[Path] = []
    for folder in search_patterns:
        candidates.extend(folder.glob(f"{file_id}.*"))

    if not candidates:
        candidates = list(UPLOAD_DIR.glob(f"**/{file_id}.*"))

    if not candidates:
        raise FileNotFoundError(f"未找到对应文件: {file_id}")

    return candidates[0]


def copy_image_to_results(source_path: Path, filename: Optional[str] = None) -> Path:
    """
    将图片拷贝到 results 目录
    Args:
        source_path: 原始文件路径
        filename: 目标文件名（可选）
    Returns:
        Path: 新文件路径
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    extension = source_path.suffix.lower() or ".jpg"
    target_name = filename or f"{source_path.stem}{extension}"
    if not target_name.lower().endswith(extension):
        target_name = f"{target_name}{extension}"
    target_path = RESULTS_DIR / target_name
    shutil.copyfile(source_path, target_path)
    return target_path


def create_comparison_image(before_path: Path, after_path: Path, filename: str) -> Path:
    """
    生成对比图（左右拼接）
    Args:
        before_path: 原图路径
        after_path: 结果图路径
        filename: 保存文件名
    Returns:
        Path: 生成文件路径
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    before = Image.open(before_path).convert("RGB")
    after = Image.open(after_path).convert("RGB")

    target_height = max(before.height, after.height)
    before = _resize_with_height(before, target_height)
    after = _resize_with_height(after, target_height)

    canvas = Image.new("RGB", (before.width + after.width, target_height), color=(0, 0, 0))
    canvas.paste(before, (0, 0))
    canvas.paste(after, (before.width, 0))

    divider_x = before.width
    draw = ImageDraw.Draw(canvas)
    draw.line([(divider_x, 0), (divider_x, target_height)], fill=(255, 255, 255), width=6)
    draw.line([(divider_x, 0), (divider_x, target_height)], fill=(0, 0, 0), width=2)

    target_path = RESULTS_DIR / filename
    canvas.save(target_path, format="JPEG", quality=95)
    return target_path


def _resize_with_height(image: Image.Image, target_height: int) -> Image.Image:
    """按高度等比缩放"""
    if image.height == target_height:
        return image
    ratio = target_height / image.height
    target_width = max(1, int(image.width * ratio))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

