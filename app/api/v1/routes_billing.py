# -*- coding: utf-8 -*-
"""
计费和套餐管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.schemas.billing import (
    UserBillingInfo,
    ChangePlanRequest,
    ChangePlanResponse
)
from app.services.billing import billing_service
from app.services.auth.auth_service import get_current_user_id

router = APIRouter()


@router.get("/billing/me", response_model=UserBillingInfo, summary="获取当前用户计费信息")
async def get_my_billing_info(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    获取当前用户的套餐和算力信息
    
    需要登录。返回：
    - 当前套餐信息
    - 剩余算力
    - 每月总算力
    - 下次续费时间
    - 算力使用百分比
    
    示例：
    ```
    GET /api/v1/billing/me
    Authorization: Bearer <token>
    ```
    """
    billing_info = billing_service.get_user_billing_info(current_user_id)
    
    if not billing_info:
        raise HTTPException(
            status_code=404,
            detail="用户计费信息不存在"
        )
    
    return billing_info


@router.post("/billing/change_plan", response_model=ChangePlanResponse, summary="切换套餐")
async def change_plan(
    request: ChangePlanRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    切换用户套餐
    
    需要登录。功能：
    - 切换到新套餐
    - 重置算力为新套餐的额度
    - 设置下次续费时间
    
    注意：
    - MVP 阶段不接入真实支付
    - 切换后立即生效
    - 算力会被重置为新套餐的月度额度
    
    示例：
    ```
    POST /api/v1/billing/change_plan
    Authorization: Bearer <token>
    {
      "plan_id": "pro"
    }
    ```
    """
    try:
        result = billing_service.change_plan(
            user_id=current_user_id,
            new_plan_id=request.plan_id,
            reset_credits=True
        )
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"切换套餐失败: {str(e)}"
        )


@router.post("/billing/consume_credits", summary="消耗算力（内部接口）")
async def consume_credits(
    amount: int,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    消耗用户算力
    
    这是一个内部接口，通常在任务处理时调用。
    
    参数：
    - amount: 要消耗的算力数量
    
    返回：
    - success: 是否成功
    - remaining_credits: 剩余算力
    """
    success = billing_service.consume_credits(current_user_id, amount)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="算力不足或用户不存在"
        )
    
    # 获取更新后的信息
    billing_info = billing_service.get_user_billing_info(current_user_id)
    
    return {
        "success": True,
        "remaining_credits": billing_info.current_credits if billing_info else 0
    }


@router.post("/billing/add_credits", summary="增加算力（内部接口）")
async def add_credits(
    amount: int,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    增加用户算力
    
    这是一个内部接口，用于充值、赠送等场景。
    
    参数：
    - amount: 要增加的算力数量
    
    返回：
    - success: 是否成功
    - total_credits: 总算力
    """
    success = billing_service.add_credits(current_user_id, amount)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="用户不存在"
        )
    
    # 获取更新后的信息
    billing_info = billing_service.get_user_billing_info(current_user_id)
    
    return {
        "success": True,
        "total_credits": billing_info.current_credits if billing_info else 0
    }

