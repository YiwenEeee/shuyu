"""推荐反馈语分档：根据 matchScore(0~100) 选择 S/A/B 档并生成文案。

对应 feedback_rules.md（对齐 D3 定稿：匹配只展示高分书友）：
  - S / A 档：让 DeepSeek 生成个性化推荐语
  - B 档：模板 + Top-N 原文（正向措辞）
  - C 档：只在「列表为空」时由 B/前端展示（不再作为逐条推荐语）
"""

from __future__ import annotations

from typing import List, Optional

from .llm import LLMError, chat
from .rag_config import RagConfig


def tier_for(match_score: float, cfg: RagConfig) -> str:
    """matchScore(0~100) -> 档位。C 不参与逐条推荐。"""
    if match_score >= cfg.strong_threshold:
        return "S"
    if match_score >= cfg.high_threshold:
        return "A"
    return "B"


def empty_hint() -> str:
    """无好匹配时的兜底文案（列表为空 / 全部低于 weak）。"""
    return "这次还没遇到真正同频的人。再上传一条笔记，命运的齿轮随时会转。"


def _template_b(top_texts: List[str]) -> str:
    candidates = "；".join([t[:40] for t in top_texts[:2]])
    if candidates:
        return f"你们读到了同一处共鸣，角度略有不同——说不定正好能互补。（TA 的摘录：{candidates}…）"
    return "你们读到了同一处共鸣，角度略有不同——说不定正好能互补。"


def _personalized(
    source_nick: str,
    cand_nick: str,
    source_content: str,
    candidate_text: str,
    match_score: float,
    tier: str,
) -> str:
    vibe = "几乎说到一块去了，直击灵魂" if tier == "S" else "同书同感，但角度略有不同"
    a_name = (source_nick or "").strip() or "对方"
    b_name = (cand_nick or "").strip() or "对方"
    system = "你是一个懂读书、擅长用文字连接同频者的推荐官。"
    prompt = (
        f"用户（昵称「{a_name}」）的读书笔记：\n{source_content[:200]}\n\n"
        f"用户（昵称「{b_name}」）的最相近摘录（匹配度 {match_score:.0f}%）：\n{candidate_text[:200]}\n\n"
        f"请用 30 字以内，为「{a_name}」写一段推荐语，介绍 TA 与「{b_name}」的『{vibe}』。"
        "语气真诚、有温度，不要用『亲』『您』等称呼，不要堆砌感叹号。"
        "称呼对方时只用上面给出的昵称，不要把 A/B 当作名字写出来。只输出推荐语本身。"
    )
    return chat(prompt, system=system, max_tokens=120)


def build_feedback(
    source_nick: str,
    cand_nick: str,
    source_content: str,
    candidate_text: str,
    match_score: float,
    cfg: RagConfig,
) -> Optional[str]:
    """按匹配度给单条候选生成推荐语；S/A 用 LLM，B 用模板。失败返回 None（不影响分数）。"""
    tier = tier_for(match_score, cfg)
    if tier in ("S", "A"):
        try:
            return _personalized(
                source_nick, cand_nick, source_content, candidate_text, match_score, tier
            )
        except LLMError:
            return None
    return _template_b([candidate_text])
