"""LLM 服务：DeepSeek。

两类 AI 入口（互相独立）：
  1. extract_meta(content) —— 上传时实时提取 主体/关键词/情绪（AI 三栏）
  2. chat(...)             —— 通用对话入口（供反馈档位 / 推荐语统一调用）
提供 mock 模式用于无 key 本地验证。
"""

from __future__ import annotations

import json
import os
from typing import Optional

from .rag_config import config

DEEPSEEK_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/chat/completions")
LLM_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
MOCK = os.getenv("RAG_MOCK", "0") == "1"


class LLMError(RuntimeError):
    """LLM 调用失败。"""


def _chat(prompt: str, system: Optional[str] = None, max_tokens: int = 0) -> str:
    if MOCK:
        return _MOCK_CHAT(prompt)

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
            "max_tokens": max_tokens or config.llm_max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def chat(prompt: str, system: Optional[str] = None, max_tokens: int = 0) -> str:
    """对外公开的对话入口：供反馈档位 / 推荐语统一调用。"""
    return _chat(prompt, system=system, max_tokens=max_tokens)


def _MOCK_CHAT(prompt: str) -> str:
    # 简化 mock：返回一句示意文本，保证链路可跑
    return "这本书里，你们读到了彼此想说的那一句。"


def extract_meta(content: str) -> dict:
    """上传时：AI 提取主体(topics)、关键词(keywords)、情绪(sentiment)。"""
    if MOCK:
        return {"topics": ["读书感悟"], "keywords": ["共鸣"], "sentiment": "neu"}

    system = (
        "你是图书笔记分析助手。只输出 JSON，不要其他文字。"
        '格式：{"topics": [字符串数组], "keywords": [字符串数组], "sentiment": "pos|neu|neg"}'
    )
    out = _chat(f"请分析下面这条读书笔记：\n{content}", system=system)
    out = _strip_code_fence(out)
    try:
        data = json.loads(out)
        return {
            "topics": list(data.get("topics", [])),
            "keywords": list(data.get("keywords", [])),
            "sentiment": str(data.get("sentiment", "neu")),
        }
    except json.JSONDecodeError as exc:
        raise LLMError(f"AI 元信息返回非 JSON: {out}") from exc


def _strip_code_fence(text: str) -> str:
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()
