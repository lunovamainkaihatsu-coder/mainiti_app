from __future__ import annotations

import json
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_TITLE = "🩸 呪われたUI（Day64）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOG_PATH = DATA_DIR / "logs.json"

DISCLAIMER = "※これは演出アプリです。霊的断定・予言・危険行為の誘導はありません。怖い人はすぐ閉じてOK。"


# -------------------------
# 保存/読込
# -------------------------
def load_logs():
    if not LOG_PATH.exists():
        return []
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_logs(rows):
    LOG_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


# -------------------------
# 呪い演出：文字のグリッチ
# -------------------------
COMBINING = ["\u0336", "\u0335", "\u0334", "\u0333", "\u0332", "\u0301", "\u0300", "\u0308", "\u0307", "\u034F"]
GLITCH_CHARS = list("█▓▒░@#%&$!?")

def glitch_text(text: str, intensity: int) -> str:
    """intensity: 0..10"""
    if intensity <= 0:
        return text
    out = []
    for ch in text:
        # 文字を壊す確率
        if ch.strip() and random.random() < (0.03 * intensity):
            out.append(random.choice(GLITCH_CHARS))
        else:
            out.append(ch)

        # 合成文字を載せる
        if ch.strip() and random.random() < (0.06 * intensity):
            out.append(random.choice(COMBINING))
            if random.random() < 0.5:
                out.append(random.choice(COMBINING))
    return "".join(out)


def creepy_whisper(intensity: int) -> str:
    base = [
        "……きこえる？",
        "うしろ、じゃない。",
        "みてるのは、あなた。",
        "今の“間”は、見逃さない。",
        "閉じても、残る。",
        "大丈夫。まだ、やさしいほう。",
        "そのボタンは、押さないほうがいい。",
    ]
    line = random.choice(base)
    return glitch_text(line, intensity)


def cursed_seed() -> int:
    # セッション内で固定っぽく見せる演出（でも完全固定じゃない）
    if "curse_seed" not in st.session_state:
        st.session_state["curse_seed"] = random.randint(1000, 9999)
    return st.session_state["curse_seed"]


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🩸 呪われたUI（演出）")
st.caption("操作しにくい。読みにくい。たまに、変なことが起きる。※ただの演出です。")
st.info(DISCLAIMER)

seed = cursed_seed()

# 強度
colA, colB = st.columns([2, 1])
with colA:
    intensity = st.slider("呪い強度", 0, 10, 6)
with colB:
    safe_mode = st.toggle("セーフモード（弱め）", value=False)

if safe_mode:
    intensity = max(0, intensity - 3)

# “揺れ”演出のCSS（強度に応じて揺れ幅が変わる）
shake_px = 1 + intensity  # 1..11
blur = 0.0 if intensity < 7 else 0.3  # 強すぎると読めないので控えめ
opacity = 1.0 if intensity < 9 else 0.95

st.markdown(
    f"""
    <style>
    @keyframes shake {{
      0% {{ transform: translate(0px, 0px); }}
      20% {{ transform: translate({shake_px}px, -{shake_px}px); }}
      40% {{ transform: translate(-{shake_px}px, {shake_px}px); }}
      60% {{ transform: translate({shake_px}px, {shake_px}px); }}
      80% {{ transform: translate(-{shake_px}px, -{shake_px}px); }}
      100% {{ transform: translate(0px, 0px); }}
    }}

    /* タイトルっぽい部分を揺らす */
    .cursed {{
      animation: shake {max(0.6, 1.5 - intensity*0.06)}s infinite;
      filter: blur({blur}px);
      opacity: {opacity};
      text-shadow: 0 0 {min(12, 2+intensity)}px rgba(255,255,255,0.12);
    }}

    /* ボタンを微妙にズラす（押しにくい） */
    div.stButton > button {{
      position: relative;
      left: {random.randint(-intensity, intensity)}px;
      top: {random.randint(-intensity, intensity)}px;
      transform: rotate({random.randint(-intensity, intensity)*0.15}deg);
    }}

    /* たまにカーソルが変になる…っぽい演出（実害なし） */
    .cursed-area {{
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.12);
      padding: 12px 14px;
      background: rgba(255,255,255,0.03);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.divider()

# メイン表示
msg = f"CURSE ID: {seed}"
st.markdown(f"<div class='cursed-area'><div class='cursed'><b>{glitch_text(msg, intensity)}</b></div></div>", unsafe_allow_html=True)

st.write("")

user_text = st.text_input("入力してみて（任意）", placeholder="例：おーぷん、やめたい、こわい、だいじょうぶ…")
if not user_text.strip():
    user_text = "……"

# “壊れたプレビュー”
preview = glitch_text(user_text, intensity)
st.markdown(f"**プレビュー：** {preview}")

st.write("")

# 不気味ボタン（押すと何か起きた“気がする”）
left, right = st.columns(2)

with left:
    if st.button("押してはいけない", use_container_width=True):
        # ちょっと待たせて恐怖演出（短い）
        with st.spinner(glitch_text("……反応しています", intensity)):
            time.sleep(0.6 if intensity < 7 else 0.9)

        whisper = creepy_whisper(intensity)

        # たまに“画面が乱れた感”を出す
        if random.random() < 0.15 + intensity * 0.03:
            st.warning(glitch_text("通信が不安定です。", intensity))

        st.session_state["last_whisper"] = whisper

        # ログ保存
        logs = load_logs()
        logs.append({
            "at": datetime.now().isoformat(timespec="seconds"),
            "seed": seed,
            "intensity": intensity,
            "text": user_text,
            "whisper": whisper,
        })
        save_logs(logs)

with right:
    # “浄化”ボタン：呪い強度を下げる気分になれる
    if st.button("浄化する", use_container_width=True):
        st.session_state["last_whisper"] = glitch_text("……だいじょうぶ。ここは安全。", max(0, intensity-5))
        st.success("気配が薄れた。")

# 結果表示
if "last_whisper" in st.session_state:
    st.subheader("🕯 反応")
    st.markdown(f"<div class='cursed-area'><div class='cursed'>{st.session_state['last_whisper']}</div></div>", unsafe_allow_html=True)

    st.caption("※演出です。怖かったら“浄化する”か、タブを閉じてOK。")

st.divider()

# 履歴
with st.expander("🗂 ログ（最新10件）"):
    logs = load_logs()
    if not logs:
        st.write("まだログはないよ。")
    else:
        for row in reversed(logs[-10:]):
            st.markdown(f"**{row['at']}｜CURSE {row['seed']}｜強度 {row['intensity']}**")
            st.caption(f"入力：{row.get('text','')}")
            st.markdown(f"反応：{row.get('whisper','')}")
            st.write("---")

st.caption(glitch_text("……おやすみ。", intensity if intensity >= 5 else 0))
