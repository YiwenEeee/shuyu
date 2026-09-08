"""RAG 链路 D2 验收演示（对齐最终 ziduan.md / houduan API）。

验证点：
  1. 上传时 AI 三栏（主体/关键词/情绪）
  2. 只有 isPublic=true 且 reviewStatus=approved 才入池（私密/未过审不入）
  3. 智能匹配（非随机）：matchScore 0~100 降序，排除本人，返回嵌套 author/book
  4. 推荐语（可用于空），绝不虚构分数

用法：
  python -m app.rag_demo --mock     # 无 key，验证链路逻辑
  python -m app.rag_demo            # 真实模式（需 backend/.env 填 key）
"""

from __future__ import annotations

import os
import sys
import tempfile


def _notes() -> list[dict]:
    free = "自由不是想做什么就做什么，而是可以不去做自己不想做的事。内心不被绑架，才是真正的自由。"
    free2 = "所谓长大，就是学会在不想继续的时候停下来。真正的自由，恰恰来自自律与清醒。"
    time_memory = "我们总在回忆中重新理解时间。书里的记忆，像一条往回流的河。"
    lonely = "孤独不是没人陪，而是你突然明白了，有些路只能自己走。读书，是给自己找一段安静。"

    def author(uid, name):
        return {"userId": uid, "nickname": name, "avatarPath": f"/uploads/avatars/u{uid}.png"}

    def book(bid):
        return {"bookId": bid, "title": "百年孤独", "author": "加西亚·马尔克斯",
                "coverPath": f"/uploads/covers/b{bid}.png", "status": "active"}

    return [
        {"noteId": 1, "author": author(101, "山间读者"), "book": book(101), "content": free,
         "isPublic": True, "reviewStatus": "approved"},
        {"noteId": 2, "author": author(201, "晚风读者"), "book": book(101), "content": lonely,
         "isPublic": False, "reviewStatus": "approved"},  # 私密 -> 不入池
        {"noteId": 3, "author": author(301, "夜航读者"), "book": book(101), "content": free2,
         "isPublic": True, "reviewStatus": "approved"},
        {"noteId": 4, "author": author(101, "山间读者"), "book": book(101), "content": free,
         "isPublic": True, "reviewStatus": "approved"},  # 本人另一条，会被排除
        {"noteId": 5, "author": author(501, "晴耕读者"), "book": book(102), "content": time_memory,
         "isPublic": True, "reviewStatus": "pending"},    # 未过审 -> 不入池
        {"noteId": 6, "author": author(601, "松间读者"), "book": book(101), "content":
         "自由是能拒绝自己不想做的事，不被别人绑架。人这一生，最难的是内心自洽。",
         "isPublic": True, "reviewStatus": "approved"},   # 与 note1 相近 -> 高分
    ]


def main() -> int:
    mock = "--mock" in sys.argv
    if mock:
        os.environ["RAG_MOCK"] = "1"
        print("[demo] mock 模式（仅本地验证链路逻辑）\n")
    else:
        print("[demo] 真实模式（依赖 SILICONFLOW_API_KEY / DEEPSEEK_API_KEY）\n")

    from app.services.rag_service import RagService
    from app.services.vector_store import RagStore

    notes = _notes()
    store = RagStore(path=os.path.join(tempfile.gettempdir(), "shuyu_rag_demo.json"))
    rag = RagService(store)

    # 1) 上传时 AI 三栏
    print("== 1. 上传时 AI 三栏（以 note 1 为例）==")
    meta = rag.analyze_note(notes[0]["content"])
    print(f"   主体 topics:   {meta.get('topics')}")
    print(f"   关键词 keywords: {meta.get('keywords')}")
    print(f"   情绪 sentiment:  {meta.get('sentiment')}")

    # 2) 入池（审核通过且公开）
    print("\n== 2. 入池（只有 公开 + 已过审 才入池）==")
    published = []
    for n in notes:
        res = rag.publish_note(
            n["noteId"], n["content"], n["author"], n["book"], n["isPublic"], n["reviewStatus"]
        )
        mark = "入池" if res.get("published") else f"不入池({res.get('reason')})"
        print(f"   note {n['noteId']:>2} public={n['isPublic']} review={n['reviewStatus']} -> {mark}")
        if res.get("published"):
            published.append(n["noteId"])

    # 3) 模拟 AI 异步处理完成
    for nid in published:
        rag.mark_ai_ready(nid)

    # 4) 智能匹配（用户 101 用 note 1，排除本人两条）
    print("\n== 3. 智能匹配（用户 101 用 note 1，排除本人 note 1&4）==")
    my_notes = {n["noteId"] for n in notes if n["author"]["userId"] == 101}
    results = rag.match(1, notes[0]["content"], my_note_ids=my_notes)
    for r in results:
        print(f"   bottleId={r['bottleId']} noteId={r['noteId']} 作者={r['author']['nickname']}"
              f" 匹配度={r['matchScore']}% aiStatus={r['aiStatus']}")
        print(f"       推荐语: {r['recommendation']}")
        print(f"       摘要: {r['contentPreview'][:24]}…")

    print("\n[demo] D2 链路跑通 OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
