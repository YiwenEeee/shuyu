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


def _clean_meta_list(items, max_len: int = 6, max_count: int = 8) -> list:
    """清洗 topics/keywords：去空白、去超长(原文句子/长短语)、去重，只留短概念词。"""
    seen, out = set(), []
    for it in items or []:
        if not isinstance(it, str):
            continue
        s = it.strip()
        if not s or len(s) > max_len:  # 超过 max_len 的像原文切片/长短语，丢弃
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= max_count:
            break
    return out


def _norm_sentiment(v) -> str:
    s = str(v or "").strip().lower()
    if s.startswith("pos"):
        return "pos"
    if s.startswith("neg"):
        return "neg"
    return "neu"


def extract_meta(content: str) -> dict:
    """上传时：AI 提取主体(topics)、关键词(keywords)、情绪(sentiment)。"""
    if MOCK:
        return {"topics": ["阅读感悟"], "keywords": ["共鸣"], "sentiment": "neu"}

    system = (
        "你是图书笔记分析助手。从笔记里提取结构化信息，只输出 JSON，不要其他文字。\n"
        "要求：\n"
        "1) topics：3~5 个尽可能「抽象、短小的主题/概念词」，每个 1~4 个字，"
        "例如【时间】【回忆】【自由】；是从内容提炼的概念，禁止输出原文句子或长短语。\n"
        "2) keywords：3~8 个关键词，每个 1~4 个字，代表内容的核心意象/概念，"
        "例如【时间】【记忆】【河床】；不要照抄原文句子。\n"
        "3) sentiment：根据笔记整体情感只取一个：pos（积极/温暖/正向）、"
        "neu（中立/陈述）、neg（消极/低落/悲凉）。\n"
        '格式：{"topics": [词数组], "keywords": [词数组], "sentiment": "pos|neu|neg"}'
    )
    out = _chat(f"请分析下面这条读书笔记：\n{content}", system=system)
    out = _strip_code_fence(out)
    try:
        data = json.loads(out)
        return {
            "topics": _clean_meta_list(data.get("topics", [])),
            "keywords": _clean_meta_list(data.get("keywords", [])),
            "sentiment": _norm_sentiment(data.get("sentiment", "neu")),
        }
    except json.JSONDecodeError as exc:
        raise LLMError(f"AI 元信息返回非 JSON: {out}") from exc


def _strip_code_fence(text: str) -> str:
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()
