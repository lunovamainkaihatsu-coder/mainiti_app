# app.py
from __future__ import annotations

import datetime as dt
import json
import uuid
from pathlib import Path
from typing import Dict, List

import streamlit as st

APP_TITLE = "したいこと100（Day51）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "wants.json"

CATEGORIES = ["仕事", "お金", "家族", "体験", "自由", "健康", "その他"]
MAX_ITEMS = 100

# --------------------
# utils
# --------------------
def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_items() -> List[Dict]:
    raw = _read_json(DATA_PATH, {"items": []})
    items = raw.get("items", [])
    if isinstance(items, list):
        # 最低限の正規化
        out = []
        for it in items:
            if not isinstance(it, dict):
                continue
            it.setdefault("id", str(uuid.uuid4()))
            it.setdefault("text", "")
            it.setdefault("category", "その他")
            it.setdefault("done", False)
            it.setdefault("done_at", None)
            it.setdefault("created_at", dt.datetime.now().isoformat(timespec="seconds"))
            out.append(it)
        return out
    return []


def save_items(items: List[Dict]):
    _write_json(DATA_PATH, {"items": items})


def celebrate_message(done_count: int) -> str:
    if done_count == 1:
        return "🎉 はじめの一歩！現実が動き始めた。"
    if done_count == 10:
        return "🎊 10個達成！意識が完全に現実へ向いてる。"
    if done_count == 50:
        return "🏆 50個達成！ここまで来たのは本物。"
    if done_count >= 100:
        return "🌈 100個達成！あなたは現実をデザインした。"
    return "✨ おめでとう。これはあなたが動かした現実。"


# --------------------
# UI
# --------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("思ったことを、忘れない。忘れないから、現実になる。")

items = load_items()

done_count = sum(1 for x in items if x.get("done"))
remaining_slots = MAX_ITEMS - len(items)

# ---- header stats
c1, c2, c3 = st.columns(3)
c1.metric("達成", f"{done_count} / {MAX_ITEMS}")
c2.metric("残り登録枠", f"{max(remaining_slots, 0)}")
c3.metric("未達成", f"{sum(1 for x in items if not x.get('done'))}")

st.divider()

# ---- add new item
with st.expander("➕ やりたいことを追加", expanded=True):
    colA, colB = st.columns([3, 1])
    with colA:
        text = st.text_input("やりたいこと", placeholder="例：アプリで月1万円稼ぐ")
    with colB:
        category = st.selectbox("カテゴリ", CATEGORIES)

    if st.button("追加する", use_container_width=True):
        if not text.strip():
            st.error("内容を入れてね")
        elif len(items) >= MAX_ITEMS:
            st.error("100個に到達しています（これ以上は追加できません）")
        else:
            items.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": text.strip(),
                    "category": category,
                    "done": False,
                    "done_at": None,
                    "created_at": dt.datetime.now().isoformat(timespec="seconds"),
                }
            )
            save_items(items)
            st.success("追加したよ。意識に刻まれた。")
            st.rerun()

st.divider()

# ---- tabs by category
tabs = st.tabs(CATEGORIES + ["すべて"])

tab_map: Dict[str, List[Dict]] = {name: [] for name in CATEGORIES}
for it in items:
    cat = it.get("category") or "その他"
    if cat not in tab_map:
        cat = "その他"
    tab_map[cat].append(it)


def render_list(list_items: List[Dict], key_prefix: str):
    """タブごとにキーを一意化して DuplicateElementKey を回避する"""
    for it in list_items:
        cols = st.columns([0.08, 0.72, 0.2])

        chk_key = f"{key_prefix}_chk_{it['id']}"  # ★ここが重要

        with cols[0]:
            checked = st.checkbox(
                "",
                value=bool(it.get("done", False)),
                key=chk_key,
            )

        with cols[1]:
            st.write(it.get("text", ""))
            st.caption(it.get("category", ""))

        with cols[2]:
            if it.get("done_at"):
                st.caption(f"達成日：{str(it['done_at'])[:10]}")

        # update
        if checked != bool(it.get("done", False)):
            it["done"] = checked
            it["done_at"] = dt.datetime.now().isoformat(timespec="seconds") if checked else None
            save_items(items)

            if checked:
                new_done_count = sum(1 for x in items if x.get("done"))
                st.success(celebrate_message(new_done_count))

            st.rerun()


for i, name in enumerate(CATEGORIES):
    with tabs[i]:
        render_list(tab_map[name], key_prefix=f"tab_{name}")

with tabs[-1]:
    render_list(items, key_prefix="tab_all")

st.divider()

with st.expander("⚙️ 管理"):
    st.caption(f"保存先: {DATA_PATH}")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧨 全削除（注意）", type="primary", use_container_width=True):
            save_items([])
            st.success("全削除しました")
            st.rerun()

    with col2:
        if st.button("📥 JSONを表示", use_container_width=True):
            st.json({"items": items})
