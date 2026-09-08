"""RAG 链路配置。

阈值 / Top-N / 向量维度都集中在这里，D3 调优时只改本文件。
与 feedback_rules.md 的分档保持一致。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class RagConfig:
    # 检索
    top_n: int = int(os.getenv("RAG_TOP_N", "3"))          # 返回条数（待 B/A 定，默认 3）

    # 相似度分档阈值（余弦相似度，0~1），对应 feedback_rules.md
    strong_threshold: float = float(os.getenv("RAG_STRONG", "0.70"))  # S · 灵魂共振
    high_threshold: float = float(os.getenv("RAG_HIGH", "0.50"))      # A · 高相关
    weak_threshold: float = float(os.getenv("RAG_WEAK", "0.30"))      # B · 一般相关，低于此值兜底 C

    # embedding
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "1024"))      # bge-m3 固定 1024

    # LLM
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "200"))

    # 向量持久化路径（相对于 backend 根目录；不存在则仅内存）
    vector_store_path: str = field(
        default_factory=lambda: os.getenv(
            "VECTOR_STORE_PATH",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vectors.json"),
        )
    )


config = RagConfig()

