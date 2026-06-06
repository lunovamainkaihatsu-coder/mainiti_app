import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day162：人生ステータス画面"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day162_life_status.json")

STATS = [
    "体力",
    "精神力",
    "知識",
    "開発力",
    "経済力",
    "人間関係",
]

STAT_ICONS = {
    "体力": "❤️",
    "精神力": "😊",
    "知識": "🧠",
    "開発力": "💻",
    "経済力": "💰",
    "人間関係": "🤝",
}

ACTIONS = [
    "筋トレ",
    "ストレッチ",
    "読書",
    "開発",
    "勉強",
    "感謝",
    "会話",
    "家計管理",
    "仕事",
    "回復",
    "その他",
]

TITLES = [
    {"name": "🌱 はじまりの冒険者", "condition": "総合Lv 1"},
    {"name": "📚 学びの旅人", "condition": "知識 50以上"},
    {"name": "💻 小さな開発者", "condition": "開発力 50以上"},
    {"name": "❤️ 体力づくりの挑戦者", "condition": "体力 50以上"},
    {"name": "😊 心を整える者", "condition": "精神力 50以上"},
    {"name": "💰 金銭感覚の見習い", "condition": "経済力 50以上"},
    {"name": "🤝 つながりを大切にする者", "condition": "人間関係 50以上"},
    {"name": "👑 バランス型成長者", "condition": "全ステータス 50以上"},
]


def default_status():
    return {
        "体力": 10,
        "精神力": 10,
        "知識": 10,
        "開発力": 10,
        "経済力": 10,
        "人間関係": 10,
    }


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "status": default_status(),
                    "logs": [],
                },
                f,
                ensure_ascii=False,
                indent=2
            )


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "status" not in data:
        data["status"] = default_status()

    if "logs" not in data:
        data["logs"] = []

    for stat in STATS:
        if stat not in data["status"]:
            data["status"][stat] = 10

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def calc_level(total):
    return total // 100 + 1


def unlocked_titles(status):
    total = sum(status.values())
    level = calc_level(total)

    result = ["🌱 はじまりの冒険者"]

    if status["知識"] >= 50:
        result.append("📚 学びの旅人")

    if status["開発力"] >= 50:
        result.append("💻 小さな開発者")

    if status["体力"] >= 50:
        result.append("❤️ 体力づくりの挑戦者")

    if status["精神力"] >= 50:
        result.append("😊 心を整える者")

    if status["経済力"] >= 50:
        result.append("💰 金銭感覚の見習い")

    if status["人間関係"] >= 50:
        result.append("🤝 つながりを大切にする者")

    if all(v >= 50 for v in status.values()):
        result.append("👑 バランス型成長者")

    if level >= 10:
        result.append("🌙 ルナと歩む者")

    return result


def to_df(data):
    rows = []

    for x in data["logs"]:
        row = {
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "action_name": x["action_name"],
            "action_type": x["action_type"],
            "memo": x.get("memo", ""),
        }

        for stat in STATS:
            row[stat] = x["changes"].get(stat, 0)

        rows.append(row)

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚔️",
    layout="wide"
)

st.title("⚔️ Day162：人生ステータス画面")
st.caption("行動すると能力が上がる、人生RPG風のステータス管理アプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("行動を記録して能力アップ")

    action_name = st.text_input(
        "今日の行動",
        placeholder="例：読書30分 / アプリ開発 / 筋トレ"
    )

    action_type = st.selectbox(
        "行動カテゴリ",
        ACTIONS
    )

    st.write("上がった能力を入力")

    changes = {}

    c1, c2 = st.columns(2)

    for i, stat in enumerate(STATS):
        with c1 if i % 2 == 0 else c2:
            changes[stat] = st.number_input(
                f"{STAT_ICONS[stat]} {stat}",
                min_value=0,
                max_value=20,
                value=0,
                step=1,
                key=f"change_{stat}"
            )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：心理学を学んだ / 5分だけでも進めた"
    )

    if st.button("⚔️ ステータスに反映", type="primary"):
        if not action_name.strip():
            st.warning("行動名を入力してね。")
        elif sum(changes.values()) == 0:
            st.warning("どれか1つは能力を上げてね。")
        else:
            for stat, value in changes.items():
                data["status"][stat] += int(value)

            item = {
                "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "action_name": action_name.strip(),
                "action_type": action_type,
                "changes": changes,
                "memo": memo.strip(),
            }

            data["logs"].append(item)
            save_data(data)

            st.success("ステータスが上がったよ！")
            st.rerun()

with right:
    st.subheader("現在のステータス")

    status = data["status"]
    total = sum(status.values())
    level = calc_level(total)

    st.metric("総合レベル", level)
    st.metric("総合ポイント", total)

    st.divider()

    for stat in STATS:
        value = status.get(stat, 0)
        progress = min(value / 100, 1.0)

        st.write(f"{STAT_ICONS[stat]} {stat}：{value}")
        st.progress(progress)

    st.divider()

    st.subheader("称号")
    titles = unlocked_titles(status)

    for title in titles:
        st.success(title)

st.divider()
st.subheader("成長履歴")

df = to_df(data)

if df.empty:
    st.write("まだ成長履歴がないよ。")
else:
    st.dataframe(
        df[["date", "action_name", "action_type", "体力", "精神力", "知識", "開発力", "経済力", "人間関係", "memo"]],
        use_container_width=True,
        height=320
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day162_life_status_logs.csv",
        mime="text/csv"
    )

st.divider()

with st.expander("⚙️ ステータス調整・リセット"):
    st.warning("ステータスを直接調整する場合だけ使ってね。")

    adjusted = {}

    for stat in STATS:
        adjusted[stat] = st.number_input(
            f"{STAT_ICONS[stat]} {stat} 現在値",
            min_value=0,
            max_value=9999,
            value=int(data["status"].get(stat, 10)),
            step=1,
            key=f"adjust_{stat}"
        )

    if st.button("📝 ステータスを直接更新"):
        data["status"] = adjusted
        save_data(data)
        st.success("ステータスを更新したよ。")
        st.rerun()

    if st.button("⚠️ 全データリセット", type="secondary"):
        data["status"] = default_status()
        data["logs"] = []
        save_data(data)
        st.warning("リセットしたよ。")
        st.rerun()
