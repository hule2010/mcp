# MCP 自然语言工作流系统

这是一个基于大模型的工作流系统，可以将用户的自然语言描述转换为可执行的工作流，并调用 MCP（Model Context Protocol）的各种能力。

## 功能特点

- 🤖 使用 DeepSeek 大模型理解自然语言意图
- 🔄 自动生成结构化工作流
- 📢 支持钉钉通知
- 🚀 支持环境部署
- 📁 支持文件上传
- ⚡ 支持并行和顺序执行
- 🔍 详细的执行日志和状态跟踪

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp env.example .env

# 编辑 .env 文件，填入你的 API 密钥和配置
```

### 3. 启动服务

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. 测试工作流

```bash
python test_workflow.py
```

## API 使用

### 创建工作流

**请求:**
```bash
POST http://localhost:8000/workflow
Content-Type: application/json

{
    "query": "部署 my-app 到生产环境，然后发送钉钉通知"
}
```

**响应:**
```json
{
    "result": {
        "workflow_description": "部署应用并通知",
        "total_steps": 2,
        "completed_steps": 2,
        "status": "success"
    },
    "steps": [
        {
            "action": "deploy",
            "params": {
                "project_name": "my-app",
                "environment": "production"
            },
            "status": "success",
            "duration": 2.5
        },
        {
            "action": "dingtalk_notify",
            "params": {
                "message": "my-app 已成功部署到生产环境"
            },
            "status": "success",
            "duration": 0.3
        }
    ]
}
```

## 支持的动作

### 1. 钉钉通知 (dingtalk_notify)
- `message`: 通知消息内容
- `at_mobiles`: @特定手机号列表（可选）
- `is_at_all`: 是否@所有人（可选）

### 2. 环境部署 (deploy)
- `environment`: 目标环境（dev/test/prod）
- `project_name`: 项目名称
- `version`: 版本号（可选）
- `config`: 部署配置（可选）

### 3. 文件上传 (upload_file)
- `file_path`: 文件路径
- `service_name`: 目标服务名称
- `metadata`: 文件元数据（可选）

## 工作流示例

### 简单通知
```
"给团队发送钉钉消息说今天的会议改到下午3点"
```

### 部署流程
```
"将 backend-api 的 v1.2.3 版本部署到测试环境"
```

### 复杂工作流
```
"先部署前端项目到生产环境，然后上传部署报告，最后通知所有人部署完成"
```

## 高级功能

### 并行执行
在工作流中设置 `"parallel": true` 可以并行执行所有步骤。

### 错误处理
设置 `"stop_on_error": false` 可以在某个步骤失败后继续执行。

### 上下文引用
使用 `${variable}` 语法可以引用之前步骤的结果。

## 开发指南

### 添加新的 MCP 动作

1. 在 `llm_parser.py` 的 `AVAILABLE_ACTIONS` 中添加动作定义
2. 在 `mcp_client.py` 中实现对应的执行方法
3. 更新 `action_map` 映射

### 自定义工作流逻辑

修改 `workflow_executor.py` 中的执行逻辑，可以实现：
- 条件执行
- 循环执行
- 错误重试
- 自定义上下文处理

## 注意事项

1. 确保所有 API 密钥都已正确配置
2. 部署和文件上传功能需要对应的后端服务支持
3. 钉钉机器人需要配置安全设置（关键词/加签/IP白名单）
4. 建议在生产环境中添加认证和速率限制

## 故障排除

### 常见问题

1. **ImportError**: 确保已安装所有依赖
2. **API 调用失败**: 检查环境变量配置
3. **工作流解析失败**: 查看日志确认大模型返回格式

### 日志查看

```bash
# 查看应用日志
tail -f uvicorn.log

# 调试模式
export DEBUG=true
uvicorn app:app --reload --log-level debug
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 