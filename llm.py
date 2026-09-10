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


_PUNCT = set("，。！？、；：,.!?;:…—～()（）「」『』《》\"'“”‘’@#￥%&*+/\\|<>[]{}·")
_FRAG_START = ("最", "很", "太", "这", "那")
_FRAG_END = ("了", "着", "过", "完", "吗", "呢", "吧", "啊")


def _clean_meta_list(items, content: str = "", max_len: int = 4, max_count: int = 8) -> list:
    """清洗 topics/keywords：只保留 1~4 字的抽象短词；去标点/空白/明显片段、去重、去原文子串。"""
    content = content or ""
    seen, out = set(), []
    for it in items or []:
        if not isinstance(it, str):
            continue
        s = it.strip()
        if not s or len(s) > max_len:  # 超过 4 字的像原文切片/长短语，丢弃
            continue
        if any((ch in _PUNCT) or ch.isspace() or ch.isdigit() for ch in s):
            continue
        if s.startswith(_FRAG_START) or s.endswith(_FRAG_END):  # 明显的片段（如"读完""最触动…"）
            continue
        if content and len(s) >= 3 and s in content:  # 是原文子串（≥3 字）→ 视为原文切片
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
        "你是图书笔记的【概念提炼】助手。只输出 JSON，不要其他文字。\n"
        "核心要求：提炼【抽象名词概念】，不要摘抄原文。\n"
        "1) topics：3~5 个**抽象名词**，每个 **1~4 个字**，代表笔记主题，"
        "例如【理想】【勇气】【现实】【自由】【孤独】【成长】。\n"
        "   ——禁止输出动词短语、句子片段或原文摘抄；『读完』『最触动我的是』『满地都是六便士』这类都不算主题词。\n"
        "2) keywords：3~8 个**名词性关键词**，每个 **1~4 个字**，例如【理想】【勇气】【现实】；同样禁止原文摘抄。\n"
        "3) sentiment：必须根据情感判断，不要默认中性——出现喜悦/感动/温暖判 pos，"
        "出现低落/悲伤/愤懑/失落判 neg，确实中立/纯陈述才判 neu。\n"
        '格式：{"topics": [名词数组], "keywords": [名词数组], "sentiment": "pos|neu|neg"}'
    )
    out = _chat(f"请分析下面这条读书笔记：\n{content}", system=system)
    out = _strip_code_fence(out)
    try:
        data = json.loads(out)
        return {
            "topics": _clean_meta_list(data.get("topics", []), content),
            "keywords": _clean_meta_list(data.get("keywords", []), content),
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
