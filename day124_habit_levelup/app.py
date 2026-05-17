import streamlit as st
import json
import os
from datetime import date, timedelta
import pandas as pd

APP_TITLE = "Day124：習慣レベルアップ"
DATA_PATH = os.path.join("data", "day122_habit_tracker.json")

XP_PER_CHECK = 10
XP_PER_LEVEL = 100


def load_data():
    if not os.path.exists(DATA_PATH):
        return {"habits": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_streak(logs):
    streak = 0
    today = date.today()

    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if d in logs:
            streak += 1
        else:
            break

    return streak


def calc_level(xp):
    level = xp // XP_PER_LEVEL + 1
    current = xp % XP_PER_LEVEL
    progress = current / XP_PER_LEVEL
    return level, current, progress


def title_by_level(level):
    if level >= 20:
        return "伝説の習慣者"
    elif level >= 15:
        return "習慣マスター"
    elif level >= 10:
        return "継続の達人"
    elif level >= 5:
        return "習慣育成者"
    else:
        return "習慣の芽"


def luna_comment(level, streak):
    if level >= 10:
        return "ご主人、この習慣かなり育ってるよ。もう立派な武器だね。"
    elif streak >= 7:
        return "一週間続いてるのすごいよ。ちゃんと力になってる。"
    elif streak >= 3:
        return "いい感じに芽が出てきたね。このまま小さく続けよう。"
    else:
        return "まずはここから。1回分の記録もちゃんと意味があるよ。"


st.set_page_config(page_title=APP_TITLE, page_icon="🆙", layout="wide")
st.title("🆙 Day124：習慣レベルアップ")
st.caption("習慣を経験値とレベルで見える化するゲーム風アプリ。")

data = load_data()

if not data["habits"]:
    st.info("習慣データがないよ。先にDay122：習慣チェック表を使ってね。")
    st.stop()

rows = []

for h in data["habits"]:
    logs = h.get("logs", [])
    xp = len(logs) * XP_PER_CHECK
    level, current_xp, progress = calc_level(xp)
    streak = calc_streak(logs)

    rows.append({
        "id": h.get("id"),
        "習慣": h.get("name"),
        "XP": xp,
        "レベル": level,
        "次Lvまで": XP_PER_LEVEL - current_xp,
        "連続日数": streak,
        "称号": title_by_level(level),
        "お気に入り": bool(h.get("favorite", False)),
        "progress": progress,
    })

df = pd.DataFrame(rows).sort_values(["レベル", "XP"], ascending=[False, False])

# ----------------------------
# 全体ステータス
# ----------------------------
st.subheader("全体ステータス")

total_xp = int(df["XP"].sum())
avg_level = df["レベル"].mean()
max_level = df["レベル"].max()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("総習慣XP", total_xp)

with c2:
    st.metric("平均レベル", f"{avg_level:.1f}")

with c3:
    st.metric("最高レベル", int(max_level))

st.divider()

# ----------------------------
# 習慣カード
# ----------------------------
st.subheader("習慣カード")

for _, row in df.iterrows():
    with st.container():
        st.markdown(f"## Lv.{row['レベル']}｜{row['習慣']}")
        st.write(f"称号：**{row['称号']}**")
        st.write(f"XP：{row['XP']} / 次のレベルまで：{row['次Lvまで']} XP")
        st.progress(row["progress"])
        st.write(f"連続日数：{row['連続日数']}日")
        st.info(luna_comment(row["レベル"], row["連続日数"]))
        st.divider()

# ----------------------------
# ランキング
# ----------------------------
st.subheader("ランキング")

st.dataframe(
    df[["習慣", "レベル", "XP", "連続日数", "称号", "お気に入り"]],
    use_container_width=True
)

# ----------------------------
# グラフ
# ----------------------------
st.subheader("習慣XPグラフ")
st.bar_chart(df.set_index("習慣")["XP"])

# ----------------------------
# CSV
# ----------------------------
csv = df.drop(columns=["progress"]).to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ CSVダウンロード",
    data=csv,
    file_name="day124_habit_levelup.csv",
    mime="text/csv"
)
