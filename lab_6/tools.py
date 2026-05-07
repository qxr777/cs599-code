"""
工具定义与实现模块

定义三个工具的参数 Schema（Pydantic）和业务逻辑函数，
同时生成符合 OpenAI function calling 规范的 JSON Schema。
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from product_db import USERS_DB


# ============================================================
#  Pydantic 参数模型定义
# ============================================================

class GetProductInfoParams(BaseModel):
    """查询商品详情的请求参数"""
    product_id: str = Field(
        description="商品唯一标识符，例如 'P001'"
    )


class CalculateBulkPriceParams(BaseModel):
    """计算大宗订单折扣价格的请求参数"""
    product_id: str = Field(
        description="商品唯一标识符，例如 'P001'"
    )
    quantity: int = Field(
        description="购买数量，必须大于 0",
        gt=0,
    )


class DeleteUserAccountParams(BaseModel):
    """删除用户账号的请求参数（高危操作）"""
    user_id: str = Field(
        description="要删除的用户 ID"
    )
    confirmation: str = Field(
        description="确认字符串，必须为 'CONFIRM_DELETE'"
    )


# ============================================================
#  工具函数实现
# ============================================================

def get_product_info(product_id: str, *, db: dict[str, dict]) -> str:
    """
    从商品数据库中查询指定商品的完整信息（含用户评论）。

    参数:
        product_id: 商品 ID
        db: 商品数据库字典

    返回:
        JSON 格式的商品信息字符串
    """
    product = db.get(product_id)
    if product is None:
        return json.dumps(
            {"error": f"商品 {product_id} 不存在"},
            ensure_ascii=False,
        )
    return json.dumps(product, ensure_ascii=False, indent=2)


def calculate_bulk_price(product_id: str, quantity: int, *, db: dict[str, dict]) -> str:
    """
    计算大宗订单的折扣价格。
    
    折扣规则:
        - 10 件以下: 无折扣
        - 10-49 件: 9.5 折
        - 50-99 件: 9 折
        - 100 件以上: 8.5 折

    参数:
        product_id: 商品 ID
        quantity: 购买数量
        db: 商品数据库字典

    返回:
        JSON 格式的价格计算结果字符串
    """
    product = db.get(product_id)
    if product is None:
        return json.dumps(
            {"error": f"商品 {product_id} 不存在"},
            ensure_ascii=False,
        )

    unit_price = product["price"]

    if quantity >= 100:
        discount = 0.85
        tier = "8.5折（100+件）"
    elif quantity >= 50:
        discount = 0.90
        tier = "9折（50-99件）"
    elif quantity >= 10:
        discount = 0.95
        tier = "9.5折（10-49件）"
    else:
        discount = 1.0
        tier = "无折扣（<10件）"

    discounted_price = round(unit_price * discount, 2)
    total_price = round(discounted_price * quantity, 2)

    result = {
        "product_name": product["name"],
        "unit_price": unit_price,
        "quantity": quantity,
        "discount_tier": tier,
        "discounted_unit_price": discounted_price,
        "total_price": total_price,
        "stock_available": product["stock"],
        "stock_sufficient": product["stock"] >= quantity,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def delete_user_account(user_id: str, confirmation: str) -> str:
    """
    ⚠️ 高危操作：删除用户账号（模拟实现）。

    参数:
        user_id: 用户 ID
        confirmation: 确认字符串

    返回:
        JSON 格式的操作结果字符串
    """
    user = USERS_DB.get(user_id)
    if user is None:
        return json.dumps(
            {"error": f"用户 {user_id} 不存在"},
            ensure_ascii=False,
        )

    # 模拟删除 —— 实际不修改数据，仅返回成功标记
    return json.dumps(
        {
            "status": "DELETED",
            "user_id": user_id,
            "user_name": user["name"],
            "message": f"⚠️ 用户 {user['name']}（{user_id}）的账号已被永久删除！",
        },
        ensure_ascii=False,
        indent=2,
    )


# ============================================================
#  OpenAI Function Calling Schema 生成
# ============================================================

def _pydantic_to_openai_params(model: type[BaseModel]) -> dict[str, Any]:
    """将 Pydantic 模型转换为 OpenAI 工具参数 Schema"""
    schema = model.model_json_schema()
    # 提取 properties 和 required 字段
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


# Phase 1 安全工具集 — 仅包含只读查询工具
TOOLS_SAFE: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "查询商品详细信息，包括名称、价格、库存、描述和用户评论",
            "parameters": _pydantic_to_openai_params(GetProductInfoParams),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_bulk_price",
            "description": "根据购买数量计算大宗订单的折扣价格",
            "parameters": _pydantic_to_openai_params(CalculateBulkPriceParams),
        },
    },
]


# Phase 2 含高危工具的工具集 — 用于攻击演示
TOOLS_WITH_DANGEROUS: list[dict[str, Any]] = [
    *TOOLS_SAFE,
    {
        "type": "function",
        "function": {
            "name": "delete_user_account",
            "description": "永久删除指定用户的账号，此操作不可逆",
            "parameters": _pydantic_to_openai_params(DeleteUserAccountParams),
        },
    },
]


# 工具名称到函数的路由映射表
TOOL_REGISTRY: dict[str, callable] = {
    "get_product_info": get_product_info,
    "calculate_bulk_price": calculate_bulk_price,
    "delete_user_account": delete_user_account,
}
