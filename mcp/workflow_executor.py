# workflow_executor.py
import asyncio
import json
from typing import Any, Dict, List, Tuple
from datetime import datetime
from mcp_client import call_mcp_api, MCPClient
import llm_parser as Parser
class WorkflowExecutor:
    """工作流执行器"""

    def __init__(self):
        self.client = MCPClient()

    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个工作流步骤"""
        action = step.get("action")
        params = step.get("params", {})
        description = step.get("description", f"执行 {action}")

        # 替换参数中的上下文变量
        resolved_params = self._resolve_params(params, context)

        start_time = datetime.now()
        try:
            # 执行动作
            result = await self.client.execute_action(action, resolved_params)

            # 记录执行结果
            execution_info = {
                "action": action,
                "params": resolved_params,
                "description": description,
                "result": result,
                "status": result.get("status", "success"),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": (datetime.now() - start_time).total_seconds()
            }

            # 更新上下文
            if result.get("status") == "success":
                context[f"step_{action}_result"] = result

            return execution_info

        except Exception as e:
            # 错误处理
            return {
                "action": action,
                "params": resolved_params,
                "description": description,
                "status": "error",
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": (datetime.now() - start_time).total_seconds()
            }

    def _resolve_params(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """解析参数中的上下文引用"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # 从上下文中获取值
                context_key = value[2:-1]
                resolved[key] = context.get(context_key, value)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_params(value, context)
            else:
                resolved[key] = value
        return resolved

    async def execute_workflow_async(self, workflow: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """异步执行工作流"""
        steps = workflow.get("steps", [])
        context = {"workflow": workflow}
        steps_result = []

        # 判断是否可以并行执行
        can_parallel = workflow.get("parallel", False)

        if can_parallel:
            # 并行执行所有步骤
            tasks = [self.execute_step(step, context) for step in steps]
            steps_result = await asyncio.gather(*tasks)
        else:
            # 顺序执行步骤
            for step in steps:
                step_result = await self.execute_step(step, context)
                steps_result.append(step_result)

                # 如果步骤失败且设置了停止标志，则停止执行
                if step_result.get("status") == "error" and workflow.get("stop_on_error", True):
                    break

        # 汇总结果
        summary = {
            "workflow_description": workflow.get("description", "未命名工作流"),
            "total_steps": len(steps),
            "completed_steps": len([s for s in steps_result if s.get("status") != "error"]),
            "failed_steps": len([s for s in steps_result if s.get("status") == "error"]),
            "total_duration": sum(s.get("duration", 0) for s in steps_result),
            "status": "success" if all(s.get("status") != "error" for s in steps_result) else "partial_failure"
        }

        return summary, steps_result

def execute_workflow(workflow: Any) -> Tuple[dict, List[dict]]:
    """
    执行结构化工作流，依次调用 mcp API。
    返回最终结果和每一步的执行信息。
    """
    executor = WorkflowExecutor()

    # 创建新的事件循环来执行异步代码
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(executor.execute_workflow_async(workflow))
    finally:
        loop.close()


if __name__ == '__main__':
    query = "上传文件 report.pdf 到文档服务"
    workflow = Parser.parse_to_workflow(query)
    execute_workflow(workflow)