"""
Pipeline 模块
"""
from app.services.image.pipelines.base import PipelineBase
from app.services.image.pipelines.head_swap_pipeline import HeadSwapPipeline
from app.services.image.pipelines.background_pipeline import BackgroundPipeline
from app.services.image.pipelines.pose_change_pipeline import PoseChangePipeline

__all__ = [
    "PipelineBase",
    "HeadSwapPipeline",
    "BackgroundPipeline",
    "PoseChangePipeline"
]

