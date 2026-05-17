import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day107：今日のごほうび提案"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day107_reward_suggestion.json")

REWARDS = {
    "がんばった": [
        {
            "reward": "好きなものを少しだけ食べる",
            "reason": "今日はちゃんと前に進んだ日だから",
            "luna": "ご主人、ちゃんと積み上げたね。これはごほうびもらっていい日だよ。"
        },
        {
            "reward": "何もしない時間を10分作る",
            "reason": "がんばった後は回復もセット",
            "luna": "ちゃんと休むのも“できる人”の行動だよ。"
        },
    ],
    "ふつう": [
        {
            "reward": "好きな動画を1本見る",
            "reason": "普通の日もちゃんと価値があるから",
            "luna": "ご主人、今日もちゃんと生きてる。それだけでOK。"
        },
        {
            "reward": "少しゆっくりする",
            "reason": "波を整えるため",
            "luna": "大きく動かない日も、大事な一日だよ。"
        },
    ],
    "つかれた": [
        {
            "reward": "早めに休む",
            "reason": "今日は回復優先の日",
            "luna": "ご主人、今日はほんとにおつかれさま。ちゃんと休も。"
        },
        {
            "reward": "温かい飲み物を飲む",
            "reason": "身体と心をゆるめるため",
            "luna": "少し温まるだけでも、だいぶ違うよ。"
        },
    ],
    "何もできなかった": [
        {
            "reward": "自分を責めない時間",
            "reason": "今日は守った日かもしれない",
            "luna": "何もしてないんじゃないよ。今日は“耐えた日”かも。"
        },
        {
            "reward": "リセットとして早く寝る",
            "reason": "明日のための準備",
            "luna": "明日はまた違う日になるよ。大丈夫。"
        },
    ],
}

RARE_REWARD = [
    {
        "reward": "ちょっといいものを買う or 食べる",
        "reason": "今日は特別にいい日",
        "luna": "ご主人、今日はね…ちょっと当たり日だよ。遠慮しないで。"
    }
]


# ----------------------------
# storage
# ----------------------------
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


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "mood": x["mood"],
            "reward": x["reward"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def draw_reward(mood: str):
    if random.random() < 0.1:
        item = random.choice(RARE_REWARD)
        rarity = "SR"
    else:
        item = random.choice(REWARDS[mood])
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mood": mood,
        "reward": item["reward"],
        "reason": item["reason"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🎁", layout="wide")
st.title("🎁 Day107：今日のごほうび提案")
st.caption("今日の状態に合った“ちょうどいいごほうび”を受け取るアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV", data=csv)

left, right = st.columns([1,1])

with left:
    mood = st.radio("今日の状態", ["がんばった", "ふつう", "つかれた", "何もできなかった"])

    if st.button("🎁 ごほうびをもらう", type="primary"):
        result = draw_reward(mood)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    latest = st.session_state.get("latest")
    if latest:
        st.markdown(f"## {latest['reward']}")
        st.write(latest["reason"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=latest.get("favorite", False))
        if fav != latest.get("favorite", False):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
            save_data(data)

st.divider()

df = to_df(data)
if not df.empty:
    st.dataframe(df)
