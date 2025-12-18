import time
import random
import streamlit as st

st.set_page_config(page_title="勉強ここまでタイマー", page_icon="⏱️", layout="centered")

# -----------------------------
# セッション状態 初期化
# -----------------------------
if "running" not in st.session_state:
    st.session_state.running = False
if "end_ts" not in st.session_state:
    st.session_state.end_ts = None
if "duration_sec" not in st.session_state:
    st.session_state.duration_sec = 0
if "last_done_msg" not in st.session_state:
    st.session_state.last_done_msg = ""

DONE_MESSAGES = [
    "今日はここまで。止まれたのは判断力。",
    "集中できなくてもOK。向き合った時間は残った。",
    "途中でも大丈夫。悪化しなかった、それが勝ち。",
    "“やった感”じゃなく“やった事実”。区切り完了。",
    "今日は生存優先でOK。ここまでで十分。",
]

st.title("⏱️ 勉強ここまでタイマー")
st.caption("ページ数じゃなく、時間で区切る。集中できなくてもOK。")

# -----------------------------
# 設定UI（動作中は触らせない）
# -----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    minutes = st.radio(
        "時間を選ぶ",
        options=[5, 10, 15, 25],
        horizontal=True,
        disabled=st.session_state.running,
    )

with col2:
    st.write("")
    st.write("")
    if not st.session_state.running:
        if st.button("▶ 開始", use_container_width=True):
            st.session_state.running = True
            st.session_state.duration_sec = int(minutes) * 60
            st.session_state.end_ts = time.time() + st.session_state.duration_sec
            st.session_state.last_done_msg = ""
            st.rerun()
    else:
        if st.button("■ 中断（今日はここまで）", use_container_width=True):
            st.session_state.running = False
            st.session_state.end_ts = None
            st.session_state.last_done_msg = random.choice(DONE_MESSAGES)
            st.rerun()

st.divider()

# -----------------------------
# タイマー表示
# -----------------------------
placeholder = st.empty()

def fmt_mmss(sec: int) -> str:
    m = sec // 60
    s = sec % 60
    return f"{m:02d}:{s:02d}"

if st.session_state.running and st.session_state.end_ts is not None:
    remaining = int(st.session_state.end_ts - time.time())

    if remaining <= 0:
        st.session_state.running = False
        st.session_state.end_ts = None
        st.session_state.last_done_msg = random.choice(DONE_MESSAGES)
        st.balloons()  # 静か版なら消してOK
        st.rerun()
    else:
        placeholder.markdown(
            f"""
            <div style="text-align:center; padding: 24px;">
              <div style="font-size: 56px; font-weight: 800;">{fmt_mmss(remaining)}</div>
              <div style="margin-top: 10px; font-size: 14px; opacity: 0.8;">
                今は、やる気を出す時間じゃない。<br/>
                ただ、そこにいる時間。
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # 1秒更新（Streamlitの定番）
        time.sleep(1)
        st.rerun()
else:
    placeholder.markdown(
        """
        <div style="text-align:center; padding: 24px;">
          <div style="font-size: 20px; font-weight: 700;">準備できたら「開始」</div>
          <div style="margin-top: 10px; font-size: 14px; opacity: 0.8;">
            今日は短くてOK。5分でも勝ち。
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# 終了メッセージ
# -----------------------------
if st.session_state.last_done_msg:
    st.success(st.session_state.last_done_msg)
    st.caption("次に進めなくてもOK。ここまで区切れた。")
