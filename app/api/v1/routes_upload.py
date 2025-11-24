"""
文件上传相关路由
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime
from pathlib import Path

from app.schemas.image import UploadImageResponse
from app.services.storage import get_local_storage
from app.utils.id_generator import generate_file_id

router = APIRouter()


# 允许的文件类型
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

# 最大文件大小（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload", response_model=UploadImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    purpose: str = Form(default="source")
):
    """
    上传图片
    
    Args:
        file: 上传的文件
        purpose: 用途（source: 原图, reference: 参考图）
        
    Returns:
        UploadImageResponse: 上传结果
    """
    # 1. 验证文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持的格式: JPG, PNG, WEBP"
        )
    
    # 2. 读取文件数据
    file_data = await file.read()
    file_size = len(file_data)
    
    # 3. 验证文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制（最大 10MB）"
        )
    
    # 4. 生成文件名
    file_id = generate_file_id()
    file_extension = ALLOWED_TYPES[file.content_type]
    new_filename = f"{file_id}{file_extension}"
    
    # 5. 根据用途确定子目录
    subdirectory = purpose if purpose in ["source", "reference"] else "other"
    
    # 6. 保存文件
    try:
        storage = get_local_storage()
        relative_path = await storage.save_file(
            file_data=file_data,
            filename=new_filename,
            subdirectory=subdirectory
        )
        
        # 7. 获取访问 URL
        file_url = storage.get_url(relative_path)
        
        # 8. 返回响应
        return UploadImageResponse(
            file_id=file_id,
            filename=file.filename or new_filename,
            size=file_size,
            url=file_url,
            uploaded_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"文件保存失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"文件保存失败: {str(e)}"
        )

