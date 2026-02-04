from __future__ import annotations

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, date

APP_TITLE = "🌿 週のふりかえりAI（Day71）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SAVE_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これは自己肯定感を高めるための振り返りツールです。できなかったことは数えません。"


# -------------------------
# 保存系
# -------------------------
def load_data():
    if not SAVE_PATH.exists():
        return []
    try:
        return json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    except:
        return []

def save_data(data):
    SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# -------------------------
# ルナの一言
# -------------------------
LUNA_LINES = [
    "ほら、ちゃんと進んでる。",
    "ゼロじゃない。それが一番すごい。",
    "積み重ねは、もう始まってるよ。",
    "今週のあなた、ほんとにえらい。",
    "できた数だけ、未来は軽くなる。",
]


def week_id():
    y, w, _ = date.today().isocalendar()
    return f"{y}-W{w:02d}"


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🌿 週のふりかえりAI")
st.caption("『できたこと』だけ数えよう。できなかったことは無視でOK。")
st.info(DISCLAIMER)

data = load_data()

wid = week_id()
st.markdown(f"### 🗓 今週：{wid}")

st.divider()

st.subheader("✅ 今週できたこと（いくつでも）")

items = []
for i in range(5):
    items.append(st.text_input(f"{i+1}.", key=f"item{i}"))

extra = st.text_area("その他まとめて（任意）")

st.divider()

if st.button("ふりかえる", use_container_width=True):

    done_list = [x for x in items if x.strip()]
    count = len(done_list)

    if extra.strip():
        count += 1

    line = LUNA_LINES[count % len(LUNA_LINES)]

    st.subheader("📊 結果")
    st.markdown(f"### 🌟 できた数： **{count}**")

    for d in done_list:
        st.markdown(f"・{d}")

    if extra.strip():
        st.markdown(f"・{extra}")

    st.markdown(f"\n🌙 **ルナ：{line}**")

    copy_text = f"今週の成果：{count}個\n" + "\n".join(done_list)
    st.text_area("コピペ用", copy_text, height=150)

    if st.button("💾 保存"):
        data.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "week": wid,
            "count": count,
            "items": done_list,
            "extra": extra
        })
        save_data(data)
        st.success("保存しました")

st.divider()

with st.expander("🗂 過去ログ"):
    if not data:
        st.write("まだ記録がありません")
    else:
        for row in reversed(data[-10:]):
            st.markdown(f"**{row['time']}｜{row['week']}｜{row['count']}個**")
            for i in row["items"]:
                st.caption(i)
            st.write("---")
