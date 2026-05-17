import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day141：ストレッチ提案アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day141_stretch_suggester.json")

CONDITIONS = ["眠い・だるい", "肩こり", "腰が重い", "脚が重い", "運動後", "寝る前"]
LEVELS = ["超軽め", "普通", "しっかり"]

STRETCHES = {
    "眠い・だるい": {
        "超軽め": [
            ["首を左右にゆっくり倒す 20秒", "肩回し 10回", "深呼吸 3回"],
            ["背伸び 20秒", "手首・足首回し 各10回", "深呼吸 3回"],
        ],
        "普通": [
            ["首ストレッチ 左右30秒", "肩甲骨寄せ 10回", "背伸び 30秒", "前屈 20秒"],
        ],
        "しっかり": [
            ["首ストレッチ 左右30秒", "肩回し 20回", "背中伸ばし 30秒", "股関節回し 20回", "深呼吸 5回"],
        ],
    },
    "肩こり": {
        "超軽め": [
            ["肩回し 前後10回", "首を左右に倒す 各20秒", "肩をすくめて脱力 5回"],
        ],
        "普通": [
            ["肩回し 前後15回", "首ストレッチ 左右30秒", "肩甲骨寄せ 15回", "胸開き 30秒"],
        ],
        "しっかり": [
            ["肩回し 前後20回", "首ストレッチ 左右40秒", "肩甲骨寄せ 20回", "胸開き 40秒", "背中丸め伸ばし 40秒"],
        ],
    },
    "腰が重い": {
        "超軽め": [
            ["膝抱えストレッチ 30秒", "腰を左右に倒す 10回", "深呼吸 3回"],
        ],
        "普通": [
            ["膝抱え 左右30秒", "猫のポーズ 10回", "お尻ストレッチ 左右30秒"],
        ],
        "しっかり": [
            ["猫のポーズ 15回", "膝抱え 左右40秒", "お尻ストレッチ 左右40秒", "股関節開き 40秒"],
        ],
    },
    "脚が重い": {
        "超軽め": [
            ["足首回し 左右10回", "ふくらはぎ伸ばし 左右20秒", "太もも軽くさする 30秒"],
        ],
        "普通": [
            ["ふくらはぎ伸ばし 左右30秒", "太もも前伸ばし 左右30秒", "もも裏伸ばし 左右30秒"],
        ],
        "しっかり": [
            ["ふくらはぎ伸ばし 左右40秒", "太もも前伸ばし 左右40秒", "もも裏伸ばし 左右40秒", "股関節回し 20回"],
        ],
    },
    "運動後": {
        "超軽め": [
            ["深呼吸 3回", "使った部位を軽く伸ばす 30秒", "水を飲む"],
        ],
        "普通": [
            ["太もも前伸ばし 左右30秒", "もも裏伸ばし 左右30秒", "胸開き 30秒", "深呼吸 5回"],
        ],
        "しっかり": [
            ["太もも前伸ばし 左右40秒", "もも裏伸ばし 左右40秒", "お尻ストレッチ 左右40秒", "胸開き 40秒", "背中伸ばし 40秒"],
        ],
    },
    "寝る前": {
        "超軽め": [
            ["深呼吸 5回", "首をゆっくり回す 5回", "肩の力を抜く"],
        ],
        "普通": [
            ["深呼吸 5回", "背伸び 30秒", "前屈 30秒", "お尻ストレッチ 左右30秒"],
        ],
        "しっかり": [
            ["深呼吸 5回", "前屈 40秒", "股関節開き 40秒", "お尻ストレッチ 左右40秒", "首ストレッチ 左右30秒"],
        ],
    },
}

LUNA_COMMENTS = {
    "眠い・だるい": [
        "ご主人、今日はまず身体をゆるめるところからでいいよ。",
        "だるい日は軽く動かすだけでも血が巡るよ。",
    ],
    "肩こり": [
        "肩まわり、少しほどいてあげよっか。",
        "首と肩は頑張りが出やすい場所だよ。やさしくね。",
    ],
    "腰が重い": [
        "腰が重い日は無理に反らさず、ゆっくりいこう。",
        "ご主人、腰は大事。気持ちよさ優先でね。",
    ],
    "脚が重い": [
        "脚が重い日は、ふくらはぎをゆるめると楽になりやすいよ。",
        "今日の脚、ちゃんと支えてくれてたんだね。労わろう。",
    ],
    "運動後": [
        "運動後のケアまでできたら、かなり偉いよ。",
        "筋トレした身体に、ちゃんとありがとうしようね。",
    ],
    "寝る前": [
        "寝る前は頑張らないストレッチが正解だよ。",
        "ご主人、今日はゆっくり眠れる準備をしようね。",
    ],
}


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


def generate_plan(condition, level):
    return random.choice(STRETCHES[condition][level])


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "date": x["date"],
            "condition": x["condition"],
            "level": x["level"],
            "menu": " / ".join(x["menu"]),
            "done": bool(x.get("done", False)),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🧘", layout="wide")
st.title("🧘 Day141：ストレッチ提案アプリ")
st.caption("今の身体の状態に合わせて、軽いストレッチメニューを提案するアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今の身体の状態")

    condition = st.radio("状態", CONDITIONS, horizontal=False)
    level = st.radio("強度", LEVELS, horizontal=True)

    if st.button("🧘 ストレッチ提案", type="primary"):
        menu = generate_plan(condition, level)

        item = {
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "condition": condition,
            "level": level,
            "menu": menu,
            "done": False,
            "memo": "",
            "favorite": False,
            "comment": random.choice(LUNA_COMMENTS[condition]),
        }

        data["logs"].append(item)
        save_data(data)
        st.session_state["latest"] = item
        st.rerun()

with right:
    st.subheader("今日のストレッチ")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"## {latest['condition']} × {latest['level']}")

        st.markdown("### メニュー")
        for i, m in enumerate(latest["menu"], start=1):
            st.success(f"{i}. {m}")

        st.markdown("### ルナコメント")
        st.info(latest["comment"])

        done = st.checkbox("✅ 実行した", value=bool(latest.get("done", False)))
        favorite = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))
        memo = st.text_area("メモ", value=latest.get("memo", ""))

        if st.button("📝 保存"):
            latest["done"] = done
            latest["favorite"] = favorite
            latest["memo"] = memo

            for x in data["logs"]:
                if x["id"] == latest["id"]:
                    x.update(latest)

            save_data(data)
            st.success("保存したよ！")
            st.rerun()
    else:
        st.info("まだ提案がないよ。")

st.divider()

st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ")
else:
    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )

    selected = st.selectbox("削除する記録を選ぶ", df["id"].tolist())

    if st.button("🗑️ 選択した記録を削除", type="secondary"):
        data["logs"] = [x for x in data["logs"] if x["id"] != selected]
        save_data(data)
        st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day141_stretch_suggester.csv",
        mime="text/csv"
    )
