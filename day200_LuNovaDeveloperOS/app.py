import json
import os

import streamlit as st


st.set_page_config(
    page_title="LuNova Developer OS",
    page_icon="🏆",
    layout="wide"
)


TASK_FILE = "data/tasks.json"

DEFAULT_TASKS = {
    "アプリ開発": False,
    "note投稿": False,
    "X投稿": False,
    "GitHub更新": False,
    "筋トレ": False,
}


def load_tasks():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(TASK_FILE):
        save_tasks(DEFAULT_TASKS)
        return DEFAULT_TASKS.copy()

    try:
        with open(TASK_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        save_tasks(DEFAULT_TASKS)
        return DEFAULT_TASKS.copy()


def save_tasks(tasks):
    os.makedirs("data", exist_ok=True)

    with open(TASK_FILE, "w", encoding="utf-8") as file:
        json.dump(
            tasks,
            file,
            ensure_ascii=False,
            indent=2
        )


tasks = load_tasks()


st.title("🏆 LuNova Developer OS")
st.caption("LuNovaの開発・発信・収益化を管理する司令室")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📱 開発中",
        value="3"
    )

with col2:
    st.metric(
        label="✅ アプリアイデア",
        value="200"
    )

with col3:
    completed_count = sum(tasks.values())

    st.metric(
        label="🎯 今日の達成",
        value=f"{completed_count} / {len(tasks)}"
    )

st.divider()

st.header("🎯 今日のミッション")

updated_tasks = {}

for task_name, completed in tasks.items():
    updated_tasks[task_name] = st.checkbox(
        task_name,
        value=completed,
        key=f"task_{task_name}"
    )

if updated_tasks != tasks:
    save_tasks(updated_tasks)
    tasks = updated_tasks
    st.rerun()

progress = sum(tasks.values()) / len(tasks)

st.progress(progress)

st.write(
    f"今日の達成率："
    f"**{int(progress * 100)}％**"
)

if progress == 1:
    st.success("🎉 今日のミッションをすべて達成しました！")

elif progress >= 0.6:
    st.info("🔥 いいペースです。あと少し！")

elif progress > 0:
    st.info("🌱 今日も着実に前進しています。")

else:
    st.info("🌙 まずは一つ、できることから始めよう。")

st.divider()

st.header("🚀 現在開発中")

app_col1, app_col2, app_col3 = st.columns(3)

with app_col1:
    st.subheader("🌙 Luna")
    st.write("寄り添うAIパートナー")
    st.progress(0.65)
    st.caption("完成度：65％")

with app_col2:
    st.subheader("🌿 LifeRhythmAI")
    st.write("生活習慣を支えるAI")
    st.progress(0.45)
    st.caption("完成度：45％")

with app_col3:
    st.subheader("📚 次の一冊")
    st.write("AI本レコメンドアプリ")
    st.progress(0.80)
    st.caption("完成度：80％")

st.divider()

st.success(
    "LuNova Developer OSへようこそ。"
    "今日も自分のペースで、確実に前へ進もう。"
)
