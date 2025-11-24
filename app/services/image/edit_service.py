"""
图像编辑服务
作为 Pipeline 的统一入口，负责根据编辑模式分发到对应的 Pipeline
"""
from typing import Optional

from app.services.image.dto import EditTaskInput, EditTaskResult
from app.services.image.enums import EditMode
from app.services.image.pipelines import (
    HeadSwapPipeline,
    BackgroundPipeline,
    PoseChangePipeline
)


class ImageEditService:
    """图像编辑服务类"""
    
    def __init__(self):
        """初始化图像编辑服务"""
        # 初始化各个 Pipeline（懒加载或预加载）
        self._pipelines = {}
    
    def execute_edit(self, task_input: EditTaskInput) -> EditTaskResult:
        """
        执行图像编辑
        
        Args:
            task_input: 任务输入
            
        Returns:
            EditTaskResult: 编辑结果
        """
        try:
            # 获取对应的 Pipeline
            pipeline = self._get_pipeline(task_input.mode)
            
            if not pipeline:
                return EditTaskResult(
                    success=False,
                    error_message=f"不支持的编辑模式: {task_input.mode}"
                )
            
            # 执行 Pipeline
            result = pipeline.execute(task_input)
            
            return result
            
        except Exception as e:
            return EditTaskResult(
                success=False,
                error_message=f"图像编辑失败: {str(e)}"
            )
    
    def _get_pipeline(self, mode: EditMode):
        """
        获取对应模式的 Pipeline
        
        Args:
            mode: 编辑模式
            
        Returns:
            Pipeline 实例
        """
        # 如果已创建，直接返回（缓存）
        if mode in self._pipelines:
            return self._pipelines[mode]
        
        # 根据模式创建对应的 Pipeline
        if mode == EditMode.HEAD_SWAP:
            pipeline = HeadSwapPipeline()
        elif mode == EditMode.BACKGROUND_CHANGE:
            pipeline = BackgroundPipeline()
        elif mode == EditMode.POSE_CHANGE:
            pipeline = PoseChangePipeline()
        else:
            return None
        
        # 缓存 Pipeline 实例
        self._pipelines[mode] = pipeline
        
        return pipeline
    
    def validate_config(self, mode: EditMode, config: dict) -> bool:
        """
        验证配置参数
        
        Args:
            mode: 编辑模式
            config: 配置字典
            
        Returns:
            bool: 是否有效
        """
        # TODO: 根据模式验证配置参数
        return True
    
    def get_supported_modes(self) -> list[str]:
        """
        获取支持的编辑模式列表
        
        Returns:
            list[str]: 模式列表
        """
        return [mode.value for mode in EditMode]


# 全局服务实例（单例模式）
_image_edit_service_instance: Optional[ImageEditService] = None


def get_image_edit_service() -> ImageEditService:
    """获取图像编辑服务实例（单例）"""
    global _image_edit_service_instance
    if _image_edit_service_instance is None:
        _image_edit_service_instance = ImageEditService()
    return _image_edit_service_instance

