"""RAG 核心链路（C · D2 生死线）· 对齐最终 ziduan.md / houduan API。

流程：
  - 上传笔记：analyze_note(content) -> {topics, keywords, sentiment}（AI 三栏，实时）
  - 审核通过且公开：publish_note(...) 入池（embedding + 创建漂流瓶，aiStatus）
  - 智能匹配：match(source_note_id, source_content, my_note_ids, exclude_note_ids)
      -> 按 matchScore 0~100 降序的候选列表（推荐语可空，绝不虚构分数）
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

from .embedding import embed_texts
from .llm import extract_meta, generate_recommendation
from .rag_config import config
from .vector_store import RagStore


def _score_to_100(cosine: float) -> float:
    """把余弦相似度线性归一化到 0~100（真实转换，不虚构）。"""
    lo, hi = config.match_low, config.match_high
    if hi <= lo:
        return round(max(0.0, min(1.0, cosine)) * 100, 1)
    x = (cosine - lo) / (hi - lo)
    x = max(0.0, min(1.0, x))
    return round(x * 100, 1)


class RagService:
    def __init__(self, store: RagStore | None = None):
        self.store = store or RagStore()
        self._bottle_seq = 0

    # ---- 上传：AI 三栏 ----
    def analyze_note(self, content: str) -> Dict[str, object]:
        return extract_meta(content)

    # ---- 入池（审核通过且公开时由 B 调用）----
    def publish_note(
        self,
        note_id: int,
        content: str,
        author: dict,
        book: dict,
        is_public: bool,
        review_status: str,
    ) -> Dict[str, object]:
        """只有 isPublic=true 且 reviewStatus=approved 才入池、建瓶、启动 AI。"""
        if not (is_public and review_status == "approved"):
            return {"noteId": note_id, "published": False, "reason": "需公开且已过审"}

        vec = embed_texts([content])[0]
        self._bottle_seq += 1
        bottle_id = self._bottle_seq + note_id * 1000  # 生成一个稳定瓶 id
        created_at = datetime.now(timezone.utc).isoformat()
        expires_at = (datetime.now(timezone.utc) + timedelta(days=config.bottle_ttl_days)).isoformat()
        self.store.upsert(
            note_id,
            {
                "vector": vec,
                "text": content,
                "author": author,
                "book": book,
                "is_public": is_public,
                "review_status": review_status,
                "bottle_id": bottle_id,
                "status": "active",
                "ai_status": "processing",  # 入池即启动 AI 任务
                "created_at": created_at,
                "expires_at": expires_at,
            },
        )
        return {"noteId": note_id, "published": True, "bottleId": bottle_id, "dim": len(vec)}

    def remove_note(self, note_id: int) -> None:
        """转私密 / 被拒 / 删除时移出池。"""
        self.store.delete(note_id)

    def mark_ai_ready(self, note_id: int) -> bool:
        rec = self.store.get(note_id)
        if not rec:
            return False
        rec["ai_status"] = "ready"
        self.store.upsert(note_id, rec)
        return True

    # ---- 智能匹配 ----
    def match(
        self,
        source_note_id: int,
        source_content: str,
        my_note_ids: Set[int] | None = None,
        exclude_note_ids: Set[int] | None = None,
    ) -> List[dict]:
        """对一篇来源笔记，返回合格池按 matchScore 降序的候选列表。"""
        source_vec = embed_texts([source_content])[0]
        exclude = set(my_note_ids or set()) | set(exclude_note_ids or set()) | {source_note_id}
        hits = self.store.search(source_vec, exclude_ids=exclude)

        now = datetime.now(timezone.utc)
        ranked: List[dict] = []
        for cand_note_id, cosine in hits:
            rec = self.store.get(cand_note_id)
            if not rec:
                continue
            if rec.get("status") != "active" or rec.get("ai_status") != "ready":
                continue
            if rec.get("expires_at") and _parse(rec["expires_at"]) < now:
                continue
            ranked.append({"cosine": cosine, "rec": rec, "noteId": cand_note_id})

        # 按 matchScore 降序，同分 bottleId 降序
        for item in ranked:
            item["matchScore"] = _score_to_100(item["cosine"])
        ranked.sort(key=lambda i: (-i["matchScore"], -i["rec"]["bottle_id"]))

        items: List[dict] = []
        for idx, item in enumerate(ranked):
            rec = item["rec"]
            top_n = config.recommend_top_n
            rec_text = rec["text"]
            recommendation = (
                generate_recommendation(source_content, [rec_text], [item["matchScore"]])
                if idx < top_n
                else None
            )
            items.append(
                {
                    "bottleId": rec["bottle_id"],
                    "author": rec["author"],
                    "book": rec["book"],
                    "status": rec["status"],
                    "aiStatus": rec["ai_status"],
                    "createdAt": rec["created_at"],
                    "expiresAt": rec["expires_at"],
                    "contentPreview": rec_text[:100],
                    "noteId": item["noteId"],
                    "recommendation": recommendation,
                    "matchScore": item["matchScore"],
                }
            )
        return items


def _parse(iso: str) -> datetime:
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return datetime.now(timezone.utc) + timedelta(days=1)


# 模块级单例，方便 B 后端直接 import
rag = RagService()

