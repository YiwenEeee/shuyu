"""RAG 核心链路（D2 生死线）。

流程：笔记上传 -> embedding 存向量 -> query -> NumPy 余弦检索 Top-N
      -> 按相似度分档生成推荐语。
对外提供：
  - index_note(note_id, content): 上传时向量化入库
  - match(note_id, content): 发起匹配，返回 [{matched_note_id, similarity_score,
                            recommendation_text, tier}]
"""

from __future__ import annotations

from typing import Dict, List

from .embedding import embed_texts
from .feedback import build_feedback
from .rag_config import config
from .vector_store import VectorStore


class RagService:
    def __init__(
        self,
        store: VectorStore | None = None,
        note_texts: Dict[int, str] | None = None,
    ):
        self.store = store or VectorStore()
        # 真实链路中由数据库提供 note_id -> 正文；demo/集成时注入
        self._note_texts = note_texts or {}

    def index_note(self, note_id: int, content: str) -> Dict[str, object]:
        """笔记上传时调用：文本转向量并入库。"""
        vec = embed_texts([content])[0]
        self.store.upsert(note_id, vec)
        return {"note_id": note_id, "vector_dim": len(vec)}

    def match_one(
        self,
        note_id: int,
        content: str,
        topic: str = "",
    ) -> Dict[str, object]:
        query_vec = embed_texts([content])[0]
        hits = self.store.search(query_vec, config.top_n, exclude_ids={note_id})

        if not hits:
            # 无候选 -> 兜底
            text, tier = build_feedback(topic, [], [], 0.0, config)
            return {
                "matched_note_id": None,
                "similarity_score": 0.0,
                "recommendation_text": text,
                "tier": tier,
            }

        # 取出 Top-N 原文供生成推荐语用（此处用向量库记录无法还原正文，
        # 因此由外部提供 note 正文映射，注入到近邻匹配。）
        top_ids = [nid for nid, _ in hits]
        best_score = hits[0][1]

        top_texts = [self._note_texts.get(nid, "") for nid in top_ids]
        text, tier = build_feedback(topic, top_texts, [s for _, s in hits], best_score, config)

        return {
            "matched_note_id": top_ids[0],
            "similarity_score": round(best_score, 4),
            "recommendation_text": text,
            "tier": tier,
        }


# 模块级单例，方便 B 后端直接 import
rag = RagService()
