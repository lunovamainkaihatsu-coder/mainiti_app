from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_TITLE = "🌙 夜の3分整え（Day68）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これは一般的なセルフケア提案です。つらさが強い場合は休息や相談も大切です。"


# -------------------------
# 保存/読込
# -------------------------
def load_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(rows):
    HISTORY_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


# -------------------------
# 夜の整え：チェック項目
# -------------------------
CHECKS = [
    ("🫧 水分", "水をひと口でも飲めた"),
    ("🧼 体", "顔を洗った／歯を磨いた／シャワーした"),
    ("🧠 頭", "明日の不安を“1行”にして外に出した"),
    ("📱 情報", "スマホを一度置けた（1分でもOK）"),
    ("🫶 自分", "今日の自分に『おつかれ』と言えた"),
]

WHISPERS = [
    "今日は、ここまでで十分。",
    "整えるだけで、明日は違う。",
    "眠ることは、最大の回復。",
    "あなたは今日もよく耐えた。",
    "大丈夫。ちゃんと積み上がってる。",
]

SUGGESTIONS_LOW = [
    "布団に入るだけで勝ち。スマホは裏返してOK。",
    "温かい飲み物を3口だけ。",
    "呼吸：4秒吸って6秒吐く×5回だけ。",
    "明日のことは、明日の自分に渡していい。",
]

SUGGESTIONS_OK = [
    "最後に部屋のライトを少し落として、体を“夜モード”にしよう。",
    "明日の最小タスクを1つだけ書いて、終わり。",
    "首・肩を30秒ゆっくり回して、力を抜こう。",
    "『今日できたこと』を1つ思い出して寝よう。",
]


def build_result(done_count: int, notes: str) -> dict:
    whisper = random.choice(WHISPERS)
    if done_count <= 1:
        tip = random.choice(SUGGESTIONS_LOW)
        mood = "🕯 今日は“守る日”"
    elif done_count <= 3:
        tip = random.choice(SUGGESTIONS_OK)
        mood = "🌙 ちょい整い"
    else:
        tip = random.choice(SUGGESTIONS_OK)
        mood = "🌟 かなり整ってる"

    note_line = f"メモ：『{notes.strip()}』\n" if notes.strip() else ""
    return {
        "mood": mood,
        "whisper": whisper,
        "tip": tip,
        "note_line": note_line,
    }


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🌙 夜の3分整え")
st.caption("寝る前に“整えた”を数えるだけ。ルナがそっと締めるよ。")
st.info(DISCLAIMER)

history = load_history()

st.divider()

st.subheader("✅ 今日の整えチェック（できた分だけ）")
checked = []
for key, label in CHECKS:
    checked.append(st.checkbox(f"{key}  {label}"))

notes = st.text_area("今日のひとこと（任意）", height=80, placeholder="例：しんどかったけど進んだ／不安がある／今日は守れた…")

st.divider()

if st.button("整え完了", use_container_width=True):
    done_count = sum(1 for x in checked if x)
    r = build_result(done_count, notes)
    st.session_state["result"] = (done_count, r)

if "result" in st.session_state:
    done_count, r = st.session_state["result"]

    st.subheader("🧾 今日の結果")
    st.markdown(f"**整えスコア：{done_count} / {len(CHECKS)}**")
    st.markdown(f"**{r['mood']}**")
    if r["note_line"]:
        st.caption(r["note_line"])
    st.markdown(f"🌙 **ひとこと**：{r['whisper']}")
    st.markdown(f"🧩 **次の一手**：{r['tip']}")

    copy_text = (
        f"整えスコア：{done_count}/{len(CHECKS)}\n"
        f"{r['mood']}\n\n"
        f"{r['note_line']}"
        f"ひとこと：{r['whisper']}\n"
        f"次の一手：{r['tip']}"
    )
    st.text_area("コピペ用", copy_text, height=170)

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "done_count": done_count,
                "checked": checked,
                "notes": notes.strip(),
                "mood": r["mood"],
                "whisper": r["whisper"],
                "tip": r["tip"],
            })
            save_history(history)
            st.success("保存したよ。")
    with cB:
        if st.button("🧹 クリア", use_container_width=True):
            st.session_state.pop("result", None)
            st.rerun()

st.divider()

with st.expander("🗂 履歴（最新10件）"):
    if not history:
        st.write("まだ履歴がないよ。")
    else:
        for row in reversed(history[-10:]):
            st.markdown(f"**{row['time']}｜スコア {row['done_count']}/{len(CHECKS)}｜{row['mood']}**")
            if row.get("notes"):
                st.caption(f"メモ：{row['notes']}")
            st.caption(f"ひとこと：{row['whisper']}")
            st.caption(f"次の一手：{row['tip']}")
            st.write("---")
