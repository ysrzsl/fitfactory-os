"""AI 对话 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from src.ai.client import DeepSeekClient

router = APIRouter()

# 全局 Agent 实例（简单实现，每次对话保持上下文）
_agent: DeepSeekClient | None = None

SYSTEM_PROMPT = """你是 FitFactory OS 的 AI 厂长助理。你的工作是帮助服装厂厂长和助理管理生产。

你可以：
- 查询订单状态和进度
- 执行自动排产
- 模拟插单影响
- 查看产线状态
- 检查延期预警
- 查询即将到期订单
- 查看生产统计数据
- 🔍 搜索工艺标准和 SOP 知识库（面料缩水、设备故障、质检流程等工艺问题必须调用 search_knowledge 工具）

规则：
1. 用中文回答，简洁带数据
2. 涉及排产决策时给出理由和备选
3. 遇到工艺/技术/操作类问题（如面料处理、缩水、故障、流程SOP），必须先调用 search_knowledge 搜索知识库
4. 数字要精确
5. 不要直接说'我无法回答'，先尝试搜索知识库"""


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
def chat_with_ai(req: ChatRequest):
    """与 AI 助手对话"""
    global _agent
    if _agent is None:
        _agent = DeepSeekClient(system_prompt=SYSTEM_PROMPT)

    reply = _agent.ask(req.message)
    return ChatResponse(reply=reply)


@router.post("/reset")
def reset_chat():
    """重置对话上下文"""
    global _agent
    _agent = DeepSeekClient(system_prompt=SYSTEM_PROMPT)
    return {"status": "reset"}
