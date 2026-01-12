from streamlit_autorefresh import st_autorefresh

import json
import time
import datetime as dt
from pathlib import Path

import streamlit as st

APP_TITLE = "朝活スイッチ15分（Day53）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOG_PATH = DATA_DIR / "log.json"

MODES = {
    "🧠 学習": "知識は未来の自由を増やす。",
    "💪 体": "体を動かすと、心も起きる。",
    "🧹 整理": "環境が整うと、思考も整う。",
}

TIMES = [5, 10, 15, 25]


# --------------------
# utils
# --------------------
def load_log():
    if not LOG_PATH.exists():
        return []
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_log(logs):
    LOG_PATH.write_text(
        json.dumps(logs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def calc_streak(logs):
    """連続日数を計算（途切れても責めない仕様）"""
    if not logs:
        return 0

    days = sorted({x["date"] for x in logs})
    streak = 1
    for i in range(len(days) - 1, 0, -1):
        d1 = dt.date.fromisoformat(days[i])
        d0 = dt.date.fromisoformat(days[i - 1])
        if (d1 - d0).days == 1:
            streak += 1
        else:
            break
    return streak


# --------------------
# UI
# --------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("☀️ 朝活スイッチ 15分")
st.caption("考えなくていい。始めるだけでいい。")

logs = load_log()
today = dt.date.today().isoformat()

st.divider()

# --- 選択 ---
mode = st.radio("今日の朝活は？", list(MODES.keys()), horizontal=True)
minutes = st.select_slider("時間（分）", options=TIMES, value=15)

st.info(MODES[mode])

st.divider()

# --- タイマー ---
if "running" not in st.session_state:
    st.session_state.running = False
if "end_time" not in st.session_state:
    st.session_state.end_time = None

def start_timer():
    st.session_state.running = True
    st.session_state.end_time = time.time() + minutes * 60

def stop_timer():
    st.session_state.running = False
    st.session_state.end_time = None

if not st.session_state.running:
    st.button("▶ 朝活スタート", use_container_width=True, on_click=start_timer)
else:
    remaining = int(st.session_state.end_time - time.time())

    # ★1秒ごとに自動で再描画（タイマーが動く）
    st_autorefresh(interval=1000, key="timer_refresh")

    if remaining <= 0:
        stop_timer()
        st.balloons()
        st.success("🎉 完了！朝活、やりきった。")
    else:
        m = remaining // 60
        s = remaining % 60
        # ★「分:秒」で表示（15時間に見えない）
        st.metric("残り時間", f"{m}分{s}秒")
        st.button("⏹ 中断", use_container_width=True, on_click=stop_timer)

st.divider()

# --- ログ ---
st.subheader("✍️ ひとことログ（任意）")
memo = st.text_input("今日やったことを一言", placeholder="例：公式を1ページ読んだ")

if st.button("💾 今日を記録する", use_container_width=True):
    logs.append(
        {
            "date": today,
            "mode": mode,
            "minutes": minutes,
            "memo": memo.strip(),
            "saved_at": dt.datetime.now().isoformat(timespec="seconds"),
        }
    )
    save_log(logs)
    st.success("記録したよ。積み上がってる。")
    st.rerun()

st.divider()

# --- ステータス ---
st.subheader("📊 朝活ステータス")
streak = calc_streak(logs)
total = len(logs)

c1, c2 = st.columns(2)
c1.metric("連続日数", f"{streak} 日")
c2.metric("累計回数", f"{total} 回")

if streak >= 7:
    st.success("🌈 1週間継続！もう習慣だ。")
elif streak >= 3:
    st.info("🔥 いい流れ。身体が覚え始めてる。")
elif streak == 1:
    st.info("✨ 初日クリア。これで十分。")

st.divider()

with st.expander("📖 過去ログ"):
    if not logs:
        st.write("まだ記録がないよ。")
    else:
        for x in reversed(logs[-30:]):
            st.write(
                f"- {x['date']}｜{x['mode']}｜{x['minutes']}分｜{x.get('memo','')}"
            )
