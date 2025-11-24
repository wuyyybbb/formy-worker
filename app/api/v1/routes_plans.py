# -*- coding: utf-8 -*-
"""
套餐配置相关的 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.plan import Plan, PlanListResponse
from app.config.plans import get_all_plans, get_plan_by_id, get_featured_plan

router = APIRouter()


@router.get("/plans", response_model=PlanListResponse, summary="获取所有套餐")
async def list_plans():
    """
    获取所有可用套餐配置
    
    返回：
    - plans: 套餐列表（按排序顺序）
    - total: 套餐总数
    
    示例：
    ```
    GET /api/v1/plans
    ```
    """
    plans = get_all_plans()
    return PlanListResponse(
        plans=plans,
        total=len(plans)
    )


@router.get("/plans/{plan_id}", response_model=Plan, summary="获取单个套餐详情")
async def get_plan(plan_id: str):
    """
    根据 plan_id 获取单个套餐的详细信息
    
    参数：
    - plan_id: 套餐ID（starter / basic / pro / ultimate）
    
    返回：
    - 套餐详细信息
    
    示例：
    ```
    GET /api/v1/plans/pro
    ```
    """
    plan = get_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(
            status_code=404,
            detail=f"套餐 '{plan_id}' 不存在"
        )
    return plan


@router.get("/plans/featured/current", response_model=Plan, summary="获取推荐套餐")
async def get_featured():
    """
    获取当前推荐的套餐
    
    返回：
    - 推荐套餐的详细信息
    
    示例：
    ```
    GET /api/v1/plans/featured/current
    ```
    """
    plan = get_featured_plan()
    if not plan:
        raise HTTPException(
            status_code=404,
            detail="当前没有推荐套餐"
        )
    return plan

