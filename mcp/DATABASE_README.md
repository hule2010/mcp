# 数据库MCP客户端使用指南

## 概述

数据库MCP客户端是一个基于DeepSeek大语言模型的自然语言数据库查询工具。它能够：

- 接收自然语言查询（如"统计近一年有多少新增用户"）
- 使用DeepSeek AI自动生成SQL查询语句
- 执行查询并返回结果
- 支持PostgreSQL、MySQL、SQLite数据库

## 快速开始

### 1. 配置环境变量

编辑 `.env` 文件，配置您的数据库连接信息：

```bash
# PostgreSQL配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_password
POSTGRES_DATABASE=your_actual_database

# 数据库类型
DATABASE_TYPE=postgresql
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行示例

```bash
python quick_start.py
```

## 使用方法

### 基本用法

```python
from database_mcp_client import query_new_users_count_sync

# 统计近一年新增用户
result = query_new_users_count_sync("统计近一年有多少新增用户")

if result["status"] == "success":
    print(f"新增用户数量: {result['user_count']}")
    print(f"生成的SQL: {result['generated_sql']}")
else:
    print(f"查询失败: {result['error']}")
```

### 支持的自然语言查询

- "统计近一年有多少新增用户"
- "查询最近30天注册的用户数量"
- "统计本月新增用户"
- "查询今年的用户注册情况"
- "统计上个月的订单数量"

### 表配置

系统预配置了以下表：

- `users` - 用户表（默认时间字段：created_at）
- `orders` - 订单表（默认时间字段：created_at）
- `products` - 商品表（默认时间字段：created_at）
- `user_logs` - 用户日志表（默认时间字段：log_time）

### 自定义表配置

```python
from database_config import add_custom_table_config, TableConfig

# 添加自定义表配置
config = TableConfig(
    table_name="custom_table",
    description="自定义表",
    time_field="created_time",
    fields={
        "id": "主键ID",
        "name": "名称",
        "created_time": "创建时间"
    }
)

add_custom_table_config("custom_table", config)
```

## API参考

### query_new_users_count_sync()

统计新增用户数量的同步方法。

**参数：**
- `natural_language` (str): 自然语言查询
- `table_name` (str, optional): 表名，如果不指定会自动推断

**返回：**
```python
{
    "status": "success",
    "natural_language": "统计近一年有多少新增用户",
    "table_name": "users",
    "generated_sql": "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '1 year'",
    "user_count": 1250,
    "raw_results": [{"count": 1250}],
    "message": "查询结果: 1250"
}
```

### execute_natural_language_query_sync()

执行通用自然语言查询的同步方法。

**参数：**
- `natural_language` (str): 自然语言查询
- `table_name` (str, optional): 表名，如果不指定会自动推断

**返回：**
```python
{
    "status": "success",
    "natural_language": "查询最近30天注册的用户",
    "table_name": "users",
    "generated_sql": "SELECT * FROM users WHERE created_at >= NOW() - INTERVAL '30 days'",
    "results": [...],
    "result_count": 45,
    "message": "查询成功，返回 45 条结果"
}
```

## 测试

### 创建测试数据库

```bash
python test_database_client.py create-sample
```

### 运行测试

```bash
python test_database_client.py
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `.env` 文件中的数据库配置
   - 确认数据库服务正在运行
   - 验证用户名、密码、数据库名是否正确

2. **DeepSeek API调用失败**
   - 检查 `DEEPSEEK_API_KEY` 是否正确
   - 确认API密钥有效且有足够余额

3. **SQL生成错误**
   - 检查表名和字段名是否存在
   - 确认表配置是否正确

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后运行您的查询
result = query_new_users_count_sync("统计近一年有多少新增用户")
```

## 支持的数据库

- ✅ PostgreSQL
- ✅ MySQL
- ✅ SQLite

## 许可证

MIT License