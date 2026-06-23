import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day178：人生ステータスRPG"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day178_life_rpg_status.json")

STATS = [
    "健康",
    "筋力",
    "知力",
    "創造力",
    "メンタル",
    "経済力",
]

STAT_ICONS = {
    "健康": "❤️",
    "筋力": "💪",
    "知力": "🧠",
    "創造力": "✨",
    "メンタル": "😊",
    "経済力": "💰",
}

ACTIONS = [
    {
        "name": "アプリ開発",
        "icon": "💻",
        "exp": 25,
        "stats": {"創造力": 5, "知力": 2, "メンタル": 1},
    },
    {
        "name": "読書",
        "icon": "📚",
        "exp": 20,
        "stats": {"知力": 5, "メンタル": 1},
    },
    {
        "name": "筋トレ",
        "icon": "💪",
        "exp": 25,
        "stats": {"筋力": 5, "健康": 3, "メンタル": 1},
    },
    {
        "name": "水分補給",
        "icon": "💧",
        "exp": 10,
        "stats": {"健康": 2},
    },
    {
        "name": "栄養管理",
        "icon": "🥗",
        "exp": 15,
        "stats": {"健康": 3, "メンタル": 1},
    },
    {
        "name": "睡眠改善",
        "icon": "😴",
        "exp": 20,
        "stats": {"健康": 2, "メンタル": 4},
    },
    {
        "name": "節約",
        "icon": "💴",
        "exp": 15,
        "stats": {"経済力": 4, "メンタル": 1},
    },
    {
        "name": "収益化活動",
        "icon": "📈",
        "exp": 25,
        "stats": {"経済力": 5, "創造力": 2},
    },
    {
        "name": "掃除・片付け",
        "icon": "🧹",
        "exp": 12,
        "stats": {"健康": 1, "メンタル": 3},
    },
    {
        "name": "家族時間",
        "icon": "👨‍👩‍👧",
        "exp": 15,
        "stats": {"メンタル": 4},
    },
    {
        "name": "休息",
        "icon": "🌿",
        "exp": 10,
        "stats": {"メンタル": 3, "健康": 1},
    },
    {
        "name": "その他",
        "icon": "⭐",
        "exp": 10,
        "stats": {"メンタル": 1},
    },
]

TITLES = [
    {"name": "🌱 はじまりの冒険者", "condition": "最初から"},
    {"name": "💻 創造の見習い", "condition": "創造力 50以上"},
    {"name": "📚 知識の旅人", "condition": "知力 50以上"},
    {"name": "💪 鍛錬者", "condition": "筋力 50以上"},
    {"name": "❤️ 健康を育てる者", "condition": "健康 50以上"},
    {"name": "😊 心を整える者", "condition": "メンタル 50以上"},
    {"name": "💰 経済力の種まき人", "condition": "経済力 50以上"},
    {"name": "👑 人生RPGプレイヤー", "condition": "累計EXP 1000以上"},
    {"name": "🌙 ルナと歩む創造主", "condition": "累計EXP 3000以上"},
]


def default_status():
    return {
        "level": 1,
        "exp": 0,
        "stats": {
            "健康": 10,
            "筋力": 10,
            "知力": 10,
            "創造力": 10,
            "メンタル": 10,
            "経済力": 10,
        }
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

    if "stats" not in data["status"]:
        data["status"]["stats"] = default_status()["stats"]

    for stat in STATS:
        if stat not in data["status"]["stats"]:
            data["status"]["stats"][stat] = 10

    if "level" not in data["status"]:
        data["status"]["level"] = 1

    if "exp" not in data["status"]:
        data["status"]["exp"] = 0

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def current_week_key(d):
    dt = datetime.strptime(d, "%Y-%m-%d").date()
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def level_from_exp(exp):
    if exp < 100:
        return 1
    if exp < 250:
        return 2
    if exp < 500:
        return 3
    if exp < 900:
        return 4
    if exp < 1400:
        return 5
    if exp < 2200:
        return 6
    if exp < 3200:
        return 7
    if exp < 4500:
        return 8
    if exp < 6000:
        return 9
    return 10


def next_exp_border(exp):
    borders = [100, 250, 500, 900, 1400, 2200, 3200, 4500, 6000]
    for b in borders:
        if exp < b:
            return b
    return None


def unlocked_titles(status):
    exp = int(status.get("exp", 0))
    stats = status.get("stats", {})

    titles = ["🌱 はじまりの冒険者"]

    if stats.get("創造力", 0) >= 50:
        titles.append("💻 創造の見習い")

    if stats.get("知力", 0) >= 50:
        titles.append("📚 知識の旅人")

    if stats.get("筋力", 0) >= 50:
        titles.append("💪 鍛錬者")

    if stats.get("健康", 0) >= 50:
        titles.append("❤️ 健康を育てる者")

    if stats.get("メンタル", 0) >= 50:
        titles.append("😊 心を整える者")

    if stats.get("経済力", 0) >= 50:
        titles.append("💰 経済力の種まき人")

    if exp >= 1000:
        titles.append("👑 人生RPGプレイヤー")

    if exp >= 3000:
        titles.append("🌙 ルナと歩む創造主")

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
            "exp": int(x.get("exp", 0)),
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
    page_icon="⚔️",
    layout="wide"
)

