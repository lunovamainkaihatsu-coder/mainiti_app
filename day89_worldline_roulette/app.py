import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day89：世界線ルーレット（未来分岐メーカー）"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day89_worldline.json")

RARITIES = [
    ("N", 0.55),
    ("R", 0.27),
    ("SR", 0.13),
    ("SSR", 0.05),
]

# 世界線テンプレ（モード別）
WORLDLINES = {
    "攻め": [
        "朝の集中が冴え、作ったものが一気に形になる世界線。",
        "偶然の連絡がきっかけで、次のチャンスが繋がる世界線。",
        "今日の一手が“雪だるま”になって、明日が楽になる世界線。",
        "強気の一歩が、未来の自分に拍手される世界線。",
        "やる気が火種から炎になり、周囲も巻き込む世界線。",
    ],
    "守り": [
        "無理をしない判断が功を奏し、静かに整う世界線。",
        "小さな前進が積み重なり、安心が戻ってくる世界線。",
        "片付けた分だけ心が軽くなり、流れが戻る世界線。",
        "自分を責めずに淡々と進め、結果だけが残る世界線。",
        "“できることだけ”が最高の選択になった世界線。",
    ],
    "回復": [
        "休むことを選んだことで、翌日から反転する世界線。",
        "身体が整い、心のノイズが消えていく世界線。",
        "優しい時間が増え、人生の土台が強くなる世界線。",
        "小さな呼吸と水分補給が、未来の火を守る世界線。",
        "今日を“回復の日”と認めた瞬間、罪悪感が消える世界線。",
    ],
}

# 1アクション（モード別）
ACTIONS = {
    "攻め": [
        "開発：25分だけコードを書く（1ファイル触る）",
        "発信：Noteのタイトル案を10個出す",
        "学習：Streamlitの小技を1つ試す",
        "整理：次のアプリの仕様を箇条書きで3つ決める",
        "営業/仕事：連絡1件だけ送る（短くでOK）",
    ],
    "守り": [
        "片付け：机の上を5分だけ整える",
        "発信：一言だけ日記orポストを書く",
        "開発：バグ1つだけ直す/コメント入れる",
        "学習：10分だけ読む/見る",
        "回復：ストレッチ＋水分補給",
    ],
    "回復": [
        "回復：10分横になる（スマホ見ない）",
        "回復：温かい飲み物＋深呼吸30秒",
        "超軽：メモ1行だけ残す（今日の気分）",
        "家族：家族対応を“今日の最優先”として認める",
        "整え：明日の朝やることを1行だけ書く",
    ],
}

TITLES = [
    "星屑の作業机", "静かな加速", "未来の鍵穴", "月光の一手", "反転の兆し",
    "運命の余白", "火種の回路", "白い静寂", "確定した予感", "銀河のメモ"
]

EMOJIS = ["🌙", "✨", "🗝️", "🎲", "🪐", "🔥", "🍀", "📌", "⚡", "🌌"]


# ---------- storage ----------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"rolls": []}, f, ensure_ascii=False, indent=2)


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


def pick_rarity():
    r = random.random()
    acc = 0.0
    for name, p in RARITIES:
        acc += p
        if r <= acc:
            return name
    return "N"


def rarity_color(r):
    # Streamlitは色指定できないので表示テキストで演出
    return {"N": "N", "R": "R", "SR": "SR", "SSR": "SSR"}.get(r, "N")


def roll_worldline(mode: str):
    rarity = pick_rarity()
    title = random.choice(TITLES)
    emoji = random.choice(EMOJIS)
    story = random.choice(WORLDLINES[mode])

    # レア度に応じて少しだけ盛る
    if rarity == "R":
        story += " しかも、偶然が味方をする。"
    elif rarity == "SR":
        story += " 直感が冴えて、選ぶ言葉が刺さる。"
    elif rarity == "SSR":
        story += " そして“流れ”が確定する。世界が静かに動く。"

    action = random.choice(ACTIONS[mode])

    card = {
        "id": f"{date.today().isoformat()}_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mode": mode,
        "rarity": rarity,
        "title": f"{emoji} {title}",
        "story": story,
        "action": action,
        "favorite": False,
    }
    return card


def to_df(data):
    rows = []
    for r in data["rolls"]:
        rows.append({
            "created_at": r.get("created_at"),
            "mode": r.get("mode"),
            "rarity": r.get("rarity"),
            "title": r.get("title"),
            "action": r.get("action"),
            "favorite": bool(r.get("favorite", False)),
            "id": r.get("id"),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="🎲", layout="wide")
st.title("🎲 Day89：世界線ルーレット（未来分岐メーカー）")
st.caption("いまの状態から、未来の“分岐”を引く。遊びながら、今日の一手も受け取る。")

data = load_data()

# セッション：直近のカード
if "last_card" not in st.session_state:
    st.session_state.last_card = None

left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("🔮 ルーレットを回す")

    mode = st.radio("いまのモードを選んでね", ["攻め", "守り", "回復"], horizontal=True)

    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        if st.button("🎲 回す！", type="primary"):
            card = roll_worldline(mode)
            data["rolls"].append(card)
            save_data(data)
            st.session_state.last_card = card
            st.rerun()

    with c2:
        if st.button("🧹 履歴を全部消す", type="secondary"):
            data["rolls"] = []
            save_data(data)
            st.session_state.last_card = None
            st.warning("履歴を全部消したよ。")
            st.rerun()

    st.divider()
    st.subheader("🃏 今回の世界線カード")

    card = st.session_state.last_card
    if card is None:
        st.info("まだ回してないよ。上の「回す！」を押してね。")
    else:
        st.markdown(f"### {card['title']}")
        st.markdown(f"- モード：**{card['mode']}**")
        st.markdown(f"- レア度：**{rarity_color(card['rarity'])}**")
        st.markdown("**未来の一文**")
        st.write(card["story"])
        st.markdown("**今日の1アクション**")
        st.success(card["action"])

        fav = st.checkbox("⭐ お気に入りにする", value=bool(card.get("favorite", False)))
        if fav != bool(card.get("favorite", False)):
            # 最新カードを更新
            card["favorite"] = fav
            # 保存データ側も更新
            for r in data["rolls"]:
                if r.get("id") == card.get("id"):
                    r["favorite"] = fav
                    break
            save_data(data)
            st.toast("お気に入り更新！")

with right:
    st.subheader("📚 図鑑（履歴）")
    df = to_df(data)
    if df.empty:
        st.write("履歴がまだないよ。")
    else:
        show_fav_only = st.checkbox("⭐ お気に入りだけ表示", value=False)
        view = df.copy()
        if show_fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(view[["created_at", "mode", "rarity", "title", "action", "favorite"]], use_container_width=True, height=360)

        st.divider()
        st.subheader("🔎 詳細を見る")
        pick_id = st.selectbox("カードを選ぶ", options=view["id"].tolist())
        chosen = None
        for r in data["rolls"]:
            if r.get("id") == pick_id:
                chosen = r
                break
        if chosen:
            st.markdown(f"### {chosen['title']}")
            st.write(f"作成：{chosen['created_at']} / レア度：{chosen['rarity']} / モード：{chosen['mode']}")
            st.write("**未来の一文**")
            st.write(chosen["story"])
            st.write("**今日の1アクション**")
            st.success(chosen["action"])

        st.divider()
        st.subheader("📦 エクスポート")
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSVダウンロード", data=csv, file_name="day89_worldline.csv", mime="text/csv")
