"""RAG 链路端到端演示脚本（D2 验收用）。

演示：只入池「公开+已过审」笔记；私密/未过审不入池；漂流瓶排除自己；
      上报 AI 元信息（主体/关键词/情绪）；返回 matched_user_id。

用法：
  # 无 key 本地验证链路逻辑（用 mock embedding / LLM）
  python -m app.rag_demo --mock

  # 真实模式（需在 backend/.env 填好两个 key）
  python -m app.rag_demo
"""

from __future__ import annotations

import os
import sys
import tempfile


def _notes() -> list[dict]:
    # (note_id, user_id, topic, content, is_public, status)
    free_like = (
        "自由不只是想做什么就做什么，而是可以不去做自己不想做的事。内心不被绑架，才是真正的自由。"
    )
    free_2 = (
        "所谓长大，就是学会在不想继续的时候停下来。真正的自由，恰恰来自自律与清醒。"
    )
    lonely = "孤独不是没人陪，而是你突然明白了，有些路只能自己走。读书，是给自己找一段安静。"
    return [
        {"note_id": 1, "user_id": 101, "topic": "自由", "content": free_like, "is_public": True, "status": "approved"},
        {"note_id": 2, "user_id": 201, "topic": "孤独", "content": lonely, "is_public": False, "status": "approved"},
        {"note_id": 3, "user_id": 301, "topic": "自由", "content": free_2, "is_public": True, "status": "approved"},
        {"note_id": 4, "user_id": 101, "topic": "自由", "content": free_like, "is_public": True, "status": "approved"},
    ]


def main() -> int:
    mock = "--mock" in sys.argv
    if mock:
        os.environ["RAG_MOCK"] = "1"
        print("[demo] mock 模式（仅本地验证链路逻辑）\n")
    else:
        print("[demo] 真实模式（依赖 SILICONFLOW_API_KEY 与 DEEPSEEK_API_KEY）\n")

    from app.services.rag_service import RagService
    from app.services.vector_store import VectorStore

    notes = _notes()
    note_texts = {n["note_id"]: n["content"] for n in notes}
    note_owners = {n["note_id"]: n["user_id"] for n in notes}
    # 用临时向量库，避免污染 backend/data/vectors.json
    store = VectorStore(path=os.path.join(tempfile.gettempdir(), "shuyu_vectors_demo.json"))
    rag = RagService(store, note_texts=note_texts, note_owners=note_owners)

    # 1. AI 元信息提取（上传时）
    print("== 1. AI 元信息提取（以 note 1 为例）==")
    meta = rag.analyze_note(note_texts[1])
    print(f"   主体 topics:   {meta.get('topics')}")
    print(f"   关键词 keywords: {meta.get('keywords')}")
    print(f"   情绪 sentiment:  {meta.get('sentiment')}")

    # 2. 索引入池（公开+已过审才入）
    print("\n== 2. 索引入池（只有 公开+已过审 才进池）==")
    for n in notes:
        res = rag.index_note(n["note_id"], n["content"], n["is_public"], n["status"], n["user_id"])
        mark = "入池" if res.get("indexed") else f"不入池({res.get('reason')})"
        print(f"   note {n['note_id']:>2} [{n['topic']}] public={n['is_public']} status={n['status']} -> {mark}")

    # 3. 漂流瓶匹配（用户 101 用 note 1 发起，排除自己的 note 1 & 4）
    print("\n== 3. 漂流瓶匹配（用户 101 用 note 1 发起）==")
    my_notes = {n["note_id"] for n in notes if n["user_id"] == 101}
    result = rag.match_one(1, note_texts[1], topic="自由", my_note_ids=my_notes)
    print(f"   匹配到用户 id: {result['matched_user_id']}")
    print(f"   匹配到笔记 id: {result['matched_note_id']}")
    print(f"   匹配度: {result['similarity_score']}")
    print(f"   档位: {result['tier']}")
    print(f"   推荐语: {result['recommendation_text']}")

    print("\n[demo] 链路跑通 OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

