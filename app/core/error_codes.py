"""
统一错误码定义
定义所有任务处理过程中可能出现的错误码和对应的用户友好文案
"""
from enum import Enum
from typing import Dict, Optional


class TaskErrorCode(str, Enum):
    """任务错误码枚举"""
    
    # ==================== 通用错误 (1xxx) ====================
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    
    # ==================== 任务数据错误 (2xxx) ====================
    TASK_DATA_NOT_FOUND = "TASK_DATA_NOT_FOUND"
    TASK_ALREADY_PROCESSING = "TASK_ALREADY_PROCESSING"
    TASK_CANCELLED = "TASK_CANCELLED"
    
    # ==================== 参数验证错误 (3xxx) ====================
    INVALID_MODE = "INVALID_MODE"
    INVALID_SOURCE_IMAGE = "INVALID_SOURCE_IMAGE"
    INVALID_REFERENCE_IMAGE = "INVALID_REFERENCE_IMAGE"
    INVALID_CONFIG = "INVALID_CONFIG"
    MISSING_REQUIRED_PARAM = "MISSING_REQUIRED_PARAM"
    
    # ==================== 图片相关错误 (4xxx) ====================
    IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
    IMAGE_FORMAT_INVALID = "IMAGE_FORMAT_INVALID"
    IMAGE_SIZE_TOO_LARGE = "IMAGE_SIZE_TOO_LARGE"
    IMAGE_SIZE_TOO_SMALL = "IMAGE_SIZE_TOO_SMALL"
    IMAGE_LOAD_FAILED = "IMAGE_LOAD_FAILED"
    IMAGE_DECODE_FAILED = "IMAGE_DECODE_FAILED"
    
    # ==================== Pipeline 执行错误 (5xxx) ====================
    PIPELINE_ERROR = "PIPELINE_ERROR"
    PIPELINE_TIMEOUT = "PIPELINE_TIMEOUT"
    PIPELINE_INIT_FAILED = "PIPELINE_INIT_FAILED"
    PIPELINE_CONFIG_ERROR = "PIPELINE_CONFIG_ERROR"
    
    # ==================== Engine 错误 (6xxx) ====================
    ENGINE_NOT_AVAILABLE = "ENGINE_NOT_AVAILABLE"
    ENGINE_CONNECTION_FAILED = "ENGINE_CONNECTION_FAILED"
    ENGINE_TIMEOUT = "ENGINE_TIMEOUT"
    ENGINE_RESPONSE_ERROR = "ENGINE_RESPONSE_ERROR"
    ENGINE_AUTH_FAILED = "ENGINE_AUTH_FAILED"
    
    # ==================== ComfyUI 特定错误 (7xxx) ====================
    COMFYUI_NOT_AVAILABLE = "COMFYUI_NOT_AVAILABLE"
    COMFYUI_CONNECTION_TIMEOUT = "COMFYUI_CONNECTION_TIMEOUT"
    COMFYUI_WORKFLOW_ERROR = "COMFYUI_WORKFLOW_ERROR"
    COMFYUI_PROCESSING_FAILED = "COMFYUI_PROCESSING_FAILED"
    COMFYUI_RESULT_NOT_FOUND = "COMFYUI_RESULT_NOT_FOUND"
    
    # ==================== 资源错误 (8xxx) ====================
    INSUFFICIENT_CREDITS = "INSUFFICIENT_CREDITS"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    STORAGE_FULL = "STORAGE_FULL"
    
    # ==================== 业务逻辑错误 (9xxx) ====================
    PROCESSING_FAILED = "PROCESSING_FAILED"
    RESULT_SAVE_FAILED = "RESULT_SAVE_FAILED"
    NO_FACE_DETECTED = "NO_FACE_DETECTED"
    MULTIPLE_FACES_DETECTED = "MULTIPLE_FACES_DETECTED"
    POSE_EXTRACTION_FAILED = "POSE_EXTRACTION_FAILED"


