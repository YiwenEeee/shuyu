"""轻量向量库 + 笔记池：内存 + JSON 持久化（纯 NumPy 余弦，无本地向量库）。

记录 = 已入池的笔记（只有 isPublic=true 且 reviewStatus=approved 才入池）。
"""

from __future__ import annotations

import json
import os
import threading
from typing import Dict, List, Optional, Tuple

import numpy as np

from .rag_config import config


class RagStore:
    def __init__(self, path: Optional[str] = None):
        self.path = path or config.vector_store_path
        self._lock = threading.Lock()
        self._records: Dict[int, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.path and os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._records = {int(k): v for k, v in json.load(f).items()}
            except Exception as exc:  # noqa: BLE001
                print(f"[rag_store] 加载失败，忽略: {exc}")

    def _save(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({str(k): rec for k, rec in self._records.items()}, f)

    def upsert(self, note_id: int, record: dict) -> None:
        with self._lock:
            self._records[note_id] = record
            self._save()

    def delete(self, note_id: int) -> None:
        with self._lock:
            if note_id in self._records:
                del self._records[note_id]
                self._save()

    def get(self, note_id: int) -> Optional[dict]:
        return self._records.get(note_id)

    def all_records(self) -> Dict[int, dict]:
        return self._records

    def search(self, query: List[float], exclude_ids: set[int] | None = None) -> List[Tuple[int, float]]:
        """返回池中所有记录 (note_id, 余弦相似度)，按分数降序；exclude_ids 优先排除。"""
        q = np.asarray(query, dtype=np.float32).reshape(1, -1)
        exclude_ids = exclude_ids or set()
        ids = [nid for nid in self._records if nid not in exclude_ids]
        if not ids:
            return []
        vecs = [self._records[i]["vector"] for i in ids]
        mat = np.asarray(vecs, dtype=np.float32)
        qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-9)
        mn = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9)
        scores = (mn @ qn.T).flatten()
        order = np.argsort(-scores)
        return [(ids[i], float(scores[i])) for i in order]

