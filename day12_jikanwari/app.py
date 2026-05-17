import streamlit as st
from datetime import datetime, timedelta, time
import pandas as pd

st.set_page_config(page_title="今日の時間割メーカー", page_icon="⏰", layout="centered")

# セッション初期化
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("⏰ 今日の時間割メーカー")
st.write("今日やりたいことを入力して、時間内でのベストな時間割を自動で作るアプリだよ。")

st.sidebar.header("メニュー")
if st.sidebar.button("🧹 ぜんぶリセット"):
    st.session_state.tasks = []
    st.sidebar.success("タスクをリセットしたよ！")

st.sidebar.markdown("---")
st.sidebar.caption("※時間割はその日のうち用。保存はしないシンプル仕様だよ。")


# --- タスク追加フォーム ---
st.subheader("1️⃣ やりたいことを追加")

with st.form("add_task_form"):
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        name = st.text_input("タスク名（例：Python勉強・Blender・Unityなど）", key="task_name")
    with c2:
        minutes = st.number_input("所要時間（分）", min_value=5, max_value=600, step=5, value=30, key="task_minutes")
    with c3:
        priority = st.selectbox("優先度", ["高", "中", "低"], key="task_priority")

    submitted = st.form_submit_button("➕ タスクを追加")
    if submitted:
        if name.strip():
            st.session_state.tasks.append(
                {
                    "name": name.strip(),
                    "minutes": int(minutes),
                    "priority": priority,
                }
            )
            st.success(f"「{name}」を追加したよ！")

        else:
            st.warning("タスク名を入れてね！")


# --- タスク一覧表示 ---
if st.session_state.tasks:
    st.subheader("📋 登録されているタスク")

    # DataFrame にして表示
    df_tasks = pd.DataFrame(st.session_state.tasks)
    df_tasks.index = df_tasks.index + 1
    df_tasks.columns = ["タスク名", "分数", "優先度"]
    st.table(df_tasks)
else:
    st.info("まだタスクがないよ。上のフォームから追加してね。")


# --- 時間設定 ---
st.subheader("2️⃣ 今日の時間帯を決める")

c4, c5 = st.columns(2)

with c4:
    start_time = st.time_input("開始時間", value=time(9, 0))
with c5:
    end_time = st.time_input("終了時間", value=time(23, 0))

if end_time <= start_time:
    st.error("終了時間は開始時間より後にしてね！")


# --- 時間割作成ロジック ---
st.subheader("3️⃣ 時間割を自動で作る")

make_schedule = st.button("🧮 時間割を作成")

def priority_key(p: str) -> int:
    mapping = {"高": 0, "中": 1, "低": 2}
    return mapping.get(p, 1)

if make_schedule:
    if not st.session_state.tasks:
        st.warning("まずはタスクを1つ以上追加してね。")
    elif end_time <= start_time:
        st.warning("開始時間と終了時間を正しく設定してね。")
    else:
        # 日付は今日で統一
        today = datetime.today().date()
        start_dt = datetime.combine(today, start_time)
        end_dt = datetime.combine(today, end_time)

        available_minutes = int((end_dt - start_dt).total_seconds() // 60)
        st.write(f"利用可能な時間：**{available_minutes} 分**")

        # 優先度順にソート
        sorted_tasks = sorted(st.session_state.tasks, key=lambda x: priority_key(x["priority"]))

        schedule_rows = []
        overflow_tasks = []

        current_dt = start_dt
        BREAK_MINUTES = 5

        for t in sorted_tasks:
            task_minutes = int(t["minutes"])
            task_end_dt = current_dt + timedelta(minutes=task_minutes)

            # 時間内に収まらないなら overflow
            if task_end_dt > end_dt:
                overflow_tasks.append(t)
                continue

            schedule_rows.append(
                {
                    "開始": current_dt.strftime("%H:%M"),
                    "終了": task_end_dt.strftime("%H:%M"),
                    "タスク名": t["name"],
                    "分数": task_minutes,
                    "優先度": t["priority"],
                }
            )

            # 次のタスクの開始時間（5分休憩込み）
            next_start = task_end_dt + timedelta(minutes=BREAK_MINUTES)
            if next_start >= end_dt:
                break
            current_dt = next_start

        if schedule_rows:
            st.success("時間割を作成したよ！")
            df_schedule = pd.DataFrame(schedule_rows)
            st.subheader("✅ 今日の時間割")
            st.dataframe(df_schedule, use_container_width=True)

            total_task_minutes = sum(row["分数"] for row in schedule_rows)
            st.write(f"- 実働時間：**{total_task_minutes} 分**")
            st.write(f"- 休憩（最大）：**{max(0, (len(schedule_rows) - 1) * BREAK_MINUTES)} 分**（タスク間 5分想定）")

        else:
            st.warning("時間内に入るタスクがなかったよ。タスクの分数か時間帯を見直してみてね。")

        if overflow_tasks:
            st.subheader("⏳ 時間内に入りきらなかったタスク")
            df_over = pd.DataFrame(overflow_tasks)
            df_over.index = df_over.index + 1
            df_over.columns = ["タスク名", "分数", "優先度"]
            st.table(df_over)
            st.info("これらは明日用 or 時間延長して再調整してもいいかも！")
