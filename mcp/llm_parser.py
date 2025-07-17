# llm_parser.py
import os
import json
from typing import Any, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 定义可用的 MCP 动作
AVAILABLE_ACTIONS = {
    "dingtalk_notify": {
        "description": "发送钉钉通知",
        "params": ["message", "at_mobiles", "is_at_all"]
    },
    "deploy": {
        "description": "部署项目到指定环境",
        "params": ["environment", "project_name", "version", "config"]
    },
    "upload_file": {
        "description": "上传文件到服务API",
        "params": ["file_path", "service_name", "metadata"]
    },
    "file_read": {
        "description": "读取文件内容",
        "params": ["file_path"]
    },
    "file_write": {
        "description": "写入文件内容",
        "params": ["file_path", "content"]
    },
    "file_delete": {
        "description": "删除文件",
        "params": ["file_path"]
    },
    "directory_list": {
        "description": "列出目录内容",
        "params": ["directory_path"]
    },
    "web_search": {
        "description": "搜索网页内容",
        "params": ["query", "num_results"]
    },
    "data_process": {
        "description": "处理数据",
        "params": ["data", "operation"]
    },
    "api_call": {
        "description": "调用外部API",
        "params": ["url", "method", "headers", "body"]
    }
}

def create_system_prompt() -> str:
    """创建系统提示词"""
    actions_desc = json.dumps(AVAILABLE_ACTIONS, ensure_ascii=False, indent=2)
    
    return f"""你是一个工作流解析助手。用户会用自然语言描述他们想要完成的任务，你需要将其转换为结构化的工作流。

可用的动作和参数：
{actions_desc}

你必须返回一个有效的JSON格式的工作流，格式如下：
{{
    "description": "工作流的简要描述",
    "steps": [
        {{
            "action": "动作名称",
            "params": {{
                "参数名": "参数值"
            }},
            "description": "这一步的说明"
        }}
    ]
}}

注意：
1. 只使用上述列出的动作
2. 确保参数完整且合理
3. 步骤应该按照逻辑顺序排列
4. 返回的必须是有效的JSON格式
"""

def parse_to_workflow(natural_language: str) -> Dict[str, Any]:
    """
    调用 DeepSeek 大模型，将自然语言解析为结构化工作流。
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": create_system_prompt()},
                {"role": "user", "content": natural_language}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        workflow_json = response.choices[0].message.content
        workflow = json.loads(workflow_json)
        
        # 验证工作流格式
        if "steps" not in workflow:
            workflow["steps"] = []
        
        # 验证每个步骤
        for step in workflow["steps"]:
            if "action" not in step or step["action"] not in AVAILABLE_ACTIONS:
                raise ValueError(f"无效的动作: {step.get('action')}")
            
        return workflow
        
    except Exception as e:
        print(f"解析工作流时出错: {str(e)}")
        # 返回一个默认的错误工作流
        return {
            "description": "解析失败",
            "steps": [],
            "error": str(e)
        }

if __name__ == "__main__":
    query = "发送钉钉消息说测试成功"
    workflow = parse_to_workflow(query)
    print(workflow)

    query = "部署 my-app 到生产环境"
    workflow = parse_to_workflow(query)
    print(workflow)

    query = "上传文件 report.pdf 到文档服务"
    workflow = parse_to_workflow(query)
    print(workflow)
    query = "部署 frontend 到测试环境，然后发送钉钉通知"
    workflow = parse_to_workflow(query)
    print(workflow)

    query = "这是一个无效的动作: unknown_action"
    workflow = parse_to_workflow(query)
    print(workflow)