"""
图片相关的数据传输对象
"""
from pydantic import BaseModel, Field
from datetime import datetime


class UploadImageResponse(BaseModel):
    """图片上传响应"""
    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    url: str = Field(..., description="访问URL")
    uploaded_at: str = Field(..., description="上传时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ImageInfo(BaseModel):
    """图片信息"""
    file_id: str
    filename: str
    size: int
    width: int
    height: int
    format: str
    url: str

