"""
图像编辑相关的枚举定义
"""
from enum import Enum


class EditMode(str, Enum):
    """图像编辑模式"""
    HEAD_SWAP = "HEAD_SWAP"                    # 换头
    BACKGROUND_CHANGE = "BACKGROUND_CHANGE"    # 换背景
    POSE_CHANGE = "POSE_CHANGE"                # 换姿势


class ProcessingStep(str, Enum):
    """处理步骤枚举"""
    # 通用步骤
    INIT = "init"                              # 初始化
    LOAD_IMAGE = "load_image"                  # 加载图片
    VALIDATE = "validate"                      # 验证输入
    COMPLETE = "complete"                      # 完成
    
    # 换头相关
    DETECT_FACE = "detect_face"                # 检测人脸
    EXTRACT_FACE = "extract_face"              # 提取人脸特征
    SWAP_FACE = "swap_face"                    # 替换人脸
    BLEND_FACE = "blend_face"                  # 融合人脸
    
    # 换背景相关
    SEGMENT_PERSON = "segment_person"          # 人像分割
    REMOVE_BACKGROUND = "remove_background"    # 移除背景
    APPLY_BACKGROUND = "apply_background"      # 应用背景
    REFINE_EDGE = "refine_edge"                # 边缘优化
    
    # 换姿势相关
    DETECT_POSE = "detect_pose"                # 检测姿态
    EXTRACT_KEYPOINTS = "extract_keypoints"    # 提取关键点
    TRANSFER_POSE = "transfer_pose"            # 姿势迁移
    REFINE_RESULT = "refine_result"            # 优化结果


class ImageQuality(str, Enum):
    """图像质量等级"""
    LOW = "low"          # 低质量（快速）
    MEDIUM = "medium"    # 中等质量（平衡）
    HIGH = "high"        # 高质量（慢速）

