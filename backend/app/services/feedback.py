"""推荐反馈语分档：根据相似度分数选择 S/A/B/C 档并生成文案。

对应 feedback_rules.md：
  - S / A 档：让 DeepSeek 生成个性化推荐语
  - B 档：模板 + Top-N 原文
  - C 档：固定兜底模板
"""

from __future__ import annotations

from typing import List, Optional

from .llm import chat
from .rag_config import RagConfig


def tier_for(score: float, cfg: RagConfig) -> str:
    """分数 -> 档位。"""
    if score >= cfg.strong_threshold:
        return "S"
    if score >= cfg.high_threshold:
        return "A"
    if score >= cfg.weak_threshold:
        return "B"
    return "C"


def _fallback_c() -> str:
    return "这次还没遇到真正同频的人。再上传一条笔记，命运的齿轮随时会转。"


def _template_b(top_texts: List[str]) -> str:
    candidates = "；".join([t[:40] for t in top_texts[:2]])
    if candidates:
        return f"你们读的是同一本书，但各自抓住的点不太一样——说不定正好能互补。（TA 的摘录：{candidates}…）"
    return "你们读的是同一本书，但各自抓住的点不太一样——说不定正好能互补。"


def _prompt_for_s(topic: str, texts: List[str], score: float, tier: str) -> tuple[str, str]:
    # 生成个性化推荐语的 prompt
    content = "\n".join([f"- {t}" for t in texts])
    vibe = "几乎说到一块去了，直击灵魂" if tier == "S" else "同书同感，但角度略有不同"
    prompt = (
        f"以下是用户 A 的一条读书笔记主题「{topic}」以及检索到的用户 B 的最相近摘录（相似度 {score:.2f}）：\n"
        f"{content}\n\n"
        f"请用 30 字以内，为 A 写一段推荐语，介绍 TA 与 B 的『{vibe}』，"
        "语气真诚、有温度，不要用『亲』『您』等称呼，不要发感叹号堆砌。"
    )
    return prompt, "你是一个懂读书、擅长用文字连接同频者的推荐官。"


def build_feedback(
    topic: str,
    top_texts: List[str],
    scores: List[float],
    best_score: float,
    cfg: RagConfig,
) -> tuple[str, str]:
    """返回 (文案, 档位)。"""
    tier = tier_for(best_score, cfg)
    if tier in ("S", "A"):
        prompt, system = _prompt_for_s(topic, top_texts, best_score, tier)
        return chat(prompt, system=system), tier
    if tier == "B":
        return _template_b(top_texts), tier
    return _fallback_c(), tier