class ErrorMessage:
    """错误消息定义 - 用户友好的文案"""
    
    # 错误码到消息的映射
    MESSAGES: Dict[TaskErrorCode, str] = {
        # 通用错误
        TaskErrorCode.UNKNOWN_ERROR: "未知错误",
        TaskErrorCode.INTERNAL_ERROR: "系统内部错误",
        TaskErrorCode.INVALID_REQUEST: "请求参数无效",
        
        # 任务数据错误
        TaskErrorCode.TASK_DATA_NOT_FOUND: "任务数据不存在",
        TaskErrorCode.TASK_ALREADY_PROCESSING: "任务正在处理中",
        TaskErrorCode.TASK_CANCELLED: "任务已取消",
        
        # 参数验证错误
        TaskErrorCode.INVALID_MODE: "编辑模式无效",
        TaskErrorCode.INVALID_SOURCE_IMAGE: "原始图片无效",
        TaskErrorCode.INVALID_REFERENCE_IMAGE: "参考图片无效",
        TaskErrorCode.INVALID_CONFIG: "配置参数无效",
        TaskErrorCode.MISSING_REQUIRED_PARAM: "缺少必要参数",
        
        # 图片相关错误
        TaskErrorCode.IMAGE_NOT_FOUND: "图片文件不存在",
        TaskErrorCode.IMAGE_FORMAT_INVALID: "图片格式不支持",
        TaskErrorCode.IMAGE_SIZE_TOO_LARGE: "图片尺寸过大",
        TaskErrorCode.IMAGE_SIZE_TOO_SMALL: "图片尺寸过小",
        TaskErrorCode.IMAGE_LOAD_FAILED: "图片加载失败",
        TaskErrorCode.IMAGE_DECODE_FAILED: "图片解码失败",
        
        # Pipeline 执行错误
        TaskErrorCode.PIPELINE_ERROR: "处理流程错误",
        TaskErrorCode.PIPELINE_TIMEOUT: "处理超时",
        TaskErrorCode.PIPELINE_INIT_FAILED: "处理流程初始化失败",
        TaskErrorCode.PIPELINE_CONFIG_ERROR: "处理流程配置错误",
        
        # Engine 错误
        TaskErrorCode.ENGINE_NOT_AVAILABLE: "AI 引擎不可用",
        TaskErrorCode.ENGINE_CONNECTION_FAILED: "无法连接到 AI 引擎",
        TaskErrorCode.ENGINE_TIMEOUT: "AI 引擎响应超时",
        TaskErrorCode.ENGINE_RESPONSE_ERROR: "AI 引擎返回错误",
        TaskErrorCode.ENGINE_AUTH_FAILED: "AI 引擎认证失败",
        
        # ComfyUI 特定错误
        TaskErrorCode.COMFYUI_NOT_AVAILABLE: "ComfyUI 服务不可用",
        TaskErrorCode.COMFYUI_CONNECTION_TIMEOUT: "连接 ComfyUI 超时",
        TaskErrorCode.COMFYUI_WORKFLOW_ERROR: "ComfyUI 工作流配置错误",
        TaskErrorCode.COMFYUI_PROCESSING_FAILED: "ComfyUI 处理失败",
        TaskErrorCode.COMFYUI_RESULT_NOT_FOUND: "无法获取 ComfyUI 处理结果",
        
        # 资源错误
        TaskErrorCode.INSUFFICIENT_CREDITS: "算力不足",
        TaskErrorCode.RESOURCE_LIMIT_EXCEEDED: "资源使用超限",
        TaskErrorCode.STORAGE_FULL: "存储空间已满",
        
        # 业务逻辑错误
        TaskErrorCode.PROCESSING_FAILED: "处理失败",
        TaskErrorCode.RESULT_SAVE_FAILED: "结果保存失败",
        TaskErrorCode.NO_FACE_DETECTED: "未检测到人脸",
        TaskErrorCode.MULTIPLE_FACES_DETECTED: "检测到多张人脸",
        TaskErrorCode.POSE_EXTRACTION_FAILED: "姿势提取失败",
    }
    
    # 错误详情建议
    SUGGESTIONS: Dict[TaskErrorCode, str] = {
        TaskErrorCode.IMAGE_FORMAT_INVALID: "请上传 JPG、PNG 或 WEBP 格式的图片",
        TaskErrorCode.IMAGE_SIZE_TOO_LARGE: "请上传小于 10MB 的图片",
        TaskErrorCode.IMAGE_SIZE_TOO_SMALL: "请上传分辨率至少为 512x512 的图片",
        TaskErrorCode.COMFYUI_NOT_AVAILABLE: "AI 服务暂时不可用，请稍后重试",
        TaskErrorCode.COMFYUI_CONNECTION_TIMEOUT: "网络连接超时，请检查网络或稍后重试",
        TaskErrorCode.NO_FACE_DETECTED: "请确保图片中包含清晰可见的人脸",
        TaskErrorCode.MULTIPLE_FACES_DETECTED: "请上传只包含单个人脸的图片",
        TaskErrorCode.INSUFFICIENT_CREDITS: "请充值算力或升级套餐",
    }
    
    @classmethod
    def get_message(cls, error_code: TaskErrorCode) -> str:
        """获取错误消息"""
        return cls.MESSAGES.get(error_code, "处理失败")
    
    @classmethod
    def get_suggestion(cls, error_code: TaskErrorCode) -> Optional[str]:
        """获取错误建议"""
        return cls.SUGGESTIONS.get(error_code)
    
    @classmethod
    def format_error(
        cls, 
        error_code: TaskErrorCode, 
        custom_message: Optional[str] = None,
        custom_details: Optional[str] = None
    ) -> dict:
        """
        格式化错误信息
        
        Args:
            error_code: 错误码
            custom_message: 自定义消息（覆盖默认消息）
            custom_details: 自定义详情（追加到建议后）
        
        Returns:
            dict: 格式化的错误字典
        """
        message = custom_message or cls.get_message(error_code)
        suggestion = cls.get_suggestion(error_code)
        
        # 构建详情
        details_parts = []
        if suggestion:
            details_parts.append(suggestion)
        if custom_details:
            details_parts.append(custom_details)
        
        details = "\n".join(details_parts) if details_parts else None
        
        return {
            "code": error_code.value,
            "message": message,
            "details": details
        }


# 便捷函数
def create_error(
    error_code: TaskErrorCode,
    custom_message: Optional[str] = None,
    custom_details: Optional[str] = None
) -> dict:
    """
    创建标准化的错误对象
    
    使用示例:
    ```python
    from app.core.error_codes import TaskErrorCode, create_error
    
    error = create_error(
        TaskErrorCode.IMAGE_NOT_FOUND,
        custom_details="文件路径: /uploads/source/xxx.jpg"
    )
    ```
    """
    return ErrorMessage.format_error(error_code, custom_message, custom_details)

