"""轻量向量库：内存 + JSON 持久化（纯 NumPy 余弦，无需本地向量库）。"""

from __future__ import annotations

import json
import os
import threading
from typing import Dict, List, Tuple

import numpy as np

from .rag_config import config


class VectorStore:
    """以 note_id 为键存向量，支持余弦检索 Top-N。"""

    def __init__(self, path: str | None = None):
        self.path = path or config.vector_store_path
        self._lock = threading.Lock()
        self._vectors: Dict[int, np.ndarray] = {}
        self._load()

    def _load(self) -> None:
        if self.path and os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._vectors = {int(k): np.asarray(v, dtype=np.float32) for k, v in raw.items()}
            except Exception as exc:  # noqa: BLE001
                print(f"[vector_store] 加载失败，忽略: {exc}")

    def _save(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        raw = {str(k): v.tolist() for k, v in self._vectors.items()}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(raw, f)

    def upsert(self, note_id: int, vector: List[float]) -> None:
        with self._lock:
            self._vectors[note_id] = np.asarray(vector, dtype=np.float32)
            self._save()

    def search(
        self, query: List[float], top_n: int, exclude_ids: set[int] | None = None
    ) -> List[Tuple[int, float]]:
        """返回 [(note_id, 余弦相似度)]，按分数降序。"""
        q = np.asarray(query, dtype=np.float32)
        if q.ndim == 1:
            q = q.reshape(1, -1)
        if not self._vectors:
            return []
        exclude_ids = exclude_ids or set()
        ids = [i for i in self._vectors.keys() if i not in exclude_ids]
        if not ids:
            return []
        mat = np.stack([self._vectors[i] for i in ids]).astype(np.float32)
        # 归一化后点积 = 余弦
        qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-9)
        mn = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9)
        scores = (mn @ qn.T).flatten()
        order = np.argsort(-scores)[:top_n]
        return [(ids[i], float(scores[i])) for i in order]

    def size(self) -> int:
        return len(self._vectors)
