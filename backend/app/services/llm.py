"""LLM 服务：调用 DeepSeek 生成推荐语 / 提取元信息。

OpenAI 兼容接口。同样提供 mock 模式用于本地验证。
"""

from __future__ import annotations

import os
from typing import Optional

from .rag_config import config

DEEPSEEK_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/chat/completions")
LLM_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
MOCK = os.getenv("RAG_MOCK", "0") == "1"


class LLMError(RuntimeError):
    """LLM 调用失败。"""


def _mock_chat(messages) -> str:
    """mock：直接把用户侧提示拼一段，保证链路能通。"""
    user = messages[-1]["content"] if messages else ""
    # 简化：取提示里的笔记切片，示意"AI 生成的推荐语"
    return "（mock 推荐语）你们在这段文字里遇到了彼此——" + user[:40]


def chat(prompt: str, system: Optional[str] = None) -> str:
    """单一文本提示调用 DeepSeek，返回生成文本。"""
    if MOCK:
        return _mock_chat(
            [{"role": "system", "content": system or ""}, {"role": "user", "content": prompt}]
        )

    import httpx

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise LLMError("缺少 DEEPSEEK_API_KEY")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = httpx.post(
        DEEPSEEK_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": config.llm_temperature,
            "max_tokens": config.llm_max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
