import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day175：健康ポイントシステム"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day175_health_points.json")

ACTIONS = [
    {
        "name": "水分目標達成",
        "icon": "💧",
        "points": 10,
        "stats": {"健康": 2, "体力": 1},
    },
    {
        "name": "筋トレした",
        "icon": "💪",
        "points": 15,
        "stats": {"筋力": 3, "健康": 2, "体力": 2},
    },
    {
        "name": "睡眠7時間以上",
        "icon": "😴",
        "points": 15,
        "stats": {"体力": 3, "メンタル": 2, "健康": 1},
    },
    {
        "name": "野菜を食べた",
        "icon": "🥦",
        "points": 10,
        "stats": {"健康": 3},
    },
    {
        "name": "たんぱく質を取った",
        "icon": "🥩",
        "points": 10,
        "stats": {"筋力": 2, "健康": 1},
    },
    {
        "name": "散歩した",
        "icon": "🚶",
        "points": 10,
        "stats": {"体力": 2, "メンタル": 2},
    },
    {
        "name": "甘いものを控えた",
        "icon": "🍰",
        "points": 8,
        "stats": {"健康": 2, "メンタル": 1},
    },
    {
        "name": "ストレッチした",
        "icon": "🧘",
        "points": 8,
        "stats": {"健康": 1, "体力": 1, "メンタル": 1},
    },
    {
        "name": "深呼吸・休憩した",
        "icon": "🌿",
        "points": 6,
        "stats": {"メンタル": 2},
    },
    {
        "name": "健康メモを記録した",
        "icon": "📝",
        "points": 5,
        "stats": {"集中力": 1},
    },
]

STATS = [
    "健康",
    "筋力",
    "体力",
    "集中力",
    "メンタル",
]

STAT_ICONS = {
    "健康": "❤️",
    "筋力": "💪",
    "体力": "⚡",
    "集中力": "🧠",
    "メンタル": "😊",
}

TITLES = [
    {"name": "🌱 健康の第一歩", "condition": "累計100pt"},
    {"name": "💧 水分意識マン", "condition": "水分目標達成 10回"},
    {"name": "💪 筋トレ戦士", "condition": "筋トレした 10回"},
    {"name": "🥦 野菜の守護者", "condition": "野菜を食べた 10回"},
    {"name": "😴 回復上手", "condition": "睡眠7時間以上 10回"},
    {"name": "❤️ 健康冒険者", "condition": "累計500pt"},
    {"name": "👑 健康王", "condition": "累計2000pt"},
]


def default_stats():
    return {
        "健康": 10,
        "筋力": 10,
        "体力": 10,
        "集中力": 10,
        "メンタル": 10,
    }


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "logs": [],
                    "stats": default_stats(),
                },
                f,
                ensure_ascii=False,
                indent=2
            )


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    if "stats" not in data:
        data["stats"] = default_stats()

    for stat in STATS:
        if stat not in data["stats"]:
            data["stats"][stat] = 10

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def current_week_key(d):
    dt = datetime.strptime(d, "%Y-%m-%d").date()
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def calc_level(total_points):
    if total_points < 100:
        return 1

    if total_points < 250:
        return 2

    if total_points < 500:
        return 3

    if total_points < 1000:
        return 4

    if total_points < 2000:
        return 5

    if total_points < 3500:
        return 6

    if total_points < 5000:
        return 7

    return 8


def next_level_points(total_points):
    borders = [100, 250, 500, 1000, 2000, 3500, 5000]

    for b in borders:
        if total_points < b:
            return b

    return None


def action_count(df, action_name):
    if df.empty:
        return 0

    return len(df[df["action_name"] == action_name])


def unlocked_titles(df, total_points):
    titles = []

    if total_points >= 100:
        titles.append("🌱 健康の第一歩")

    if action_count(df, "水分目標達成") >= 10:
        titles.append("💧 水分意識マン")

    if action_count(df, "筋トレした") >= 10:
        titles.append("💪 筋トレ戦士")

    if action_count(df, "野菜を食べた") >= 10:
        titles.append("🥦 野菜の守護者")

    if action_count(df, "睡眠7時間以上") >= 10:
        titles.append("😴 回復上手")

    if total_points >= 500:
        titles.append("❤️ 健康冒険者")

    if total_points >= 2000:
        titles.append("👑 健康王")

    if not titles:
        titles.append("🔰 健康見習い")

    return titles


def to_df(data):
    rows = []

    for x in data["logs"]:
        row = {
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "week": current_week_key(x["date"]),
            "action_name": x["action_name"],
            "icon": x["icon"],
            "points": int(x.get("points", 0)),
            "memo": x.get("memo", ""),
        }

        for stat in STATS:
            row[stat] = int(x.get("stats", {}).get(stat, 0))

        rows.append(row)

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_log(data, log_id):
    for x in data["logs"]:
        if x["id"] == log_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="❤️",
    layout="wide"
)

