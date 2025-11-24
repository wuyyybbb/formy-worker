# -*- coding: utf-8 -*-
"""
套餐配置相关的 Pydantic 模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class PlanFeature(BaseModel):
    """套餐功能项"""
    text: str = Field(..., description="功能描述")
    enabled: bool = Field(default=True, description="是否启用")


class Plan(BaseModel):
    """套餐配置"""
    plan_id: str = Field(..., description="套餐唯一标识")
    name: str = Field(..., description="套餐名称")
    price_month: int = Field(..., description="月付价格（人民币）")
    price_original: Optional[int] = Field(None, description="原价（用于显示折扣）")
    monthly_credits: int = Field(..., description="每月算力额度")
    image_count: int = Field(..., description="大约可生成图片数量")
    is_featured: bool = Field(default=False, description="是否推荐套餐")
    features: List[str] = Field(default_factory=list, description="功能列表")
    sort_order: int = Field(default=0, description="排序顺序")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "pro",
                "name": "PRO",
                "price_month": 199,
                "price_original": 249,
                "monthly_credits": 12000,
                "image_count": 300,
                "is_featured": True,
                "features": [
                    "全部 AI 功能",
                    "约 300 张图片生成",
                    "极速处理",
                    "高级批量处理",
                    "优先客服支持"
                ],
                "sort_order": 2
            }
        }


class PlanListResponse(BaseModel):
    """套餐列表响应"""
    plans: List[Plan] = Field(..., description="套餐列表")
    total: int = Field(..., description="总数量")

