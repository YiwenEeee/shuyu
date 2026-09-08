"""RAG 链路端到端演示脚本（D2 验证用）。

用法：
  # 真实模式（需在 backend/.env 填好两个 key）
  python -m app.rag_demo

  # 无 key 本地验证链路逻辑（用 mock embedding / LLM）
  python -m app.rag_demo --mock
"""

from __future__ import annotations

import os
import sys


def _demo_notes() -> list[tuple[int, str, str]]:
    # (note_id, 主题, 正文)
    return [
        (
            1,
            "自由",
            "自由不是想做什么就做什么，而是不想做什么就可以不做什么。真正的自由，是内心不被绑架。",
        ),
        (
            2,
            "孤独",
            "孤独不是没人陪，而是你突然明白了，有些路只能自己走。读书，是给自己找一段安静。",
        ),
        (
            3,
            "自由",
            "所谓长大，就是学会在该停的时候停下来。自由，恰恰来自自律与清醒。",
        ),
        (
            4,
            "自由",
            "自由不只是想做什么就做什么，而是可以不去做自己不想做的事。内心不被绑架，才是真正的自由。",
        ),
    ]


def main() -> int:
    mock = "--mock" in sys.argv
    if mock:
        os.environ["RAG_MOCK"] = "1"
        print("[demo] 使用 mock 模式（本地验证链路逻辑）\n")
    else:
        print("[demo] 真实模式，依赖 SILICONFLOW_API_KEY 与 DEEPSEEK_API_KEY\n")

    from app.services.rag_service import RagService
    from app.services.vector_store import VectorStore

    store = VectorStore()
    notes = _demo_notes()
    note_texts = {nid: content for nid, topic, content in notes}
    rag = RagService(store, note_texts=note_texts)

    # 1. 上传 -> 向量化入库
    print("== 1. 索引笔记 ==")
    for nid, topic, content in notes:
        rag.index_note(nid, content)
        print(f"   note_id={nid} 入库成功")

    # 2. 用 note_id=1 发起匹配
    print("\n== 2. 发起匹配（以 note_id=1 为 query）==")
    query_id, query_topic, query_content = notes[0]
    result = rag.match_one(query_id, query_content, topic=query_topic)
    print(f"   匹配到的笔记 id: {result['matched_note_id']}")
    print(f"   相似度: {result['similarity_score']}")
    print(f"   档位: {result['tier']}")
    print(f"   推荐语: {result['recommendation_text']}")

    print("\n[demo] 链路跑通 OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