st.title("❤️ Day175：健康ポイントシステム")
st.caption("食事・水分・運動・睡眠などをポイント化して、健康をゲームのように育てるアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の健康行動を記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    action_labels = [
        f"{x['icon']} {x['name']}（+{x['points']}pt）"
        for x in ACTIONS
    ]

    selected_label = st.selectbox(
        "行動",
        action_labels
    )

    selected_index = action_labels.index(selected_label)
    selected_action = ACTIONS[selected_index]

    st.markdown(f"## {selected_action['icon']} {selected_action['name']}")
    st.metric("獲得ポイント", selected_action["points"])

    st.write("上がるステータス")

    for stat, value in selected_action["stats"].items():
        st.info(f"{STAT_ICONS[stat]} {stat} +{value}")

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：水2L達成 / 腕立て30回 / しっかり寝た"
    )

    if st.button("❤️ ポイント獲得", type="primary"):
        for stat, value in selected_action["stats"].items():
            data["stats"][stat] = int(data["stats"].get(stat, 10)) + int(value)

        item = {
            "id": f"health_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": log_date.isoformat(),
            "action_name": selected_action["name"],
            "icon": selected_action["icon"],
            "points": int(selected_action["points"]),
            "stats": selected_action["stats"],
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)

        st.success("健康ポイントを獲得したよ！")
        st.rerun()

with right:
    st.subheader("健康ステータス")

    df = to_df(data)

    total_points = int(df["points"].sum()) if not df.empty else 0
    level = calc_level(total_points)
    next_border = next_level_points(total_points)

    c1, c2 = st.columns(2)

    with c1:
        st.metric("健康Lv", level)
        st.metric("累計ポイント", total_points)

    with c2:
        today = today_str()
        today_points = int(df[df["date"] == today]["points"].sum()) if not df.empty else 0
        week = current_week_key(today)
        week_points = int(df[df["week"] == week]["points"].sum()) if not df.empty else 0

        st.metric("今日", today_points)
        st.metric("今週", week_points)

    if next_border:
        progress = total_points / next_border
        st.progress(min(progress, 1.0))
        st.info(f"次のレベルまであと {next_border - total_points} pt")
    else:
        st.success("かなり高レベル！健康王への道を進んでるよ。")

    st.divider()

    for stat in STATS:
        value = int(data["stats"].get(stat, 10))
        st.write(f"{STAT_ICONS[stat]} {stat}：{value}")
        st.progress(min(value / 100, 1.0))

    st.divider()

    st.subheader("称号")
    for title in unlocked_titles(df, total_points):
        st.success(title)

st.divider()
st.subheader("健康ポイント履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b = st.columns(2)

    with col_a:
        action_filter = st.selectbox(
            "行動で絞る",
            ["すべて"] + [x["name"] for x in ACTIONS]
        )

    with col_b:
        week_filter = st.text_input(
            "週で絞る",
            value="",
            placeholder="例：2026-W25"
        )

    view = df.copy()

    if action_filter != "すべて":
        view = view[view["action_name"] == action_filter]

    if week_filter.strip():
        view = view[view["week"] == week_filter.strip()]

    st.dataframe(
        view[[
            "date",
            "icon",
            "action_name",
            "points",
            "健康",
            "筋力",
            "体力",
            "集中力",
            "メンタル",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・削除")

    if view.empty:
        st.write("条件に合う履歴がないよ。")
    else:
        selected_id = st.selectbox(
            "記録を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_log(data, x)['date']} / {find_log(data, x)['icon']} {find_log(data, x)['action_name']}"
        )

        selected = find_log(data, selected_id)

        if selected:
            st.markdown(f"## {selected['icon']} {selected['action_name']}")
            st.write(f"日付：{selected['date']}")
            st.write(f"ポイント：{selected['points']} pt")

            if selected.get("memo"):
                st.info(selected["memo"])

            if st.button("🗑️ この記録を削除", type="secondary"):
                for stat, value in selected.get("stats", {}).items():
                    data["stats"][stat] = max(
                        0,
                        int(data["stats"].get(stat, 10)) - int(value)
                    )

                data["logs"] = [
                    x for x in data["logs"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day175_health_points.csv",
        mime="text/csv"
    )

st.divider()

with st.expander("⚙️ ステータス調整・リセット"):
    adjusted = {}

    for stat in STATS:
        adjusted[stat] = st.number_input(
            f"{STAT_ICONS[stat]} {stat}",
            min_value=0,
            max_value=9999,
            value=int(data["stats"].get(stat, 10)),
            step=1,
            key=f"adjust_{stat}"
        )

    if st.button("📝 ステータスを直接更新"):
        data["stats"] = adjusted
        save_data(data)
        st.success("ステータスを更新したよ。")
        st.rerun()

    if st.button("⚠️ 全データリセット", type="secondary"):
        data["logs"] = []
        data["stats"] = default_stats()
        save_data(data)
        st.warning("リセットしたよ。")
        st.rerun()
