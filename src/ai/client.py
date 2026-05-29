"""
DeepSeek API 客户端
使用 OpenAI 兼容 SDK 调用 DeepSeek
"""
import os
from openai import OpenAI
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """获取 DeepSeek 客户端单例"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
    return _client


def chat(messages: list[dict], tools: list[dict] | None = None, model: str = "deepseek-chat") -> dict:
    """
    调用 DeepSeek Chat API

    Args:
        messages: 对话历史 [{"role": "system/user/assistant", "content": "..."}]
        tools: Function Calling 工具定义列表
        model: 模型名称

    Returns:
        API 响应
    """
    client = get_client()
    kwargs = dict(
        model=model,
        messages=messages,
        temperature=0.3,  # 低温度保证稳定输出
        max_tokens=2048,
    )
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    return client.chat.completions.create(**kwargs)


class DeepSeekClient:
    """高级封装：支持多轮 Function Calling 循环"""

    def __init__(self, system_prompt: str = ""):
        self.system_prompt = system_prompt
        self.messages: list[dict] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def ask(self, user_message: str) -> str:
        """发送用户消息，返回 AI 文本回复"""
        from src.ai.tools import TOOL_DEFINITIONS as tools, execute_tool

        self.messages.append({"role": "user", "content": user_message})
        response = chat(self.messages, tools=tools)
        msg = response.choices[0].message

        # 处理 Function Calling 循环（最多 5 轮防无限）
        loop = 0
        while msg.tool_calls and loop < 5:
            loop += 1
            self.messages.append(msg)

            for tc in msg.tool_calls:
                result = execute_tool(tc.function.name, tc.function.arguments)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            response = chat(self.messages, tools=tools)  # ← 修复：传入 tools
            msg = response.choices[0].message

        reply = msg.content or ""
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def clear(self):
        """清空对话历史"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
