import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
from dotenv import load_dotenv
from database_config import (
    get_table_config, 
    get_table_name_from_natural_language,
    get_table_and_sql_from_natural_language,
    get_time_mapping,
    TableConfig
)

# 加载环境变量
load_dotenv()

class DatabaseMCPClient:
    """数据库操作MCP客户端"""
    
    def __init__(self):
        # 初始化DeepSeek客户端
        self.llm_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        # 数据库连接配置
        self.db_config = {
            "mysql": {
                "host": os.getenv("MYSQL_HOST", "localhost"),
                "port": os.getenv("MYSQL_PORT", 3306),
                "user": os.getenv("MYSQL_USER", "root"),
                "password": os.getenv("MYSQL_PASSWORD", ""),
                "database": os.getenv("MYSQL_DATABASE", "test")
            },
            "postgresql": {
                "host": os.getenv("POSTGRES_HOST", "localhost"),
                "port": os.getenv("POSTGRES_PORT", 5432),
                "user": os.getenv("POSTGRES_USER", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD", ""),
                "database": os.getenv("POSTGRES_DATABASE", "test")
            },
            "sqlite": {
                "path": os.getenv("SQLITE_PATH", "test.db")
            }
        }
        
        # 默认数据库类型
        self.db_type = os.getenv("DATABASE_TYPE", "postgresql")
        
        # 数据库引擎
        self.engine = None
        self.async_engine = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接"""
        try:
            if self.db_type == "mysql":
                config = self.db_config["mysql"]
                sync_url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                async_url = f"mysql+aiomysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            elif self.db_type == "postgresql":
                config = self.db_config["postgresql"]
                sync_url = f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                async_url = f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            elif self.db_type == "sqlite":
                config = self.db_config["sqlite"]
                sync_url = f"sqlite:///{config['path']}"
                async_url = f"sqlite+aiosqlite:///{config['path']}"
            else:
                raise ValueError(f"不支持的数据库类型: {self.db_type}")
            
            self.engine = create_engine(sync_url)
            self.async_engine = create_async_engine(async_url)
            
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            raise
    
    def _create_sql_generation_prompt(self, natural_language: str, table_config: Optional[TableConfig] = None, table_schema: Optional[str] = None) -> str:
        """创建SQL生成的提示词"""
        schema_info = ""
        if table_schema:
            schema_info = f"\n数据库表结构:\n{table_schema}\n"
        
        # 添加表配置信息
        config_info = ""
        if table_config:
            config_info = f"""
表配置信息:
- 表名: {table_config.table_name}
- 表描述: {table_config.description}
- 时间字段: {table_config.time_field}
- 主键: {table_config.primary_key}
- 字段说明: {json.dumps(table_config.fields, ensure_ascii=False, indent=2)}
"""
        
        # 获取时间映射
        time_mapping = get_time_mapping(self.db_type)
        time_examples = ""
        if time_mapping:
            time_examples = f"""
时间查询示例（{self.db_type.upper()}）:
"""
            for desc, sql in list(time_mapping.items())[:5]:  # 只显示前5个示例
                time_examples += f"- {desc}: {sql}\n"
        
        return f"""你是一个SQL查询专家。用户会用自然语言描述他们想要查询的数据，你需要将其转换为SQL查询语句。

{config_info}
{schema_info}
{time_examples}

用户查询: {natural_language}

请根据用户的自然语言描述生成相应的SQL查询语句。

要求:
1. 生成的SQL必须是有效的，符合{self.db_type.upper()}语法
2. 如果涉及时间查询，请使用上述时间查询示例中的格式
3. 对于统计查询，使用COUNT()函数
4. 确保查询的安全性，避免SQL注入
5. 只返回SQL语句，不要包含其他解释
6. 如果表配置中指定了时间字段，请使用该字段名

请直接返回SQL查询语句:"""
    
    async def _generate_sql_from_natural_language(self, natural_language: str, table_config: Optional[TableConfig] = None, table_schema: Optional[str] = None) -> str:
        """使用DeepSeek将自然语言转换为SQL查询"""
        try:
            prompt = self._create_sql_generation_prompt(natural_language, table_config, table_schema)
            
            response = self.llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # 清理SQL查询（移除可能的markdown格式）
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            return sql_query.strip()
            
        except Exception as e:
            raise Exception(f"生成SQL查询失败: {str(e)}")
    
    async def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        try:
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text(sql_query))
                
                # 获取列名
                columns = result.keys()
                
                # 获取所有行数据
                rows = result.fetchall()
                
                # 转换为字典列表
                results = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = row[i]
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            raise Exception(f"执行SQL查询失败: {str(e)}")
    
    async def get_table_schema(self, table_name: str) -> str:
        """获取表结构信息"""
        try:
            if self.db_type == "mysql":
                schema_query = f"DESCRIBE {table_name}"
            elif self.db_type == "postgresql":
                schema_query = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                """
            elif self.db_type == "sqlite":
                schema_query = f"PRAGMA table_info({table_name})"
            else:
                return ""
            
            results = await self.execute_query(schema_query)
            
            # 格式化表结构信息
            schema_info = f"表名: {table_name}\n"
            for row in results:
                if self.db_type == "mysql":
                    schema_info += f"- {row['Field']}: {row['Type']} {'NOT NULL' if row['Null'] == 'NO' else 'NULL'}\n"
                elif self.db_type == "postgresql":
                    schema_info += f"- {row['column_name']}: {row['data_type']} {'NOT NULL' if row['is_nullable'] == 'NO' else 'NULL'}\n"
                elif self.db_type == "sqlite":
                    schema_info += f"- {row['name']}: {row['type']} {'NOT NULL' if row['notnull'] else 'NULL'}\n"
            
            return schema_info
            
        except Exception as e:
            print(f"获取表结构失败: {str(e)}")
            return ""
    
    async def query_new_users_count(self, natural_language: str, table_name: str = None) -> Dict[str, Any]:
        """统计新增用户数量的主要方法"""
        # 如果指定了表名，使用传统方法；否则使用优化方法
        if table_name is not None:
            # 获取表配置
            table_config = get_table_config(table_name)

            # 获取表结构
            table_schema = await self.get_table_schema(table_name)

            # 生成SQL查询
            sql_query = await self._generate_sql_from_natural_language(natural_language, table_config, table_schema)
        else:
            # 使用优化的方法直接获取表名和SQL
            table_name, sql_query = get_table_and_sql_from_natural_language(natural_language, self.db_type)

            if not sql_query:
                # 如果没有获取到SQL，回退到传统方法
                table_config = get_table_config(table_name)
                table_schema = await self.get_table_schema(table_name)
                sql_query = await self._generate_sql_from_natural_language(natural_language, table_config, table_schema)

        # 执行查询
            results = await self.execute_query(sql_query)
            
            # 提取用户数量
            user_count = 0
            if results:
                # 假设查询返回的是统计结果
                first_result = results[0]
                # 尝试找到包含数量的字段
                for key, value in first_result.items():
                    if isinstance(value, (int, float)) and ('count' in key.lower() or 'total' in key.lower() or len(first_result) == 1):
                        user_count = int(value)
                        break
            
            return {
                "status": "success",
                "natural_language": natural_language,
                "table_name": table_name,
                "generated_sql": sql_query,
                "user_count": user_count,
                "raw_results": results,
                "message": f"查询结果: {user_count}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "natural_language": natural_language,
                "message": "查询失败"
            }
    
    async def execute_natural_language_query(self, natural_language: str, table_name: str = None) -> Dict[str, Any]:
        """执行自然语言查询的通用方法"""
        try:
            # 如果没有指定表名，从自然语言中推断
            if table_name is None:
                table_name = get_table_name_from_natural_language(natural_language)
            
            # 获取表配置
            table_config = get_table_config(table_name)
            
            # 获取表结构
            table_schema = await self.get_table_schema(table_name)
            
            # 生成SQL查询
            sql_query = await self._generate_sql_from_natural_language(natural_language, table_config, table_schema)
            
            # 执行查询
            results = await self.execute_query(sql_query)
            
            return {
                "status": "success",
                "natural_language": natural_language,
                "table_name": table_name,
                "generated_sql": sql_query,
                "results": results,
                "result_count": len(results),
                "message": f"查询成功，返回 {len(results)} 条结果"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "natural_language": natural_language,
                "message": "查询失败"
            }
    
    async def execute_natural_language_query_optimized(self, natural_language: str) -> Dict[str, Any]:
        """使用DeepSeek优化的自然语言查询方法，一次性获取表名和SQL"""
        try:
            # 使用优化的函数同时获取表名和SQL
            table_name, sql_query = get_table_and_sql_from_natural_language(natural_language, self.db_type)
            
            if not sql_query:
                # 如果没有获取到SQL，回退到原来的方法
                return await self.execute_natural_language_query(natural_language, table_name)
            
            # 执行查询
            results = await self.execute_query(sql_query)
            
            return {
                "status": "success",
                "data": results,
                "count": len(results),
                "table_name": table_name,
                "sql_query": sql_query,
                "natural_language": natural_language,
                "message": f"查询成功，共找到 {len(results)} 条记录"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "natural_language": natural_language,
                "message": "查询失败"
            }

# 同步包装函数
def query_new_users_count_sync(natural_language: str, table_name: str = None) -> Dict[str, Any]:
    """同步版本的新增用户统计"""
    client = DatabaseMCPClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(client.query_new_users_count(natural_language, table_name))
    finally:
        loop.close()

def execute_natural_language_query_sync(natural_language: str, table_name: str = None) -> Dict[str, Any]:
    """同步版本的自然语言查询"""
    client = DatabaseMCPClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(client.execute_natural_language_query(natural_language, table_name))
    finally:
        loop.close()

def execute_natural_language_query_optimized_sync(natural_language: str) -> Dict[str, Any]:
    """同步版本的优化自然语言查询"""
    client = DatabaseMCPClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(client.execute_natural_language_query_optimized(natural_language))
    finally:
        loop.close()

if __name__ == "__main__":
    # 测试示例
    async def test():
        client = DatabaseMCPClient()
        
        # 测试统计近一年新增用户
        result = await client.query_new_users_count("统计近一年有多少新增用户")
        print("统计结果:", json.dumps(result, ensure_ascii=False, indent=2))
        
        # 测试其他自然语言查询
        result2 = await client.execute_natural_language_query("查询最近30天注册的用户")
        print("查询结果:", json.dumps(result2, ensure_ascii=False, indent=2))
        
        # 测试优化的自然语言查询
        result3 = await client.execute_natural_language_query_optimized("查询最近7天的订单数量")
        print("优化查询结果:", json.dumps(result3, ensure_ascii=False, indent=2))
    
    # 运行测试
    asyncio.run(test())