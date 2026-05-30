import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day153：習慣図鑑"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day153_habit_encyclopedia.json")

HABIT_BOOK = [
    {"no": "001", "name": "水分補給", "icon": "💧", "rarity": "N", "desc": "水を飲んで身体を整える基本習慣。"},
    {"no": "002", "name": "ストレッチ", "icon": "🧘", "rarity": "N", "desc": "身体をゆるめて回復を助ける習慣。"},
    {"no": "003", "name": "筋トレ", "icon": "💪", "rarity": "SR", "desc": "身体と自信を育てる成長習慣。"},
    {"no": "004", "name": "読書", "icon": "📚", "rarity": "R", "desc": "知識と考え方を増やす習慣。"},
    {"no": "005", "name": "開発", "icon": "💻", "rarity": "SR", "desc": "未来を作る創造習慣。"},
    {"no": "006", "name": "散歩", "icon": "🚶", "rarity": "R", "desc": "気分と身体を整える軽い行動。"},
    {"no": "007", "name": "感謝", "icon": "🙏", "rarity": "R", "desc": "今日の中の光を見つける習慣。"},
    {"no": "008", "name": "未来ノート", "icon": "🌌", "rarity": "SR", "desc": "理想の未来を言葉にして近づく習慣。"},
    {"no": "009", "name": "タイムライン記録", "icon": "🕒", "rarity": "R", "desc": "今日やったことを見える化する習慣。"},
    {"no": "010", "name": "お金ログ", "icon": "💴", "rarity": "R", "desc": "お金の使い方を振り返る習慣。"},
    {"no": "011", "name": "忘れ物チェック", "icon": "🎒", "rarity": "N", "desc": "出発前の安心を作る習慣。"},
    {"no": "012", "name": "回復行動", "icon": "🌿", "rarity": "R", "desc": "休むことも行動として残す習慣。"},
    {"no": "013", "name": "気持ち切り替え", "icon": "🔀", "rarity": "R", "desc": "気分を小さく切り替える習慣。"},
    {"no": "014", "name": "クエスト達成", "icon": "⚔️", "rarity": "SR", "desc": "日常をゲームのように進める習慣。"},
    {"no": "015", "name": "ルナ計画継続者", "icon": "🌙", "rarity": "SSR", "desc": "未来へ向けて作り続ける特別な習慣。"},
]

RARITY_ORDER = {"N": 1, "R": 2, "SR": 3, "SSR": 4}


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"unlocked": [], "logs": []}, f, ensure_ascii=False, indent=2)


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
    unlocked = data.get("unlocked", [])

    for item in HABIT_BOOK:
        rows.append({
            "No": item["no"],
            "習慣": item["name"],
            "レア度": item["rarity"],
            "解放": item["no"] in unlocked,
            "説明": item["desc"],
        })

    return pd.DataFrame(rows)


st.set_page_config(page_title=APP_TITLE, page_icon="📚", layout="wide")
st.title("📚 Day153：習慣図鑑")
st.caption("達成した習慣を図鑑に登録していく、ゲーム風の記録アプリ。")

data = load_data()

if "unlocked" not in data:
    data["unlocked"] = []

if "logs" not in data:
    data["logs"] = []

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("習慣を解放する")

    options = [
        f"No.{x['no']} {x['icon']} {x['name']} [{x['rarity']}]"
        for x in HABIT_BOOK
    ]

    selected_label = st.selectbox("解放する習慣", options)
    selected_index = options.index(selected_label)
    selected_item = HABIT_BOOK[selected_index]

    st.markdown(f"## {selected_item['icon']} {selected_item['name']}")
    st.write(f"レア度：{selected_item['rarity']}")
    st.info(selected_item["desc"])

    memo = st.text_area(
        "解放メモ",
        placeholder="例：今日ストレッチできた / 開発を5分進めた"
    )

    if st.button("✨ 図鑑に登録", type="primary"):
        if selected_item["no"] not in data["unlocked"]:
            data["unlocked"].append(selected_item["no"])

        data["logs"].append({
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "no": selected_item["no"],
            "name": selected_item["name"],
            "rarity": selected_item["rarity"],
            "memo": memo.strip(),
        })

        save_data(data)
        st.success("図鑑に登録したよ！")
        st.rerun()

with right:
    st.subheader("図鑑ステータス")

    total = len(HABIT_BOOK)
    unlocked_count = len(data["unlocked"])
    rate = int(unlocked_count / total * 100) if total else 0

    st.metric("解放数", f"{unlocked_count} / {total}")
    st.metric("解放率", f"{rate}%")
    st.progress(rate / 100)

    if rate >= 100:
        st.success("コンプリート！ご主人、習慣マスターだよ！")
    elif rate >= 70:
        st.info("かなり埋まってきたね。あと少し！")
    elif rate >= 40:
        st.info("いい感じに図鑑が育ってきてるよ。")
    else:
        st.info("ここから少しずつ埋めていこう。")

    st.divider()
    st.subheader("レア度別")

    for rarity in ["N", "R", "SR", "SSR"]:
        items = [x for x in HABIT_BOOK if x["rarity"] == rarity]
        unlocked_items = [x for x in items if x["no"] in data["unlocked"]]
        st.write(f"{rarity}：{len(unlocked_items)} / {len(items)}")

st.divider()
st.subheader("習慣図鑑")

rarity_filter = st.selectbox("レア度フィルタ", ["すべて", "N", "R", "SR", "SSR"])
show_only_unlocked = st.checkbox("解放済みだけ表示")

book_items = HABIT_BOOK.copy()

if rarity_filter != "すべて":
    book_items = [x for x in book_items if x["rarity"] == rarity_filter]

if show_only_unlocked:
    book_items = [x for x in book_items if x["no"] in data["unlocked"]]

cols = st.columns(3)

for i, item in enumerate(book_items):
    unlocked = item["no"] in data["unlocked"]

    with cols[i % 3]:
        if unlocked:
            st.markdown(f"### No.{item['no']} {item['icon']} {item['name']}")
            st.write(f"レア度：{item['rarity']}")
            st.success(item["desc"])
        else:
            st.markdown(f"### No.{item['no']} ？？？")
            st.write(f"レア度：{item['rarity']}")
            st.warning("未解放")
        st.divider()

st.subheader("一覧")

df = to_df(data)
st.dataframe(df, use_container_width=True, height=300)

if data["logs"]:
    st.subheader("解放ログ")

    log_df = pd.DataFrame(data["logs"])
    log_df = log_df.sort_values("created_at", ascending=False)

    st.dataframe(
        log_df[["date", "name", "rarity", "memo"]],
        use_container_width=True,
        height=240
    )

    csv = log_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ 解放ログCSV",
        data=csv,
        file_name="day153_habit_encyclopedia_logs.csv",
        mime="text/csv"
    )

st.divider()

if st.button("⚠️ 図鑑データをリセット", type="secondary"):
    data["unlocked"] = []
    data["logs"] = []
    save_data(data)
    st.warning("図鑑データをリセットしたよ。")
    st.rerun()
