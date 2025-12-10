"""
Pipeline 基类
定义所有 Pipeline 的通用接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable
import time

from app.services.image.dto import EditTaskInput, EditTaskResult
from app.services.image.enums import ProcessingStep


class PipelineBase(ABC):
    """Pipeline 基类"""
    
    def __init__(self):
        """初始化 Pipeline"""
        self.start_time: Optional[float] = None
        self.progress_callback: Optional[Callable[[int, str], None]] = None
    
    @abstractmethod
    def execute(self, task_input: EditTaskInput) -> EditTaskResult:
        """
        执行 Pipeline（抽象方法，子类必须实现）
        
        Args:
            task_input: 任务输入
            
        Returns:
            EditTaskResult: 任务结果
        """
        pass
    
    @abstractmethod
    def validate_input(self, task_input: EditTaskInput) -> bool:
        """
        验证输入参数（抽象方法，子类必须实现）
        
        Args:
            task_input: 任务输入
            
        Returns:
            bool: 是否有效
        """
        pass
    
    def _start_timer(self):
        """开始计时"""
        self.start_time = time.time()
    
    def _get_elapsed_time(self) -> float:
        """
        获取已用时间
        
        Returns:
            float: 已用时间（秒）
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def _update_progress(self, progress: int, step: str):
        """
        更新进度
        
        Args:
            progress: 进度百分比（0-100）
            step: 当前步骤描述
        """
        if self.progress_callback:
            self.progress_callback(progress, step)
    
    def _create_success_result(
        self, 
        output_image: str, 
        thumbnail: Optional[str] = None,
        metadata: Optional[dict] = None,
        comparison_image: Optional[str] = None,
    ) -> EditTaskResult:
        """
        创建成功结果
        
        Args:
            output_image: 输出图片路径
            thumbnail: 缩略图路径
            metadata: 元数据
            
        Returns:
            EditTaskResult: 结果对象
        """
        return EditTaskResult(
            success=True,
            output_image=output_image,
            thumbnail=thumbnail,
            comparison_image=comparison_image,
            metadata=metadata or {},
            processing_time=self._get_elapsed_time()
        )
    
    def _create_error_result(self, error_message: str, error_code: str = "PIPELINE_ERROR") -> EditTaskResult:
        """
        创建错误结果
        
        Args:
            error_message: 错误信息
            error_code: 错误码
            
        Returns:
            EditTaskResult: 结果对象
        """
        return EditTaskResult(
            success=False,
            error_code=error_code,
            error_message=error_message,
            processing_time=self._get_elapsed_time()
        )
    
    def _log_step(self, step: ProcessingStep, message: str):
        """
        记录步骤日志
        
        Args:
            step: 处理步骤
            message: 日志信息
        """
        # TODO: 接入实际的日志系统
        print(f"[{self.__class__.__name__}] [{step.value}] {message}")

