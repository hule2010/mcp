#!/usr/bin/env python3
"""
数据库MCP客户端使用示例
"""

from database_mcp_client import query_new_users_count_sync, execute_natural_language_query_sync

def main():
    """主函数 - 演示如何使用数据库MCP客户端"""
    
    print("=== 数据库MCP客户端使用示例 ===\n")
    
    # 示例1: 统计近一年新增用户数量
    print("1. 统计近一年新增用户数量:")
    result = query_new_users_count_sync("统计近一年有多少新增用户")
    
    if result["status"] == "success":
        print(f"   新增用户数量: {result['user_count']}")
        print(f"   生成的SQL: {result['generated_sql']}")
    else:
        print(f"   查询失败: {result['error']}")
    
    print()
    
    # 示例2: 其他自然语言查询
    queries = [
        "查询最近30天注册的用户数量",
        "统计本月新增用户",
        "查询今年的用户注册情况"
    ]
    
    for i, query in enumerate(queries, 2):
        print(f"{i}. {query}:")
        result = execute_natural_language_query_sync(query)
        
        if result["status"] == "success":
            print(f"   查询结果: {result['result_count']} 条记录")
            print(f"   生成的SQL: {result['generated_sql']}")
        else:
            print(f"   查询失败: {result['error']}")
        
        print()

if __name__ == "__main__":
    main()