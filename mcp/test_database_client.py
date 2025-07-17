#!/usr/bin/env python3
"""
数据库MCP客户端测试脚本
"""

import asyncio
import json
from database_mcp_client import DatabaseMCPClient, query_new_users_count_sync

async def test_database_client():
    """测试数据库客户端功能"""
    print("=== 数据库MCP客户端测试 ===\n")
    
    # 创建客户端实例
    client = DatabaseMCPClient()
    
    # 测试用例1: 统计近一年新增用户
    print("1. 测试统计近一年新增用户:")
    result1 = await client.query_new_users_count("统计近一年有多少新增用户")
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    print()
    
    # 测试用例2: 其他自然语言查询
    test_queries = [
        "查询最近30天注册的用户",
        "统计本月新增用户数量",
        "查询今年注册的所有用户",
        "统计上个月的用户注册数量"
    ]
    
    for i, query in enumerate(test_queries, 2):
        print(f"{i}. 测试查询: {query}")
        result = await client.execute_natural_language_query(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

def test_sync_version():
    """测试同步版本的API"""
    print("=== 同步版本测试 ===\n")
    
    # 测试同步版本
    result = query_new_users_count_sync("统计近一年有多少新增用户")
    print("同步版本结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def create_sample_database():
    """创建示例数据库和表（仅用于测试）"""
    import sqlite3
    from datetime import datetime, timedelta
    import random
    
    # 创建SQLite数据库
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME
        )
    ''')
    
    # 清空现有数据
    cursor.execute('DELETE FROM users')
    
    # 插入示例数据
    base_date = datetime.now() - timedelta(days=400)
    
    for i in range(1000):
        # 随机生成创建时间（过去400天内）
        random_days = random.randint(0, 400)
        created_at = base_date + timedelta(days=random_days)
        
        cursor.execute('''
            INSERT INTO users (username, email, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            f'user_{i+1}',
            f'user_{i+1}@example.com',
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            created_at.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    conn.commit()
    conn.close()
    
    print("示例数据库创建完成！")
    print("- 数据库文件: test.db")
    print("- 表名: users")
    print("- 数据量: 1000条用户记录")
    print("- 时间范围: 过去400天内的随机时间")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-sample":
        # 创建示例数据库
        create_sample_database()
    elif len(sys.argv) > 1 and sys.argv[1] == "sync":
        # 测试同步版本
        test_sync_version()
    else:
        # 运行异步测试
        asyncio.run(test_database_client())