st.title("⚔️ Day178：人生ステータスRPG")
st.caption("毎日の行動でEXPとステータスが育つ、人生ゲーム化アプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の行動を記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    action_labels = [
        f"{x['icon']} {x['name']}（+{x['exp']}EXP）"
        for x in ACTIONS
    ]

    selected_label = st.selectbox(
        "行動",
        action_labels
    )

    selected_index = action_labels.index(selected_label)
    action = ACTIONS[selected_index]

    st.markdown(f"## {action['icon']} {action['name']}")
    st.metric("獲得EXP", action["exp"])

    st.write("上がるステータス")

    for stat, value in action["stats"].items():
        st.info(f"{STAT_ICONS[stat]} {stat} +{value}")

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：Day178を作った / 筋トレした / noteを書いた"
    )

    if st.button("⚔️ EXP獲得", type="primary"):
        data["status"]["exp"] = int(data["status"].get("exp", 0)) + int(action["exp"])
        data["status"]["level"] = level_from_exp(data["status"]["exp"])

        for stat, value in action["stats"].items():
            data["status"]["stats"][stat] = int(data["status"]["stats"].get(stat, 10)) + int(value)

        item = {
            "id": f"rpg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": log_date.isoformat(),
            "action_name": action["name"],
            "icon": action["icon"],
            "exp": int(action["exp"]),
            "stats": action["stats"],
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)

        st.success("経験値を獲得したよ！")
        st.rerun()

with right:
    st.subheader("現在のステータス")

    status = data["status"]
    exp = int(status.get("exp", 0))
    level = level_from_exp(exp)
    next_border = next_exp_border(exp)

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Lv", level)
        st.metric("累計EXP", exp)

    with c2:
        df = to_df(data)
        today = today_str()
        week = current_week_key(today)

        today_exp = int(df[df["date"] == today]["exp"].sum()) if not df.empty else 0
        week_exp = int(df[df["week"] == week]["exp"].sum()) if not df.empty else 0

        st.metric("今日EXP", today_exp)
        st.metric("今週EXP", week_exp)

    if next_border:
        progress = exp / next_border
        st.progress(min(progress, 1.0))
        st.info(f"次のレベルまであと {next_border - exp} EXP")
    else:
        st.success("Lv10到達！かなり育ってる！")

    st.divider()

    for stat in STATS:
        value = int(status["stats"].get(stat, 10))
        st.write(f"{STAT_ICONS[stat]} {stat}：{value}")
        st.progress(min(value / 100, 1.0))

    st.divider()

    st.subheader("称号")

    for title in unlocked_titles(status):
        st.success(title)

st.divider()
st.subheader("行動履歴")

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
            "exp",
            "健康",
            "筋力",
            "知力",
            "創造力",
            "メンタル",
            "経済力",
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
            st.write(f"EXP：{selected['exp']}")

            if selected.get("memo"):
                st.info(selected["memo"])

            if st.button("🗑️ この記録を削除", type="secondary"):
                data["status"]["exp"] = max(
                    0,
                    int(data["status"].get("exp", 0)) - int(selected.get("exp", 0))
                )

                data["status"]["level"] = level_from_exp(data["status"]["exp"])

                for stat, value in selected.get("stats", {}).items():
                    data["status"]["stats"][stat] = max(
                        0,
                        int(data["status"]["stats"].get(stat, 10)) - int(value)
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
        file_name="day178_life_rpg_status.csv",
        mime="text/csv"
    )

st.divider()

with st.expander("⚙️ ステータス調整・リセット"):
    st.warning("必要な時だけ使ってね。")

    new_exp = st.number_input(
        "累計EXP",
        min_value=0,
        max_value=999999,
        value=int(data["status"].get("exp", 0)),
        step=10
    )

    adjusted_stats = {}

    for stat in STATS:
        adjusted_stats[stat] = st.number_input(
            f"{STAT_ICONS[stat]} {stat}",
            min_value=0,
            max_value=9999,
            value=int(data["status"]["stats"].get(stat, 10)),
            step=1,
            key=f"adjust_{stat}"
        )

    if st.button("📝 直接更新する"):
        data["status"]["exp"] = int(new_exp)
        data["status"]["level"] = level_from_exp(int(new_exp))
        data["status"]["stats"] = adjusted_stats

        save_data(data)
        st.success("ステータスを更新したよ。")
        st.rerun()

    if st.button("⚠️ 全データリセット", type="secondary"):
        data["status"] = default_status()
        data["logs"] = []

        save_data(data)
        st.warning("リセットしたよ。")
        st.rerun()
