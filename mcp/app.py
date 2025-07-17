from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from llm_parser import parse_to_workflow
from workflow_executor import execute_workflow
from typing import Dict, List, Any, Optional

app = FastAPI(
    title="MCP 自然语言工作流系统",
    description="将自然语言转换为可执行的工作流，并调用 MCP 能力执行",
    version="1.0.0"
)

class WorkflowRequest(BaseModel):
    query: str
    parallel: Optional[bool] = False
    stop_on_error: Optional[bool] = True
    
    class Config:
        schema_extra = {
            "example": {
                "query": "部署 my-app 到生产环境，然后发送钉钉通知",
                "parallel": False,
                "stop_on_error": True
            }
        }

class WorkflowResponse(BaseModel):
    result: Dict[str, Any]
    steps: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "result": {
                    "workflow_description": "部署并通知",
                    "total_steps": 2,
                    "completed_steps": 2,
                    "status": "success"
                },
                "steps": [
                    {
                        "action": "deploy",
                        "params": {"project_name": "my-app", "environment": "production"},
                        "status": "success",
                        "duration": 2.5
                    }
                ]
            }
        }

@app.get("/")
def root():
    """根路径，返回系统信息"""
    return {
        "name": "MCP 自然语言工作流系统",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "workflow": "/workflow",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "mcp-workflow"
    }

@app.post("/workflow", response_model=WorkflowResponse, summary="执行工作流")
def workflow_endpoint(req: WorkflowRequest):
    """
    将自然语言查询转换为工作流并执行
    
    支持的动作包括：
    - **dingtalk_notify**: 发送钉钉通知
    - **deploy**: 部署到指定环境
    - **upload_file**: 上传文件到服务
    
    示例查询：
    - "发送钉钉消息通知团队部署完成"
    - "部署 frontend 项目到测试环境"
    - "上传日志文件到文档服务"
    """
    try:
        # 1. 调用大模型解析为工作流
        workflow = parse_to_workflow(req.query)
        
        # 添加用户指定的执行选项
        if req.parallel is not None:
            workflow["parallel"] = req.parallel
        if req.stop_on_error is not None:
            workflow["stop_on_error"] = req.stop_on_error
            
        # 2. 执行工作流
        result, steps = execute_workflow(workflow)
        
        return WorkflowResponse(result=result, steps=steps)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统错误: {str(e)}")

@app.get("/test")
def test_workflow():
    """测试端点，运行一个示例工作流"""
    sample_query = "发送钉钉消息说测试成功"
    try:
        workflow = parse_to_workflow(sample_query)
        result, steps = execute_workflow(workflow)
        return WorkflowResponse(result=result, steps=steps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """处理 404 错误"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"路径 {request.url.path} 不存在",
            "available_endpoints": ["/", "/workflow", "/health", "/docs"]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """处理 500 错误"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "服务器内部错误，请稍后重试"
        }
    ) 