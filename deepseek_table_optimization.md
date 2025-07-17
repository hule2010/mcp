# DeepSeek 表名推断优化

## 问题描述

原来的 `get_table_name_from_natural_language` 函数使用简单的关键词匹配方式来推断表名，存在以下问题：

1. **准确性低**：只能通过预定义的关键词匹配，无法理解复杂的语义
2. **扩展性差**：需要手动维护关键词映射表
3. **效率低**：需要分别调用表名推断和SQL生成，增加了API调用次数

## 优化方案

### 1. 使用 DeepSeek 进行智能表名推断

**修改文件**: `database_config.py`

**原实现**:
```python
def get_table_name_from_natural_language(natural_language: str) -> str:
    """从自然语言中推断表名"""
    for keyword, table_name in NATURAL_LANGUAGE_TABLE_MAPPING.items():
        if keyword in natural_language:
            return table_name
    return "users"  # 默认返回用户表
```

**新实现**:
```python
def get_table_name_from_natural_language(natural_language: str) -> str:
    """使用DeepSeek从自然语言中推断表名"""
    try:
        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # 构建可用表名列表和描述
        available_tables = list(TABLE_CONFIGS.keys())
        table_descriptions = {}
        for table_name, config in TABLE_CONFIGS.items():
            table_descriptions[table_name] = config.description
        
        # 使用DeepSeek进行智能推断
        # ... (详细实现见代码)
        
    except Exception as e:
        # 异常时回退到原来的关键词匹配方法
        # ... (回退逻辑)
```

**优势**:
- 🎯 **智能语义理解**: 能够理解复杂的自然语言表达
- 🛡️ **容错机制**: 异常时自动回退到关键词匹配
- 📊 **动态适应**: 基于实际的表配置信息进行推断

### 2. 一次性获取表名和SQL（推荐）

**新增函数**: `get_table_and_sql_from_natural_language`

```python
def get_table_and_sql_from_natural_language(natural_language: str, db_type: str = "postgresql") -> tuple[str, str]:
    """使用DeepSeek同时获取表名和SQL查询"""
    # 一次API调用同时获取表名和SQL
    # 返回 (table_name, sql_query)
```

**优势**:
- ⚡ **效率提升**: 减少API调用次数，从2次降到1次
- 🎯 **一致性**: 表名和SQL在同一个上下文中生成，确保一致性
- 💰 **成本降低**: 减少API调用费用

### 3. 新增优化的查询方法

**新增方法**: `execute_natural_language_query_optimized`

```python
async def execute_natural_language_query_optimized(self, natural_language: str) -> Dict[str, Any]:
    """使用DeepSeek优化的自然语言查询方法，一次性获取表名和SQL"""
    # 使用优化的函数同时获取表名和SQL
    table_name, sql_query = get_table_and_sql_from_natural_language(natural_language, self.db_type)
    # ... 执行查询
```

## 使用方式

### 原有方式（仍然支持）
```python
# 异步调用
result = await client.execute_natural_language_query("查询最近30天注册的用户")

# 同步调用
result = execute_natural_language_query_sync("查询最近30天注册的用户")
```

### 优化方式（推荐）
```python
# 异步调用
result = await client.execute_natural_language_query_optimized("查询最近30天注册的用户")

# 同步调用
result = execute_natural_language_query_optimized_sync("查询最近30天注册的用户")
```

### 直接获取表名和SQL
```python
table_name, sql_query = get_table_and_sql_from_natural_language("查询最近30天注册的用户", "postgresql")
```

## 性能对比

| 方法 | API调用次数 | 准确性 | 扩展性 | 推荐度 |
|------|-------------|--------|--------|--------|
| 原关键词匹配 | 1次 | 低 | 差 | ❌ |
| DeepSeek表名推断 | 2次 | 高 | 好 | ✅ |
| 一次性获取 | 1次 | 高 | 好 | ⭐ |

## 配置要求

确保环境变量中设置了 DeepSeek API Key：
```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

## 向后兼容

- ✅ 原有的 `get_table_name_from_natural_language` 函数保持接口不变
- ✅ 原有的查询方法继续支持
- ✅ 异常时自动回退到关键词匹配，确保稳定性

## 总结

通过这次优化，我们实现了：

1. **智能化**: 从简单的关键词匹配升级到基于DeepSeek的智能语义理解
2. **效率化**: 提供一次性获取表名和SQL的方法，减少API调用
3. **稳定性**: 保持向后兼容，异常时自动回退
4. **可扩展**: 基于表配置动态适应，无需手动维护映射关系

推荐使用 `execute_natural_language_query_optimized` 方法获得最佳性能和准确性。