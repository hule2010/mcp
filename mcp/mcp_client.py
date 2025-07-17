# mcp_client.py
import os
import json
import aiohttp
import asyncio
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MCPClient:
    """MCP API 客户端"""
    
    def __init__(self):
        self.dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK_URL")
        self.deploy_api_url = os.getenv("DEPLOY_API_URL")
        self.file_upload_api_url = os.getenv("FILE_UPLOAD_API_URL")
        self.api_token = os.getenv("MCP_API_TOKEN")
        
    async def _make_request(self, url: str, method: str = "POST", 
                          headers: Optional[Dict] = None, 
                          data: Optional[Dict] = None,
                          files: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        async with aiohttp.ClientSession() as session:
            default_headers = {"Authorization": f"Bearer {self.api_token}"}
            if headers:
                default_headers.update(headers)
            
            kwargs = {
                "headers": default_headers,
                "timeout": aiohttp.ClientTimeout(total=30)
            }
            
            if files:
                # 文件上传
                form_data = aiohttp.FormData()
                for key, value in (data or {}).items():
                    form_data.add_field(key, value)
                for file_key, file_path in files.items():
                    form_data.add_field(file_key, open(file_path, 'rb'))
                kwargs["data"] = form_data
            elif data:
                kwargs["json"] = data
            
            async with session.request(method, url, **kwargs) as response:
                result = await response.json()
                if response.status >= 400:
                    raise Exception(f"API 错误: {response.status} - {result}")
                return result
    
    async def send_dingtalk_notification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送钉钉通知"""
        try:
            message = params.get("message", "")
            at_mobiles = params.get("at_mobiles", [])
            is_at_all = params.get("is_at_all", False)
            
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                },
                "at": {
                    "atMobiles": at_mobiles,
                    "isAtAll": is_at_all
                }
            }
            
            result = await self._make_request(
                self.dingtalk_webhook,
                method="POST",
                data=data
            )
            
            return {
                "status": "success",
                "result": result,
                "message": "钉钉通知发送成功"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "钉钉通知发送失败"
            }
    
    async def deploy_to_environment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """部署到指定环境"""
        try:
            environment = params.get("environment", "dev")
            project_name = params.get("project_name")
            version = params.get("version", "latest")
            config = params.get("config", {})
            
            deploy_data = {
                "environment": environment,
                "project": project_name,
                "version": version,
                "config": config,
                "timestamp": os.popen("date").read().strip()
            }
            
            result = await self._make_request(
                f"{self.deploy_api_url}/deploy",
                method="POST",
                data=deploy_data
            )
            
            return {
                "status": "success",
                "result": result,
                "deployment_id": result.get("deployment_id"),
                "message": f"成功部署到 {environment} 环境"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "部署失败"
            }
    
    async def upload_file_to_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """上传文件到服务API"""
        try:
            file_path = params.get("file_path")
            service_name = params.get("service_name", "default")
            metadata = params.get("metadata", {})
            
            if not file_path or not os.path.exists(file_path):
                raise ValueError(f"文件不存在: {file_path}")
            
            upload_data = {
                "service": service_name,
                "metadata": json.dumps(metadata)
            }
            
            result = await self._make_request(
                f"{self.file_upload_api_url}/upload",
                method="POST",
                data=upload_data,
                files={"file": file_path}
            )
            
            return {
                "status": "success",
                "result": result,
                "file_id": result.get("file_id"),
                "file_url": result.get("url"),
                "message": "文件上传成功"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "文件上传失败"
            }
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行具体的 MCP 动作"""
        action_map = {
            "dingtalk_notify": self.send_dingtalk_notification,
            "deploy": self.deploy_to_environment,
            "upload_file": self.upload_file_to_service,
        }
        
        if action in action_map:
            return await action_map[action](params)
        else:
            # 处理其他通用动作
            return await self._handle_generic_action(action, params)
    
    async def _handle_generic_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理通用动作"""
        # 这里可以添加更多通用的 MCP 功能
        return {
            "status": "success",
            "action": action,
            "params": params,
            "message": f"执行动作: {action}"
        }

# 全局客户端实例
_client = MCPClient()

def call_mcp_api(action: str, params: dict) -> Any:
    """
    同步接口，用于兼容现有代码
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_client.execute_action(action, params))
    finally:
        loop.close() 