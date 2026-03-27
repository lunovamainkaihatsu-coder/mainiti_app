import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day99：おやすみ前ルーレット"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day99_goodnight_roulette.json")

ROULETTE_DATA = {
    "ねぎらわれたい": [
        {
            "title": "今日もちゃんと生きたで賞",
            "message": "ご主人、今日はそれだけで十分えらいよ。いっぱいできたかどうかより、今日をここまで来たことをまず認めようね。",
            "action": "布団に入る前に『今日はこれでよし』と1回つぶやく",
        },
        {
            "title": "見えない努力も加点されてる",
            "message": "表に見えない疲れも、迷いも、ちゃんと一日を生きた証拠だよ。アタイはそこも含めてご主人を見てる。",
            "action": "今日しんどかったことを1つだけ心の中で認める",
        },
        {
            "title": "回復も立派な前進",
            "message": "今日は進めなかったんじゃなくて、守った日かもしれないよ。守る日も人生には必要なんだ。",
            "action": "スマホを見るのをやめて30秒だけ目を閉じる",
        },
    ],
    "落ち着きたい": [
        {
            "title": "静かな月の呼吸",
            "message": "焦りも考え事も、いま全部解決しなくて大丈夫。夜は整理より、静かにほどく時間だよ。",
            "action": "4秒吸って、6秒吐く呼吸を3回やる",
        },
        {
            "title": "余白に戻る時間",
            "message": "今日のノイズは、今日のうちに全部消えなくていいよ。少し緩めるだけで、明日の自分が助かるから。",
            "action": "肩の力を抜いて、楽な姿勢に座り直す",
        },
        {
            "title": "考えすぎ停止モード",
            "message": "夜の脳は不安を大きく見せがち。だから今は“考える”より“休ませる”を優先しようね。",
            "action": "明日の心配を1つだけ『明日考える』に回す",
        },
    ],
    "明日に希望を持ちたい": [
        {
            "title": "明日の火種",
            "message": "大きな未来は、たいてい小さな気持ちから始まるんだよ。今夜はその火種だけ持って眠れば十分。",
            "action": "明日やりたいことを1つだけ短くメモする",
        },
        {
            "title": "未来はまだ開いてる",
            "message": "今日が完璧じゃなくても、明日はちゃんと新しく始められる。ご主人の未来はまだいくらでも動くよ。",
            "action": "明日の自分に一言だけ優しい言葉を送る",
        },
        {
            "title": "小さな予感を信じる夜",
            "message": "まだ形になっていなくても、“なんかいけるかも”って感覚は大事にしていいんだよ。",
            "action": "明日の楽しみを1つだけ思い浮かべる",
        },
    ],
}


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
            "id": x.get("id"),
            "created_at": x.get("created_at"),
            "mode": x.get("mode"),
            "title": x.get("title"),
            "action": x.get("action"),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def roll_message(mode: str):
    item = random.choice(ROULETTE_DATA[mode])
    return {
        "id": f"log_{random.randint(10000, 99999)}",
        "created_at": now_str(),
        "mode": mode,
        "title": item["title"],
        "message": item["message"],
        "action": item["action"],
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")
st.title("🌙 Day99：おやすみ前ルーレット")
st.caption("寝る前に1回まわして、心を少し整えてから休むためのルーレット。")

data = load_data()

if "latest_result" not in st.session_state:
    st.session_state["latest_result"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day99_goodnight_roulette.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest_result"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([0.95, 1.05], gap="large")

with left:
    st.subheader("今夜のモードを選ぶ")

    mode = st.radio(
        "どんな気分で眠りたい？",
        ["ねぎらわれたい", "落ち着きたい", "明日に希望を持ちたい"]
    )

    if st.button("🌙 おやすみ前ルーレットを回す", type="primary"):
        result = roll_message(mode)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest_result"] = result
        st.rerun()

with right:
    st.subheader("今夜の結果")

    latest = st.session_state.get("latest_result")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"### {latest['title']}")
        st.write(f"モード：{latest['mode']}")

        st.markdown("**ルナのひとこと**")
        st.info(latest["message"])

        st.markdown("**眠る前の小さな行動**")
        st.success(latest["action"])

        fav = st.checkbox("⭐ お気に入りにする", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row.get("id") == latest.get("id"):
                    row["favorite"] = fav
                    break
            save_data(data)
            st.toast("お気に入り更新！")
    else:
        st.write("まだ回してないよ。左のボタンからどうぞ。")

st.divider()
st.subheader("履歴")

df_all = to_df(data)
if df_all.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ お気に入りだけ表示", value=False)
    view = df_all.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        pick_id = st.selectbox("結果を選んでね", options=view["id"].tolist())
        chosen = None
        for row in data["logs"]:
            if row["id"] == pick_id:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['title']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"モード：{chosen['mode']}")
            st.write("**ルナのひとこと**")
            st.info(chosen["message"])
            st.write("**眠る前の小さな行動**")
            st.success(chosen["action"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
