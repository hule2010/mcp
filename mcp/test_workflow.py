#!/usr/bin/env python3
# test_workflow.py
import requests
import json

# API 地址
API_URL = "http://localhost:8000/workflow"

# 测试用例
test_cases = [
    {
        "name": "测试1: 钉钉通知",
        "query": "发送钉钉消息通知团队说系统部署完成了"
    },
    {
        "name": "测试2: 部署流程",
        "query": "把项目 my-app 的 v2.1.0 版本部署到生产环境"
    },
    {
        "name": "测试3: 文件上传",
        "query": "上传文件 report.pdf 到文档服务"
    },
    {
        "name": "测试4: 组合工作流",
        "query": "部署 frontend 项目到测试环境，完成后发送钉钉通知，并上传部署日志文件"
    }
]

def test_workflow(test_case):
    """测试单个工作流"""
    print(f"\n{'='*60}")
    print(f"运行: {test_case['name']}")
    print(f"查询: {test_case['query']}")
    print('='*60)
    
    try:
        response = requests.post(API_URL, json={"query": test_case["query"]})
        if response.status_code == 200:
            result = response.json()
            print("\n工作流执行结果:")
            print(json.dumps(result["result"], indent=2, ensure_ascii=False))
            
            print("\n执行步骤详情:")
            for i, step in enumerate(result["steps"], 1):
                print(f"\n步骤 {i}: {step['action']}")
                print(f"  描述: {step.get('description', '无')}")
                print(f"  状态: {step.get('status', '未知')}")
                if step.get('error'):
                    print(f"  错误: {step['error']}")
                print(f"  耗时: {step.get('duration', 0):.2f}秒")
        else:
            print(f"错误: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"请求失败: {str(e)}")

def main():
    """运行所有测试"""
    print("MCP 工作流系统测试")
    print("请确保服务已启动: uvicorn app:app --reload")
    
    for test_case in test_cases:
        test_workflow(test_case)
        input("\n按回车继续下一个测试...")

if __name__ == "__main__":
    main() 