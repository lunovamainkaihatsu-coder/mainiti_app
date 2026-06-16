import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day171：あるもので献立メーカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day171_meal_idea_maker.json")

CATEGORIES = [
    "ご飯もの",
    "麺",
    "炒め物",
    "汁物",
    "副菜",
    "たんぱく質",
    "簡単",
]

MEAL_RULES = [
    {
        "name": "納豆卵ご飯",
        "category": "ご飯もの",
        "needs": ["納豆", "卵", "ご飯"],
        "optional": ["ねぎ", "のり", "しょうゆ"],
        "memo": "混ぜるだけで早い。朝食にも夜食にも使える。",
    },
    {
        "name": "親子丼風",
        "category": "ご飯もの",
        "needs": ["鶏", "卵", "ご飯"],
        "optional": ["玉ねぎ", "めんつゆ"],
        "memo": "鶏肉と卵があれば丼にしやすい。",
    },
    {
        "name": "肉じゃが風",
        "category": "ご飯もの",
        "needs": ["肉", "じゃがいも"],
        "optional": ["にんじん", "玉ねぎ", "しょうゆ"],
        "memo": "じゃがいもと肉があれば、それっぽく作れる。",
    },
    {
        "name": "野菜炒め",
        "category": "炒め物",
        "needs": ["野菜"],
        "optional": ["肉", "卵", "もやし"],
        "memo": "余った野菜をまとめて使える万能メニュー。",
    },
    {
        "name": "鶏むね野菜炒め",
        "category": "炒め物",
        "needs": ["鶏", "野菜"],
        "optional": ["にんにく", "しょうゆ", "ごま油"],
        "memo": "たんぱく質を取りたい日に良い。",
    },
    {
        "name": "卵スープ",
        "category": "汁物",
        "needs": ["卵"],
        "optional": ["ねぎ", "わかめ", "鶏ガラ"],
        "memo": "卵だけでも作りやすい軽い汁物。",
    },
    {
        "name": "味噌汁",
        "category": "汁物",
        "needs": ["味噌"],
        "optional": ["豆腐", "わかめ", "ねぎ", "じゃがいも"],
        "memo": "具材を変えれば毎日使える。",
    },
    {
        "name": "豆腐サラダ",
        "category": "副菜",
        "needs": ["豆腐"],
        "optional": ["レタス", "トマト", "わかめ"],
        "memo": "火を使わずに作れる軽い一品。",
    },
    {
        "name": "ツナマヨご飯",
        "category": "ご飯もの",
        "needs": ["ツナ", "ご飯"],
        "optional": ["マヨネーズ", "のり", "しょうゆ"],
        "memo": "時間がない時の簡単ご飯。",
    },
    {
        "name": "焼きそば風",
        "category": "麺",
        "needs": ["麺"],
        "optional": ["肉", "キャベツ", "もやし"],
        "memo": "麺と余り野菜で作れる。",
    },
    {
        "name": "うどん",
        "category": "麺",
        "needs": ["うどん"],
        "optional": ["卵", "ねぎ", "わかめ", "めんつゆ"],
        "memo": "体調が微妙な日にも食べやすい。",
    },
    {
        "name": "卵焼き",
        "category": "たんぱく質",
        "needs": ["卵"],
        "optional": ["ねぎ", "チーズ", "のり"],
        "memo": "あと一品に便利。",
    },
    {
        "name": "チーズオムレツ",
        "category": "たんぱく質",
        "needs": ["卵", "チーズ"],
        "optional": ["牛乳", "ハム"],
        "memo": "卵とチーズで満足感が出る。",
    },
    {
        "name": "バナナヨーグルト",
        "category": "簡単",
        "needs": ["バナナ", "ヨーグルト"],
        "optional": ["はちみつ", "プロテイン"],
        "memo": "朝食や間食に使える。",
    },
    {
        "name": "プロテインスムージー",
        "category": "簡単",
        "needs": ["プロテイン"],
        "optional": ["バナナ", "アボカド", "ヨーグルト", "ビーツ"],
        "memo": "ご主人の定番にも合う健康系メニュー。",
    },
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": [], "favorites": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    if "favorites" not in data:
        data["favorites"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def normalize_words(text):
    words = []

    for line in text.replace("、", "\n").replace(",", "\n").splitlines():
        w = line.strip()
        if w:
            words.append(w)

    return words


def match_score(ingredients, rule):
    matched_needs = []
    missing_needs = []
    matched_optional = []

    joined = " ".join(ingredients)

    for need in rule["needs"]:
        if need in joined:
            matched_needs.append(need)
        else:
            missing_needs.append(need)

    for opt in rule["optional"]:
        if opt in joined:
            matched_optional.append(opt)

    need_count = len(rule["needs"])
    score = len(matched_needs) * 10 + len(matched_optional) * 2

    if need_count > 0 and len(matched_needs) == need_count:
        score += 20

    return {
        "score": score,
        "matched_needs": matched_needs,
        "missing_needs": missing_needs,
        "matched_optional": matched_optional,
    }


def suggest_meals(ingredients, category_filter="すべて"):
    results = []

    for rule in MEAL_RULES:
        if category_filter != "すべて" and rule["category"] != category_filter:
            continue

        result = match_score(ingredients, rule)

        if result["score"] > 0:
            results.append({
                "name": rule["name"],
                "category": rule["category"],
                "needs": "、".join(rule["needs"]),
                "optional": "、".join(rule["optional"]),
                "matched": "、".join(result["matched_needs"] + result["matched_optional"]),
                "missing": "、".join(result["missing_needs"]),
                "score": result["score"],
                "memo": rule["memo"],
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "ingredients": x["ingredients"],
            "selected_meal": x.get("selected_meal", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🍳",
    layout="wide"
)

st.title("🍳 Day171：あるもので献立メーカー")
st.caption("冷蔵庫にある食材から、作れそうな料理を提案するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("食材を入力")

    ingredients_text = st.text_area(
        "今ある食材",
        height=180,
        placeholder="例：\n卵\n納豆\nご飯\n鶏むね肉\n玉ねぎ"
    )

    category_filter = st.selectbox(
        "料理カテゴリ",
        ["すべて"] + CATEGORIES
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：今日は軽めがいい / たんぱく質多め"
    )

    ingredients = normalize_words(ingredients_text)

    if st.button("🍳 献立を提案", type="primary"):
        if not ingredients:
            st.warning("食材を1つ以上入れてね。")
        else:
            suggestions = suggest_meals(ingredients, category_filter)

            st.session_state["ingredients"] = ingredients
            st.session_state["suggestions"] = suggestions
            st.session_state["memo"] = memo.strip()

            st.rerun()

with right:
    st.subheader("提案結果")

    suggestions = st.session_state.get("suggestions", [])
    ingredients = st.session_state.get("ingredients", [])

    if not suggestions:
        st.info("食材を入力して、献立を提案してみよう。")
    else:
        st.write("入力食材：")
        st.success("、".join(ingredients))

        df_suggest = pd.DataFrame(suggestions)

        st.dataframe(
            df_suggest[["name", "category", "score", "matched", "missing", "memo"]],
            use_container_width=True,
            height=300
        )

        meal_options = [x["name"] for x in suggestions]

        selected_meal = st.selectbox(
            "今日作るなら？",
            meal_options
        )

        selected = next((x for x in suggestions if x["name"] == selected_meal), None)

        if selected:
            st.markdown(f"## {selected['name']}")
            st.write(f"カテゴリ：{selected['category']}")
            st.write(f"使えそうな食材：{selected['matched']}")

            if selected["missing"]:
                st.warning(f"足りないかも：{selected['missing']}")
            else:
                st.success("必要食材はだいたい揃ってる！")

            st.info(selected["memo"])

        if st.button("🍽️ この献立を保存"):
            item = {
                "id": f"meal_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "ingredients": "、".join(ingredients),
                "selected_meal": selected_meal,
                "memo": st.session_state.get("memo", ""),
            }

            data["logs"].append(item)
            save_data(data)

            st.success("献立を保存したよ。")
            st.rerun()

st.divider()
st.subheader("献立履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df[["date", "ingredients", "selected_meal", "memo"]],
        use_container_width=True,
        height=300
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day171_meal_idea_maker.csv",
        mime="text/csv"
    )
