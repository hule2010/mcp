"""
数据库表配置文件
定义各种业务场景下的表结构和字段映射
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TableConfig:
    """表配置类"""
    table_name: str
    description: str
    time_field: str  # 时间字段名
    primary_key: str = "id"
    fields: Dict[str, str] = None  # 字段名到描述的映射
    
    def __post_init__(self):
        if self.fields is None:
            self.fields = {}

# 预定义的表配置
TABLE_CONFIGS = {
    "users": TableConfig(
        table_name="users",
        description="用户表",
        time_field="created_at",
        primary_key="id",
        fields={
            "id": "用户ID",
            "username": "用户名",
            "email": "邮箱",
            "phone": "手机号",
            "status": "状态",
            "created_at": "创建时间",
            "updated_at": "更新时间",
            "deleted_at": "删除时间"
        }
    ),
    "orders": TableConfig(
        table_name="orders",
        description="订单表",
        time_field="created_at",
        primary_key="id",
        fields={
            "id": "订单ID",
            "user_id": "用户ID",
            "order_no": "订单号",
            "amount": "金额",
            "status": "订单状态",
            "created_at": "创建时间",
            "updated_at": "更新时间"
        }
    ),
    "products": TableConfig(
        table_name="products",
        description="商品表",
        time_field="created_at",
        primary_key="id",
        fields={
            "id": "商品ID",
            "name": "商品名称",
            "price": "价格",
            "category_id": "分类ID",
            "status": "状态",
            "created_at": "创建时间",
            "updated_at": "更新时间"
        }
    ),
    "user_logs": TableConfig(
        table_name="user_logs",
        description="用户日志表",
        time_field="log_time",
        primary_key="id",
        fields={
            "id": "日志ID",
            "user_id": "用户ID",
            "action": "操作类型",
            "ip_address": "IP地址",
            "log_time": "日志时间"
        }
    )
}

# 自然语言到表名的映射
NATURAL_LANGUAGE_TABLE_MAPPING = {
    "用户": "users",
    "新增用户": "users",
    "用户注册": "users",
    "注册用户": "users",
    "用户数量": "users",
    "订单": "orders",
    "新增订单": "orders",
    "订单数量": "orders",
    "商品": "products",
    "新增商品": "products",
    "商品数量": "products",
    "用户日志": "user_logs",
    "日志": "user_logs",
    "操作日志": "user_logs"
}

# 时间描述到SQL的映射（PostgreSQL）
TIME_MAPPING_PG = {
    "近一年": "created_at >= NOW() - INTERVAL '1 year'",
    "最近一年": "created_at >= NOW() - INTERVAL '1 year'",
    "近12个月": "created_at >= NOW() - INTERVAL '12 months'",
    "近30天": "created_at >= NOW() - INTERVAL '30 days'",
    "最近30天": "created_at >= NOW() - INTERVAL '30 days'",
    "近一个月": "created_at >= NOW() - INTERVAL '1 month'",
    "本月": "created_at >= DATE_TRUNC('month', NOW())",
    "当月": "created_at >= DATE_TRUNC('month', NOW())",
    "上个月": "created_at >= DATE_TRUNC('month', NOW() - INTERVAL '1 month') AND created_at < DATE_TRUNC('month', NOW())",
    "今年": "created_at >= DATE_TRUNC('year', NOW())",
    "当年": "created_at >= DATE_TRUNC('year', NOW())",
    "去年": "created_at >= DATE_TRUNC('year', NOW() - INTERVAL '1 year') AND created_at < DATE_TRUNC('year', NOW())",
    "近7天": "created_at >= NOW() - INTERVAL '7 days'",
    "最近7天": "created_at >= NOW() - INTERVAL '7 days'",
    "近一周": "created_at >= NOW() - INTERVAL '1 week'",
    "本周": "created_at >= DATE_TRUNC('week', NOW())",
    "今天": "created_at >= DATE_TRUNC('day', NOW())",
    "昨天": "created_at >= DATE_TRUNC('day', NOW() - INTERVAL '1 day') AND created_at < DATE_TRUNC('day', NOW())"
}

# 时间描述到SQL的映射（MySQL）
TIME_MAPPING_MYSQL = {
    "近一年": "created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)",
    "最近一年": "created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)",
    "近12个月": "created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)",
    "近30天": "created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
    "最近30天": "created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
    "近一个月": "created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)",
    "本月": "created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')",
    "当月": "created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')",
    "上个月": "created_at >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH), '%Y-%m-01') AND created_at < DATE_FORMAT(NOW(), '%Y-%m-01')",
    "今年": "created_at >= DATE_FORMAT(NOW(), '%Y-01-01')",
    "当年": "created_at >= DATE_FORMAT(NOW(), '%Y-01-01')",
    "去年": "created_at >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 YEAR), '%Y-01-01') AND created_at < DATE_FORMAT(NOW(), '%Y-01-01')",
    "近7天": "created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)",
    "最近7天": "created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)",
    "近一周": "created_at >= DATE_SUB(NOW(), INTERVAL 1 WEEK)",
    "本周": "created_at >= DATE_SUB(NOW(), INTERVAL WEEKDAY(NOW()) DAY)",
    "今天": "created_at >= CURDATE()",
    "昨天": "created_at >= DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND created_at < CURDATE()"
}

def get_table_config(table_name: str) -> Optional[TableConfig]:
    """根据表名获取表配置"""
    return TABLE_CONFIGS.get(table_name)

def get_table_name_from_natural_language(natural_language: str) -> str:
    """从自然语言中推断表名"""
    for keyword, table_name in NATURAL_LANGUAGE_TABLE_MAPPING.items():
        if keyword in natural_language:
            return table_name
    return "users"  # 默认返回用户表

def get_time_mapping(db_type: str) -> Dict[str, str]:
    """根据数据库类型获取时间映射"""
    if db_type == "postgresql":
        return TIME_MAPPING_PG
    elif db_type == "mysql":
        return TIME_MAPPING_MYSQL
    else:
        return TIME_MAPPING_PG  # 默认使用PostgreSQL

def add_custom_table_config(table_name: str, config: TableConfig):
    """添加自定义表配置"""
    TABLE_CONFIGS[table_name] = config

def add_custom_language_mapping(keywords: List[str], table_name: str):
    """添加自定义自然语言映射"""
    for keyword in keywords:
        NATURAL_LANGUAGE_TABLE_MAPPING[keyword] = table_name