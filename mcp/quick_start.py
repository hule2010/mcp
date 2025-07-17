#!/usr/bin/env python3
"""
数据库MCP客户端快速开始示例
"""

from database_mcp_client import query_new_users_count_sync

def main():
    """快速开始示例"""
    print("=== 数据库MCP客户端 - 快速开始 ===\n")
    
    # 您的自然语言查询
    query = "统计近一年有多少新增用户"
    
    print(f"查询: {query}")
    print("正在执行查询...")
    
    # 调用数据库MCP客户端
    result = query_new_users_count_sync(query)
    
    # 显示结果
    if result["status"] == "success":
        print(f"✅ 查询成功!")
        print(f"📊 新增用户数量: {result['user_count']}")
        print(f"🗂️  使用的表: {result['table_name']}")
        print(f"🔍 生成的SQL: {result['generated_sql']}")
    else:
        print(f"❌ 查询失败: {result['error']}")
        print("请检查:")
        print("1. 数据库连接配置是否正确")
        print("2. 表名和字段是否存在")
        print("3. DeepSeek API密钥是否有效")

if __name__ == "__main__":
    main()