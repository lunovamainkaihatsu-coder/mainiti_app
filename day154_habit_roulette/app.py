import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day154：習慣ルーレット"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day154_habit_roulette.json")

HABITS = [
    {"name": "水分補給", "icon": "💧", "action": "水を一口飲む", "exp": 5},
    {"name": "ストレッチ", "icon": "🧘", "action": "首か肩を30秒伸ばす", "exp": 8},
    {"name": "筋トレ", "icon": "💪", "action": "スクワット10回", "exp": 12},
    {"name": "読書", "icon": "📚", "action": "本を1ページ読む", "exp": 10},
    {"name": "開発", "icon": "💻", "action": "アプリを5分だけ触る", "exp": 15},
    {"name": "散歩", "icon": "🚶", "action": "外の空気を吸う", "exp": 10},
    {"name": "感謝", "icon": "🙏", "action": "ありがとうを1つ書く", "exp": 8},
    {"name": "未来ノート", "icon": "🌌", "action": "未来を1行書く", "exp": 12},
    {"name": "タイムライン記録", "icon": "🕒", "action": "今日やったことを1つ記録", "exp": 8},
    {"name": "お金ログ", "icon": "💴", "action": "今日使ったお金を1つ記録", "exp": 8},
    {"name": "忘れ物チェック", "icon": "🎒", "action": "持ち物を1つ確認する", "exp": 5},
    {"name": "回復行動", "icon": "🌿", "action": "深呼吸を3回する", "exp": 8},
    {"name": "気持ち切り替え", "icon": "🔀", "action": "今の気分を一言で書く", "exp": 8},
    {"name": "クエスト達成", "icon": "⚔️", "action": "小さなクエストを1つこなす", "exp": 15},
]

COMMENTS = [
    "小さくても、やったら経験値だよ。",
    "今日はこれだけでも十分前進！",
    "ルーレットで決めると、迷いが減るね。",
    "ご主人、これは図鑑解放チャンスかも。",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "habit": x["habit"],
            "action": x["action"],
            "exp": x["exp"],
            "done": bool(x.get("done", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🎲", layout="wide")
st.title("🎲 Day154：習慣ルーレット")
st.caption("今日はどの習慣をやるか、ルーレットで決めるアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("ルーレット")

    if st.button("🎲 習慣を回す", type="primary"):
        habit = random.choice(HABITS)

        item = {
            "id": f"habit_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "habit": f"{habit['icon']} {habit['name']}",
            "action": habit["action"],
            "exp": habit["exp"],
            "comment": random.choice(COMMENTS),
            "done": False,
            "memo": "",
        }

        data["logs"].append(item)
        save_data(data)
        st.session_state["latest"] = item
        st.rerun()

with right:
    st.subheader("今日の習慣")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"## {latest['habit']}")
        st.markdown("### やること")
        st.success(latest["action"])

        st.metric("EXP", latest["exp"])
        st.info(latest["comment"])

        done = st.checkbox("✅ やった", value=bool(latest.get("done", False)))
        memo = st.text_area("メモ", value=latest.get("memo", ""))

        if st.button("📝 保存"):
            latest["done"] = done
            latest["memo"] = memo.strip()

            for x in data["logs"]:
                if x["id"] == latest["id"]:
                    x.update(latest)
                    break

            save_data(data)
            st.success("保存したよ。")
            st.rerun()
    else:
        st.info("まだルーレットを回してないよ。")

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    done_only = st.checkbox("✅ 実行済みだけ表示")
    view = df.copy()

    if done_only:
        view = view[view["done"] == True]

    st.dataframe(
        view[["date", "habit", "action", "exp", "done", "memo"]],
        use_container_width=True,
        height=320
    )

    total_exp = int(df[df["done"] == True]["exp"].sum())
    st.metric("獲得EXP", total_exp)

    if not view.empty:
        selected = st.selectbox("削除する記録を選ぶ", view["id"].tolist())

        if st.button("🗑️ 選択した記録を削除", type="secondary"):
            data["logs"] = [x for x in data["logs"] if x["id"] != selected]
            save_data(data)
            st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day154_habit_roulette.csv",
        mime="text/csv"
    )
