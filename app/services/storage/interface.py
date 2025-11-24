"""
存储接口定义
"""
from abc import ABC, abstractmethod
from typing import Optional


class StorageInterface(ABC):
    """存储接口抽象类"""
    
    @abstractmethod
    async def save_file(
        self, 
        file_data: bytes, 
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        保存文件
        
        Args:
            file_data: 文件二进制数据
            filename: 文件名
            subdirectory: 子目录
            
        Returns:
            str: 文件路径
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_path: str) -> bytes:
        """
        读取文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bytes: 文件二进制数据
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """
        获取文件访问 URL
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 访问 URL
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否存在
        """
        pass

