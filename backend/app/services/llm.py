"""LLM 服务：调用 DeepSeek 生成推荐语 / 提取元信息。

OpenAI 兼容接口。同样提供 mock 模式用于本地验证。
"""

from __future__ import annotations

import os
import json
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


def _mock_extract_meta(content: str) -> dict:
    return {"topics": ["读书感悟"], "keywords": ["共鸣"], "sentiment": "neu"}


def extract_meta(content: str) -> dict:
    """上传笔记时提取主体(topics)、关键词(keywords)、情绪(sentiment)。"""
    if MOCK:
        return _mock_extract_meta(content)

    import httpx

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise LLMError("缺少 DEEPSEEK_API_KEY")

    system = (
        "你是图书笔记分析助手。只输出 JSON，不要其他文字。"
        '格式：{"topics": [字符串数组], "keywords": [字符串数组], "sentiment": "pos|neu|neg"}'
    )
    prompt = f"请分析下面这条读书笔记更短一些：\n{content}"
    resp = httpx.post(
        DEEPSEEK_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 200,
        },
        timeout=60,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    # 宽容解析：去掉可能的 ```json 包裹
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMError(f"AI 元信息返回非 JSON: {text}") from exc
