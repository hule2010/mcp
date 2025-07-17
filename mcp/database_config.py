"""
数据库表配置文件
定义各种业务场景下的表结构和字段映射
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import os
from openai import OpenAI

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
    """使用DeepSeek从自然语言中推断表名"""
    try:
        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # 构建可用表名列表
        available_tables = list(TABLE_CONFIGS.keys())
        table_descriptions = {}
        for table_name, config in TABLE_CONFIGS.items():
            table_descriptions[table_name] = config.description
        
        # 创建提示词
        prompt = f"""你是一个数据库表名推断专家。根据用户的自然语言查询，从可用的表中选择最合适的表名。

可用的表:
{json.dumps(table_descriptions, ensure_ascii=False, indent=2)}

用户查询: {natural_language}

请根据用户查询的内容，选择最合适的表名。只返回表名，不要包含其他解释。
如果无法确定，请返回 "users"。

要求:
1. 只返回表名，不要包含其他文字
2. 表名必须是上述可用表中的一个
3. 根据查询内容的语义来判断最合适的表
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        table_name = response.choices[0].message.content.strip()
        
        # 验证返回的表名是否在可用表中
        if table_name in available_tables:
            return table_name
        else:
            # 如果返回的表名不在可用表中，回退到关键词匹配
            for keyword, fallback_table_name in NATURAL_LANGUAGE_TABLE_MAPPING.items():
                if keyword in natural_language:
                    return fallback_table_name
            return "users"  # 默认返回用户表
            
    except Exception as e:
        print(f"使用DeepSeek推断表名失败: {str(e)}")
        # 回退到原来的关键词匹配方法
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

def get_table_and_sql_from_natural_language(natural_language: str, db_type: str = "postgresql") -> tuple[str, str]:
    """使用DeepSeek同时获取表名和SQL查询"""
    try:
        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # 构建可用表信息
        available_tables = {}
        for table_name, config in TABLE_CONFIGS.items():
            available_tables[table_name] = {
                "description": config.description,
                "time_field": config.time_field,
                "primary_key": config.primary_key,
                "fields": config.fields
            }
        
        # 获取时间映射示例
        time_mapping = get_time_mapping(db_type)
        time_examples = ""
        if time_mapping:
            time_examples = f"""
时间查询示例（{db_type.upper()}）:
"""
            for desc, sql in list(time_mapping.items())[:5]:
                time_examples += f"- {desc}: {sql}\n"
        
        # 创建提示词
        prompt = f"""你是一个数据库专家。根据用户的自然语言查询，需要同时确定合适的表名和生成对应的SQL查询。

可用的表信息:
{json.dumps(available_tables, ensure_ascii=False, indent=2)}

{time_examples}

用户查询: {natural_language}

请返回JSON格式的结果，包含表名和SQL查询:
{{
    "table_name": "选择的表名",
    "sql_query": "生成的SQL查询语句"
}}

要求:
1. 表名必须是上述可用表中的一个
2. SQL必须是有效的{db_type.upper()}语法
3. 如果涉及时间查询，请使用上述时间查询示例中的格式
4. 对于统计查询，使用COUNT()函数
5. 确保查询的安全性，避免SQL注入
6. 只返回JSON格式，不要包含其他解释
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # 清理可能的markdown格式
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        # 解析JSON结果
        result = json.loads(result_text.strip())
        table_name = result.get("table_name", "users")
        sql_query = result.get("sql_query", "")
        
        # 验证表名
        if table_name not in TABLE_CONFIGS:
            table_name = "users"
        
        return table_name, sql_query
        
    except Exception as e:
        print(f"使用DeepSeek获取表名和SQL失败: {str(e)}")
        # 回退到原来的方法
        table_name = get_table_name_from_natural_language(natural_language)
        return table_name, ""