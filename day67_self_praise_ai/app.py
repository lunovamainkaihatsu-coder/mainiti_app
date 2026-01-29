from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_TITLE = "🌸 自分を褒めるAI（Day67）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これは自己肯定感を高めるための言葉の提案です。医療行為ではありません。"


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
# 褒めテンプレ
# -------------------------
OPENERS = [
    "今日のあなた、ちゃんとやってる。",
    "まず言わせて。えらい。",
    "その一歩、ほんとに価値ある。",
    "見えないところで頑張ってるの、知ってる。",
    "今日を生きた時点で勝ちだよ。",
]

FOCUS = {
    "小さな行動": [
        "動けたこと自体がすごい。",
        "ゼロから1にしたのが一番難しいんだよ。",
        "“少しだけ”が積み重なる人が強い。",
    ],
    "我慢した/耐えた": [
        "踏ん張ったの、偉すぎる。",
        "崩れそうでも立て直したのが強い。",
        "逃げずに受け止めた分、成長してる。",
    ],
    "挑戦した": [
        "怖くてもやったのが最高。",
        "未知に踏み込める人は伸びる。",
        "挑戦は才能。行動は証拠。",
    ],
    "人に優しくした": [
        "優しさを選べるのは本物の強さ。",
        "相手を思えた自分、誇っていい。",
        "それ、ちゃんと世界を良くしてる。",
    ],
    "体を守った": [
        "休む判断ができたのが偉い。",
        "回復は前進。体を守るのは才能。",
        "無理しなかったあなたは賢い。",
    ],
}

CLOSERS = [
    "今日はこれで十分。ちゃんと進んでる。",
    "明日はまた明日。今日はあなたをねぎらおう。",
    "この積み上げは、必ず未来に効く。",
    "“できた”を数えていこう。あなたは伸びてる。",
    "自分を味方にできる人が、いちばん強い。",
]

SMALL_REWARD = [
    "温かい飲み物を一杯。",
    "ストレッチ30秒。",
    "好きな音楽を1曲だけ。",
    "スマホを裏返して3分だけ休む。",
    "深呼吸を5回。",
]


def praise(text: str, focus_key: str) -> dict:
    opener = random.choice(OPENERS)
    mid = random.choice(FOCUS[focus_key])
    closer = random.choice(CLOSERS)
    reward = random.choice(SMALL_REWARD)

    # 入力を“褒めに変換”する軽い演出
    cleaned = text.strip()
    if not cleaned:
        cleaned = "うまく言えないけど、今日を生きた"

    mirror = random.choice([
        f"あなたがやったこと：『{cleaned}』",
        f"今日の記録：『{cleaned}』",
        f"今日のあなた：『{cleaned}』",
    ])

    return {
        "mirror": mirror,
        "message": f"{opener}\n\n{mid}\n\n{closer}",
        "reward": f"🍬 ご褒美提案：{reward}",
    }


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🌸 自分を褒めるAI")
st.caption("今日できたことを1つ書いて。ルナがやさしく褒めるよ。")
st.info(DISCLAIMER)

history = load_history()

st.divider()

focus_key = st.selectbox("褒めポイント（選ぶだけ）", list(FOCUS.keys()))
text = st.text_area("今日できたこと（1つでOK）", height=90, placeholder="例：アプリを少し進めた／娘の相手をした／休む判断をした…")

st.divider()

if st.button("褒めて", use_container_width=True):
    r = praise(text, focus_key)
    st.session_state["result"] = r

if "result" in st.session_state:
    r = st.session_state["result"]
    st.subheader("🫶 ルナから")
    st.markdown(f"**{r['mirror']}**")
    st.markdown(r["message"])
    st.markdown(r["reward"])

    st.text_area(
        "コピペ用（Markdown）",
        f"{r['mirror']}\n\n{r['message']}\n\n{r['reward']}",
        height=220
    )

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "focus": focus_key,
                "text": text.strip(),
                "mirror": r["mirror"],
                "message": r["message"],
                "reward": r["reward"],
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
            st.markdown(f"**{row['time']}｜{row['focus']}**")
            if row.get("text"):
                st.caption(f"入力：{row['text']}")
            st.markdown(row["mirror"])
            st.markdown(row["message"])
            st.markdown(row["reward"])
            st.write("---")
