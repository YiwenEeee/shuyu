"""RAG 核心链路（D2 生死线）。

流程：笔记上传 -> AI 提取元信息 -> embedding 存向量 -> query -> NumPy 余弦检索 Top-N
      -> 按相似度分档生成推荐语。
规则：只有 visibility=public 且 status=approved 的笔记才向量化进池；
      私密 / 未过审 / 被拒的笔记只存储、不参与匹配；漂流瓶匹配排除自己。
对外提供：
  - analyze_note(content): 上传时提取主体/关键词/情绪
  - index_note(...): 公开+已过审才入池
  - remove_note(note_id): 转私密/被拒/删除时移出池
  - match_one(...): 漂流瓶匹配，返回 matched_user_id/matched_note_id/
                    similarity_score/recommendation_text/tier
"""

from __future__ import annotations

from typing import Dict, Set

from .embedding import embed_texts
from .feedback import build_feedback
from .llm import extract_meta
from .rag_config import config
from .vector_store import VectorStore


class RagService:
    def __init__(
        self,
        store: VectorStore | None = None,
        note_texts: Dict[int, str] | None = None,
        note_owners: Dict[int, int] | None = None,
    ):
        self.store = store or VectorStore()
        # 真实链路中由数据库提供 note_id -> 正文；demo/集成时注入
        self._note_texts = note_texts or {}
        # note_id -> user_id，用于返回 matched_user_id
        self._note_owners = note_owners or {}

    def analyze_note(self, content: str) -> Dict[str, object]:
        """上传时调用：AI 提取主体 / 关键词 / 情绪。"""
        return extract_meta(content)

    def index_note(
        self,
        note_id: int,
        content: str,
        is_public: bool,
        status: str,
        owner_id: int | None = None,
    ) -> Dict[str, object]:
        """笔记向量化入池。只有 visibility=public 且 status=approved 才进池。"""
        if not (is_public and status == "approved"):
            return {"note_id": note_id, "indexed": False, "reason": "未入池：需公开且已过审"}
        vec = embed_texts([content])[0]
        self.store.upsert(note_id, vec)
        if owner_id is not None:
            self._note_owners[note_id] = owner_id
        return {"note_id": note_id, "indexed": True, "vector_dim": len(vec)}

    def remove_note(self, note_id: int) -> None:
        """笔记转私密 / 被拒 / 删除时移出池。"""
        self.store.delete(note_id)

    def match_one(
        self,
        note_id: int,
        content: str,
        topic: str = "",
        my_note_ids: Set[int] | None = None,
    ) -> Dict[str, object]:
        query_vec = embed_texts([content])[0]
        # 排除当前笔记 + 自己所有笔记，避免匹配到自己
        exclude = set(my_note_ids or set()) | {note_id}
        hits = self.store.search(query_vec, config.top_n, exclude_ids=exclude)

        if not hits:
            # 无候选 -> 兜底
            text, tier = build_feedback(topic, [], [], 0.0, config)
            return {
                "matched_user_id": None,
                "matched_note_id": None,
                "similarity_score": 0.0,
                "recommendation_text": text,
                "tier": tier,
            }

        top_ids = [nid for nid, _ in hits]
        best_score = hits[0][1]
        top_texts = [self._note_texts.get(nid, "") for nid in top_ids]
        text, tier = build_feedback(topic, top_texts, [s for _, s in hits], best_score, config)

        return {
            "matched_user_id": self._note_owners.get(top_ids[0]),
            "matched_note_id": top_ids[0],
            "similarity_score": round(best_score, 4),
            "recommendation_text": text,
            "tier": tier,
        }


# 模块级单例，方便 B 后端直接 import
rag = RagService()

