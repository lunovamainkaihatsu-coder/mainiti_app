
import streamlit as st
import json, os, uuid
from datetime import date

st.set_page_config(page_title="未来の自分に1問", page_icon="📮")

FILE = "data/questions.json"
os.makedirs("data", exist_ok=True)

CATEGORIES = [
    "🌱 自分","💼 仕事","🤖 AI・開発",
    "📚 勉強","🎨 創作","💰 お金",
    "👨‍👩‍👧 家族","🌈 未来","✨ その他"
]

MOODS = ["😄 ワクワク","🙂 良い","🤔 不安","😐 普通","😢 落ち込み"]

def load():
    if not os.path.exists(FILE):
        with open(FILE,"w",encoding="utf-8") as f:
            json.dump({"questions":[]},f)
    with open(FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

data = load()

st.title("📮 未来の自分に1問")
st.caption("今日の問いを、未来の自分へ届けよう。")

today = str(date.today())

# ---------- 集計 ----------
waiting = [q for q in data["questions"] if q["answer"]==""]
ready = [q for q in waiting if q["answer_date"]<=today]
done = [q for q in data["questions"] if q["answer"]!=""]

c1,c2,c3 = st.columns(3)
c1.metric("📬 回答待ち", len(waiting))
c2.metric("🔥 今日答える", len(ready))
c3.metric("✅ 回答済み", len(done))

st.divider()

# ---------- 新規作成 ----------
st.subheader("✍️ 未来へ質問する")

with st.form("new"):
    q = st.text_area("質問")
    predict = st.text_area("今の自分の予想")
    col1,col2 = st.columns(2)
    with col1:
        cat = st.selectbox("カテゴリー", CATEGORIES)
        mood = st.selectbox("今の気持ち", MOODS)
    with col2:
        answer_day = st.date_input("回答する日", value=date.today())

    ok = st.form_submit_button("📮 送る")

    if ok and q.strip():
        data["questions"].append({
            "id": str(uuid.uuid4()),
            "question": q,
            "prediction": predict,
            "category": cat,
            "mood": mood,
            "created": today,
            "answer_date": str(answer_day),
            "answer": "",
            "favorite": False
        })
        save(data)
        st.success("未来へ質問を送りました！")
        st.rerun()

st.divider()

# ---------- 今日答える ----------
st.subheader("📬 今日届いた質問")

if not ready:
    st.info("今日は届いた質問はありません✨")

for item in ready:
    with st.container(border=True):
        st.markdown(f"### {item['category']}")
        st.write(f"**質問**：{item['question']}")
        st.write(f"**当時の予想**：{item['prediction']}")
        st.caption(f"当時の気持ち：{item['mood']}")

        ans = st.text_area(
            "未来の自分の回答",
            key=item["id"]
        )

        if st.button("✅ 回答する", key="a"+item["id"]):
            item["answer"] = ans
            save(data)
            st.success("回答を保存しました！")
            st.rerun()

st.divider()

# ---------- ランダム ----------
st.subheader("🎲 昔の自分から1問")

if done:
    import random
    if st.button("質問をひらく"):
        st.session_state["random"] = random.choice(done)["id"]

    rid = st.session_state.get("random")
    if rid:
        obj = next(x for x in done if x["id"]==rid)
        st.markdown(f"### {obj['category']}")
        st.write(f"**質問**：{obj['question']}")
        st.write(f"**予想**：{obj['prediction']}")
        st.write(f"**回答**：{obj['answer']}")
else:
    st.caption("回答済みが増えると遊べます。")

st.divider()

# ---------- 履歴 ----------
st.subheader("📚 すべての質問")

for item in sorted(data["questions"], key=lambda x:x["created"], reverse=True):
    with st.expander(f"{item['category']}  {item['question'][:30]}"):
        st.write(f"**質問**：{item['question']}")
        st.write(f"**予想**：{item['prediction']}")
        st.write(f"**回答予定**：{item['answer_date']}")

        if item["answer"]:
            st.success("回答済み")
            st.write(f"**回答**：{item['answer']}")
        else:
            st.warning("未回答")

        if st.button("🗑️ 削除", key="d"+item["id"]):
            data["questions"] = [
                q for q in data["questions"]
                if q["id"] != item["id"]
            ]
            save(data)
            st.rerun()

st.divider()

st.download_button(
    "💾 JSONバックアップ",
    data=json.dumps(data,ensure_ascii=False,indent=2),
    file_name="future_questions.json",
    mime="application/json"
)
