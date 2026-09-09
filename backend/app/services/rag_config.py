"""RAG 链路配置（对齐最终 ziduan.md / houduan API）。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


# 自动读取 backend/.env
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))


@dataclass
class RagConfig:
    # 检索：不设 top_n（分页由 B 控制，默认 pageSize=10）
    match_page_size: int = int(os.getenv("RAG_PAGE_SIZE", "10"))

    # matchScore 0~100 的归一化映射（把余弦相似度线性换算到 0~100，绝不虚构）
    match_low: float = float(os.getenv("MATCH_SCORE_LOW", "0.50"))
    match_high: float = float(os.getenv("MATCH_SCORE_HIGH", "0.92"))

    # 反馈档位阈值（按 matchScore 0~100，不再按余弦相似度）
    strong_threshold: float = float(os.getenv("RAG_STRONG", "85"))
    high_threshold: float = float(os.getenv("RAG_HIGH", "70"))
    weak_threshold: float = float(os.getenv("RAG_WEAK", "55"))

    # 推荐语 只对 Top 多少条生成（避免全池都调 LLM；其余留 null）
    recommend_top_n: int = int(os.getenv("RAG_TOP_N", "3"))

    # embedding
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "1024"))

    # LLM
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "200"))

    # 漂流瓶有效期（入池后 7 天）
    bottle_ttl_days: int = int(os.getenv("BOTTLE_TTL_DAYS", "7"))

    # 向量持久化路径（相对 backend 根目录）
    vector_store_path: str = field(
        default_factory=lambda: os.getenv(
            "VECTOR_STORE_PATH",
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "vectors.json",
            ),
        )
    )


config = RagConfig()
