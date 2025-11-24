# -*- coding: utf-8 -*-
"""
套餐配置数据
官方套餐列表（硬编码）
"""
from typing import List
from app.schemas.plan import Plan


# 官方套餐配置
OFFICIAL_PLANS: List[Plan] = [
    # Starter 入门版
    Plan(
        plan_id="starter",
        name="STARTER",
        price_month=49,
        price_original=59,
        monthly_credits=2000,
        image_count=50,
        is_featured=False,
        features=[
            "基础 AI 换头功能",
            "约 50 张图片生成",
            "标准处理速度"
        ],
        sort_order=0
    ),
    
    # Basic 基础版
    Plan(
        plan_id="basic",
        name="BASIC",
        price_month=99,
        price_original=119,
        monthly_credits=5000,
        image_count=120,
        is_featured=False,
        features=[
            "全部 AI 功能",
            "约 120 张图片生成",
            "优先处理速度",
            "批量处理"
        ],
        sort_order=1
    ),
    
    # Pro 专业版（推荐）
    Plan(
        plan_id="pro",
        name="PRO",
        price_month=199,
        price_original=249,
        monthly_credits=12000,
        image_count=300,
        is_featured=True,  # 推荐套餐
        features=[
            "全部 AI 功能",
            "约 300 张图片生成",
            "极速处理",
            "高级批量处理",
            "优先客服支持"
        ],
        sort_order=2
    ),
    
    # Ultimate 旗舰版
    Plan(
        plan_id="ultimate",
        name="ULTIMATE",
        price_month=399,
        price_original=499,
        monthly_credits=30000,
        image_count=750,
        is_featured=False,
        features=[
            "全部 AI 功能",
            "约 750 张图片生成",
            "最高优先级处理",
            "无限批量处理",
            "专属客服支持",
            "API 接口访问"
        ],
        sort_order=3
    )
]


def get_all_plans() -> List[Plan]:
    """
    获取所有套餐配置
    
    Returns:
        套餐列表（按 sort_order 排序）
    """
    return sorted(OFFICIAL_PLANS, key=lambda p: p.sort_order)


def get_plan_by_id(plan_id: str) -> Plan | None:
    """
    根据 plan_id 获取套餐
    
    Args:
        plan_id: 套餐ID
        
    Returns:
        套餐对象，如果不存在则返回 None
    """
    for plan in OFFICIAL_PLANS:
        if plan.plan_id == plan_id:
            return plan
    return None


def get_featured_plan() -> Plan | None:
    """
    获取推荐套餐
    
    Returns:
        推荐的套餐，如果没有则返回 None
    """
    for plan in OFFICIAL_PLANS:
        if plan.is_featured:
            return plan
    return None

