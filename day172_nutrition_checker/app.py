import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day172：栄養バランスチェッカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day172_nutrition_checker.json")

PROTEIN_WORDS = [
    "卵", "鶏", "サラダチキン", "牛肉", "豚肉", "魚", "まぐろ", "鮭",
    "プロテイン", "ヨーグルト", "納豆", "豆腐", "チーズ", "ささみ"
]

VEGETABLE_WORDS = [
    "野菜", "サラダ", "ブロッコリー", "スプラウト", "ビーツ", "アボカド",
    "トマト", "キャベツ", "レタス", "にんじん", "玉ねぎ", "きのこ"
]

CARB_WORDS = [
    "ご飯", "米", "パン", "麺", "うどん", "そば", "パスタ",
    "じゃがいも", "さつまいも", "バナナ"
]

FAT_WORDS = [
    "油", "アマニ油", "亜麻仁油", "マヨネーズ", "バター",
    "チーズ", "アボカド", "ナッツ", "揚げ"
]

SWEET_WORDS = [
    "アイス", "お菓子", "チョコ", "ケーキ", "ジュース", "ゼリー",
    "キャラメル", "ポップコーン"
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def contains_any(text, words):
    return sum(1 for w in words if w in text)


def score_meals(text):
    protein = min(100, contains_any(text, PROTEIN_WORDS) * 25)
    vegetable = min(100, contains_any(text, VEGETABLE_WORDS) * 25)
    carb = min(100, contains_any(text, CARB_WORDS) * 30)
    fat = min(100, contains_any(text, FAT_WORDS) * 35)

    sweet_count = contains_any(text, SWEET_WORDS)

    if sweet_count >= 2:
        sweet_score = 40
    elif sweet_count == 1:
        sweet_score = 70
    else:
        sweet_score = 100

    total = int((protein + vegetable + carb + fat + sweet_score) / 5)

    if total >= 85:
        rank = "S"
        comment = "かなり良いバランス！この調子でいこう。"
    elif total >= 70:
        rank = "A"
        comment = "いい感じ。あと少し整えるとさらに良い。"
    elif total >= 55:
        rank = "B"
        comment = "悪くないけど、少し偏りがあるかも。"
    else:
        rank = "C"
        comment = "今日は少し整える意識を持つと良さそう。"

    advice = []

    if protein < 60:
        advice.append("たんぱく質をもう1品足すと良さそう。卵・魚・鶏肉・豆腐・プロテインなど。")

    if vegetable < 60:
        advice.append("野菜・きのこ・海藻系を少し足すとバランスが良くなるよ。")

    if carb < 40:
        advice.append("活動量が多い日なら、炭水化物も少し入れてOK。")

    if fat > 80:
        advice.append("脂質はやや多めかも。揚げ物や油の重なりに注意。")

    if sweet_score < 100:
        advice.append("甘いものは食べてもOK。量とタイミングだけ意識しよう。")

    if not advice:
        advice.append("全体的にかなり整ってるよ。無理なく続けよう。")

    return {
        "protein": protein,
        "vegetable": vegetable,
        "carb": carb,
        "fat": fat,
        "sweet_score": sweet_score,
        "total": total,
        "rank": rank,
        "comment": comment,
        "advice": advice,
    }


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "breakfast": x["breakfast"],
            "lunch": x["lunch"],
            "dinner": x["dinner"],
            "snack": x.get("snack", ""),
            "protein": x["scores"]["protein"],
            "vegetable": x["scores"]["vegetable"],
            "carb": x["scores"]["carb"],
            "fat": x["scores"]["fat"],
            "sweet_score": x["scores"]["sweet_score"],
            "total": x["scores"]["total"],
            "rank": x["scores"]["rank"],
            "memo": x.get("memo", ""),
        })

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
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Day172：栄養バランスチェッカー")
st.caption("朝昼晩と間食を入力して、たんぱく質・野菜・炭水化物・脂質のバランスを簡易チェックするアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の食事を入力")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    breakfast = st.text_area(
        "朝食",
        height=90,
        placeholder="例：スムージー、ヨーグルト、プロテイン"
    )

    lunch = st.text_area(
        "昼食",
        height=90,
        placeholder="例：牛丼ライト、サラダチキン、ゆで卵"
    )

    dinner = st.text_area(
        "夕食",
        height=90,
        placeholder="例：シチュー、パン、白身魚"
    )

    snack = st.text_area(
        "間食",
        height=70,
        placeholder="例：ゼリー、アイス、ナッツ"
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：今日は筋トレあり / 少し食べすぎた"
    )

    if st.button("🥗 チェックする", type="primary"):
        all_text = "\n".join([breakfast, lunch, dinner, snack])
        scores = score_meals(all_text)

        item = {
            "id": f"nutrition_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": log_date.isoformat(),
            "breakfast": breakfast.strip(),
            "lunch": lunch.strip(),
            "dinner": dinner.strip(),
            "snack": snack.strip(),
            "memo": memo.strip(),
            "scores": scores,
        }

        data["logs"].append(item)
        save_data(data)

        st.session_state["latest"] = item
        st.success("栄養バランスを記録したよ。")
        st.rerun()

with right:
    st.subheader("判定結果")

    latest = st.session_state.get("latest")

    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        scores = latest["scores"]

        st.metric("総合点", f"{scores['total']}点")
        st.metric("ランク", scores["rank"])

        st.success(scores["comment"])

        st.divider()

        st.write("🥩 たんぱく質")
        st.progress(scores["protein"] / 100)
        st.write(f"{scores['protein']}点")

        st.write("🥦 野菜")
        st.progress(scores["vegetable"] / 100)
        st.write(f"{scores['vegetable']}点")

        st.write("🍚 炭水化物")
        st.progress(scores["carb"] / 100)
        st.write(f"{scores['carb']}点")

        st.write("🧈 脂質")
        st.progress(scores["fat"] / 100)
        st.write(f"{scores['fat']}点")

        st.write("🍰 甘いものバランス")
        st.progress(scores["sweet_score"] / 100)
        st.write(f"{scores['sweet_score']}点")

        st.divider()
        st.subheader("アドバイス")

        for adv in scores["advice"]:
            st.info(adv)

    else:
        st.info("まだ記録がないよ。")

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("記録数", len(df))

    with c2:
        st.metric("平均点", f"{int(df['total'].mean())}点")

    with c3:
        st.metric("最高点", f"{int(df['total'].max())}点")

    st.dataframe(
        df[[
            "date",
            "rank",
            "total",
            "protein",
            "vegetable",
            "carb",
            "fat",
            "sweet_score",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細")

    selected_id = st.selectbox(
        "記録を選ぶ",
        df["id"].tolist(),
        format_func=lambda x: f"{find_log(data, x)['date']} / {find_log(data, x)['scores']['rank']} / {find_log(data, x)['scores']['total']}点"
    )

    selected = find_log(data, selected_id)

    if selected:
        st.markdown(f"## {selected['date']} の食事")

        st.markdown("### 朝食")
        st.write(selected["breakfast"])

        st.markdown("### 昼食")
        st.write(selected["lunch"])

        st.markdown("### 夕食")
        st.write(selected["dinner"])

        if selected.get("snack"):
            st.markdown("### 間食")
            st.write(selected["snack"])

        if selected.get("memo"):
            st.info(selected["memo"])

        if st.button("🗑️ この記録を削除", type="secondary"):
            data["logs"] = [x for x in data["logs"] if x["id"] != selected_id]
            save_data(data)
            st.warning("削除したよ。")
            st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day172_nutrition_checker.csv",
        mime="text/csv"
    )
