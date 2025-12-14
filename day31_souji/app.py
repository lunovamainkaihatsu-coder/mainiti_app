import streamlit as st
import random
from datetime import date

# ----------------------------
# ページ設定
# ----------------------------
st.set_page_config(page_title="年末おそうじチェック", page_icon="🧹", layout="centered")

st.title("🧹 年末おそうじチェック")
st.caption("できた分だけチェック。全部やらなくてOK。今日は“少し”で勝ち。")

# ----------------------------
# 初期データ
# ----------------------------
DEFAULT_TASKS = {
    "🏠 リビング": [
        "床を少し拭いた",
        "テーブルの上を片付けた",
        "ゴミをまとめた",
        "ソファ周りを整えた",
    ],
    "🍳 キッチン": [
        "シンクを流した",
        "コンロ周りを拭いた",
        "排水口をさっと掃除",
        "冷蔵庫の中を1段だけ整理",
    ],
    "🛁 水回り": [
        "洗面台を拭いた",
        "トイレをさっと掃除",
        "お風呂の排水口を流した",
        "鏡をひと拭き",
    ],
    "🧺 玄関・その他": [
        "玄関をさっと掃く",
        "靴をそろえる",
        "いらない紙を捨てる",
        "洗濯物をたたむ（or まとめる）",
    ],
}

CHEER_MESSAGES = {
    "low": [
        "今日は体を守った。それだけで十分えらい。",
        "ふわっとしてる日は“ゼロ”でもOK。休むのが仕事。",
        "進まない日も、止まってるんじゃなく整えてる。",
    ],
    "mid": [
        "十分！ちゃんと前に進んでる。",
        "その“少し”が一番強い。積み上げは勝ち。",
        "よし、今日の分はクリア。あとはやさしく過ごそう。",
    ],
    "high": [
        "年末の神が微笑んでる✨",
        "やったね。部屋が整うと心も整う。",
        "めちゃくちゃ前進！今日は胸張っていい日。",
    ],
}

# ----------------------------
# セッション初期化
# ----------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = DEFAULT_TASKS

if "done" not in st.session_state:
    # 各タスクの完了状態を保持する dict
    st.session_state.done = {}  # key -> bool

if "custom_tasks" not in st.session_state:
    st.session_state.custom_tasks = []  # 追加タスク（文字列）

# 今日の日付（表示用）
today_str = date.today().strftime("%Y-%m-%d")
st.write(f"📅 今日：**{today_str}**")

st.divider()

# ----------------------------
# 追加タスク入力
# ----------------------------
with st.expander("➕ 自分のタスクを追加（任意）", expanded=False):
    new_task = st.text_input("追加したい掃除（例：窓をひと拭き）", value="")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("追加する", use_container_width=True):
            t = new_task.strip()
            if t:
                st.session_state.custom_tasks.append(t)
                st.success(f"追加したよ：{t}")
            else:
                st.warning("文字を入力してね")
    with col_b:
        if st.button("追加タスクを全消し", use_container_width=True):
            st.session_state.custom_tasks = []
            st.info("追加タスクを消したよ")

# ----------------------------
# チェックリスト表示
# ----------------------------
st.subheader("✅ チェックリスト")

total = 0
done_count = 0

for section, items in st.session_state.tasks.items():
    st.markdown(f"### {section}")
    for item in items:
        key = f"{section}::{item}"
        # 初期値
        if key not in st.session_state.done:
            st.session_state.done[key] = False

        checked = st.checkbox(item, value=st.session_state.done[key], key=key)
        st.session_state.done[key] = checked

        total += 1
        if checked:
            done_count += 1

# 追加タスク
if st.session_state.custom_tasks:
    st.markdown("### ✍️ 追加タスク")
    for i, item in enumerate(st.session_state.custom_tasks, start=1):
        key = f"custom::{i}::{item}"
        if key not in st.session_state.done:
            st.session_state.done[key] = False

        checked = st.checkbox(item, value=st.session_state.done[key], key=key)
        st.session_state.done[key] = checked

        total += 1
        if checked:
            done_count += 1

st.divider()

# ----------------------------
# 進捗表示
# ----------------------------
if total == 0:
    progress = 0.0
else:
    progress = done_count / total

st.write(f"🧮 進捗：**{done_count} / {total}**")
st.progress(progress)

# ----------------------------
# 判定 & メッセージ
# ----------------------------
def pick_message(done: int) -> str:
    if done <= 1:
        bucket = "low"
    elif done <= 4:
        bucket = "mid"
    else:
        bucket = "high"
    return random.choice(CHEER_MESSAGES[bucket])

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🧹 今日はここまででOK", use_container_width=True):
        st.success(pick_message(done_count))

with col2:
    if st.button("🔄 今日のチェックをリセット", use_container_width=True):
        # チェックだけ消す（タスク自体は残す）
        for k in list(st.session_state.done.keys()):
            st.session_state.done[k] = False
        st.toast("チェックをリセットしたよ", icon="✅")
        st.rerun()

st.caption("※チェック状態はブラウザ上に保存されます（同じ端末・同じセッション内）。")
