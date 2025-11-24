"""
本地文件系统存储实现
"""
import os
import aiofiles
from pathlib import Path
from typing import Optional

from app.services.storage.interface import StorageInterface
from app.core.config import settings


class LocalStorage(StorageInterface):
    """本地文件系统存储"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化本地存储
        
        Args:
            base_dir: 基础存储目录
        """
        self.base_dir = base_dir or settings.UPLOAD_DIR
        self._ensure_directory_exists(self.base_dir)
    
    def _ensure_directory_exists(self, directory: str):
        """确保目录存在"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, file_path: str) -> str:
        """获取完整路径"""
        return os.path.join(self.base_dir, file_path)
    
    async def save_file(
        self, 
        file_data: bytes, 
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        保存文件到本地
        
        Args:
            file_data: 文件二进制数据
            filename: 文件名
            subdirectory: 子目录
            
        Returns:
            str: 相对文件路径
        """
        # 构建保存路径
        if subdirectory:
            save_dir = os.path.join(self.base_dir, subdirectory)
            self._ensure_directory_exists(save_dir)
            relative_path = os.path.join(subdirectory, filename)
        else:
            relative_path = filename
        
        full_path = self._get_full_path(relative_path)
        
        # 异步写入文件
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(file_data)
        
        return relative_path
    
    async def get_file(self, file_path: str) -> bytes:
        """
        读取文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bytes: 文件二进制数据
        """
        full_path = self._get_full_path(file_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            full_path = self._get_full_path(file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            
            return False
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    def get_url(self, file_path: str) -> str:
        """
        获取文件访问 URL
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 访问 URL
        """
        # 返回相对 URL，由前端拼接完整 URL
        # 或者可以返回完整 URL（如果有配置域名）
        return f"/uploads/{file_path}"
    
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否存在
        """
        full_path = self._get_full_path(file_path)
        return os.path.exists(full_path)


# 全局存储实例（单例）
_local_storage_instance: Optional[LocalStorage] = None


def get_local_storage() -> LocalStorage:
    """获取本地存储实例（单例）"""
    global _local_storage_instance
    if _local_storage_instance is None:
        _local_storage_instance = LocalStorage()
    return _local_storage_instance

