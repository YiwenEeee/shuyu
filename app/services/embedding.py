"""Embedding 服务：调用硅基流动 bge-m3 把笔记文本转成向量。

支持 batch、超时、失败重试；另提供 mock 模式用于无 key 时本地验证链路。
"""

from __future__ import annotations

import os
import time
from typing import List

from .rag_config import config

SILICONFLOW_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1/embeddings")
MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
MOCK = os.getenv("RAG_MOCK", "0") == "1"  # 开发/测试用，默认不走 mock


class EmbeddingError(RuntimeError):
    """embedding 调用失败。"""


def _embed_siliconflow(texts: List[str]) -> List[List[float]]:
    import httpx

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise EmbeddingError("缺少 SILICONFLOW_API_KEY")

    # 简单 batch，避免一次塞太多文本；超时 & 重试
    results: List[List[float]] = []
    batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "10"))
    for start in range(0, len(texts), batch_size):
        chunk = texts[start : start + batch_size]
        data = None
        for attempt in range(3):
            try:
                resp = httpx.post(
                    SILICONFLOW_URL,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": MODEL, "input": chunk},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()["data"]
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    raise EmbeddingError(f"embedding 请求失败: {exc}") from exc
                time.sleep(1 + attempt)

        # 按 index 排序，保证顺序稳定
        data = sorted(data, key=lambda x: x["index"])
        results.extend([item["embedding"] for item in data])

    return results


def _mock_embed(texts: List[str]) -> List[List[float]]:
    """确定性 mock：按字 + 双字组合散列到向量，共享关键词的文本分数更高。仅供本地验证。"""
    import hashlib
    import re

    dim = config.embedding_dim
    out: List[List[float]] = []
    for text in texts:
        vec = [0.0] * dim
        cjk = re.findall(r"[\u4e00-\u9fff]", text)
        words = re.findall(r"[A-Za-z0-9]+", text)
        grams = cjk + words
        grams += [cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1)]  # 双字组合≈词
        if not grams:  # 空文本给个默认
            grams = ["\x00"]
        for gram in grams:
            h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
            vec[h % dim] += 1.0
        # L2 归一化，便于余弦
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        out.append(vec)
    return out


def embed_texts(texts: List[str]) -> List[List[float]]:
    """公开入口：把一批文本转成向量。"""
    if MOCK:
        return _mock_embed(texts)
    return _embed_siliconflow(texts)
