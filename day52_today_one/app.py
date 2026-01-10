# app.py
from __future__ import annotations

import datetime as dt
import json
import random
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

APP_TITLE = "今日の1個抽選（Want100連動） - Day52"

BASE_DIR = Path(__file__).parent

# ★ day51 の wants.json を参照（同一リポジトリ内の想定）
DAY51_WANTS_PATH = (BASE_DIR.parent / "day51_want100" / "data" / "wants.json").resolve()

# もし day51 が無い/構成が違う時のフォールバック（同フォルダのdata）
FALLBACK_PATH = (BASE_DIR / "data" / "wants.json").resolve()
(FALLBACK_PATH.parent).mkdir(exist_ok=True)

CATEGORIES = ["仕事", "お金", "家族", "体験", "自由", "健康", "その他"]


# --------------------
# utils
# --------------------
def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_wants_path() -> Path:
    """day51のwants.jsonがあればそれを使う。無ければフォールバック。"""
    if DAY51_WANTS_PATH.exists():
        return DAY51_WANTS_PATH
    return FALLBACK_PATH


def load_items(path: Path) -> List[Dict]:
    raw = read_json(path, {"items": []})
    items = raw.get("items", [])
    if isinstance(items, list):
        # 最低限の整形
        out = []
        for it in items:
            if not isinstance(it, dict):
                continue
            it.setdefault("id", "")
            it.setdefault("text", "")
            it.setdefault("category", "その他")
            it.setdefault("done", False)
            it.setdefault("done_at", None)
            it.setdefault("created_at", None)
            out.append(it)
        return out
    return []


def save_items(path: Path, items: List[Dict]):
    write_json(path, {"items": items})


def celebrate_message(done_count: int) -> str:
    if done_count == 1:
        return "🎉 1個目達成！現実が動いた。"
    if done_count == 10:
        return "🎊 10個達成！積み上がってきた。"
    if done_count == 50:
        return "🏆 50個達成！完全に別人の領域。"
    if done_count >= 100:
        return "🌈 100個達成！あなたは現実をデザインした。"
    return "✨ おめでとう。今日の1個、完了。"


def pick_one(items: List[Dict], category: Optional[str] = None) -> Optional[Dict]:
    pool = [x for x in items if not x.get("done") and str(x.get("text", "")).strip()]
    if category and category != "すべて":
        pool = [x for x in pool if x.get("category") == category]
    if not pool:
        return None
    return random.choice(pool)


def find_by_id(items: List[Dict], item_id: str) -> Optional[Dict]:
    for x in items:
        if x.get("id") == item_id:
            return x
    return None


# --------------------
# UI
# --------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🎯 今日の1個抽選（Want100連動）")
st.caption("迷いを消す。今日の行動を1つに絞る。")

wants_path = detect_wants_path()
items = load_items(wants_path)

done_count = sum(1 for x in items if x.get("done"))
todo_count = sum(1 for x in items if not x.get("done") and str(x.get("text", "")).strip())

st.info(f"参照ファイル：{wants_path}")

c1, c2, c3 = st.columns(3)
c1.metric("達成数", str(done_count))
c2.metric("未達成", str(todo_count))
c3.metric("総数", str(len(items)))

st.divider()

# フィルタ
colA, colB = st.columns([2, 1])
with colA:
    category = st.selectbox("カテゴリで絞る（任意）", ["すべて"] + CATEGORIES)
with colB:
    hard_mode = st.toggle("ちょい本気モード", value=False, help="選ばれた後に“次の一手”を1行書く")

# 抽選
if "picked_id" not in st.session_state:
    st.session_state["picked_id"] = None

if st.button("🎲 今日の1個を決める", use_container_width=True):
    picked = pick_one(items, category=category)
    st.session_state["picked_id"] = picked["id"] if picked else None

picked_item = find_by_id(items, st.session_state["picked_id"]) if st.session_state["picked_id"] else None

if picked_item is None:
    st.warning("まだ選ばれてないよ。ボタンで抽選してね。")
    if todo_count == 0 and len(items) > 0:
        st.success("すべて達成済み！…やばい、強すぎる。")
    elif len(items) == 0:
        st.error("Want100のデータが空みたい。先にDay51で登録してね。")
else:
    st.subheader("🎯 今日の1個")
    st.write(f"**{picked_item.get('text','')}**")
    st.caption(f"カテゴリ：{picked_item.get('category','')}")

    st.divider()

    if hard_mode:
        st.markdown("### ✍️ 次の一手（10秒でOK）")
        next_step = st.text_input(
            "今すぐできる最小の一歩",
            placeholder="例：検索する／メモする／予約画面を開く／1分だけ触る",
            key="next_step_input",
        )
        st.caption("書けたら、それだけで前進。")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ やった！達成にする", use_container_width=True):
            # 更新
            target = find_by_id(items, picked_item["id"])
            if target:
                target["done"] = True
                target["done_at"] = dt.datetime.now().isoformat(timespec="seconds")
                save_items(wants_path, items)

                new_done_count = sum(1 for x in items if x.get("done"))
                st.balloons()
                st.success(celebrate_message(new_done_count))

                # 次を選べるように
                st.session_state["picked_id"] = None
                st.rerun()
            else:
                st.error("対象が見つからなかった（データが変更された可能性）")

    with col2:
        if st.button("🔁 別の1個にする", use_container_width=True):
            picked = pick_one(items, category=category)
            st.session_state["picked_id"] = picked["id"] if picked else None
            st.rerun()

st.divider()

with st.expander("🔍 未達成の一覧（確認用）"):
    # 未達成だけ、カテゴリ→文字で軽く表示
    pending = [x for x in items if not x.get("done") and str(x.get("text", "")).strip()]
    if category != "すべて":
        pending = [x for x in pending if x.get("category") == category]

    if not pending:
        st.write("未達成はありません。")
    else:
        for x in pending[:200]:
            st.write(f"・{x.get('text','')}  ({x.get('category','')})")
        if len(pending) > 200:
            st.caption("※表示は200件まで")
