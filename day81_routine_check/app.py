import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Routine Check", layout="centered")

FILE = "routine.json"


# -------------------------
# 読み込み
# -------------------------
def load_data():
    if not os.path.exists(FILE):
        return {"routines": [], "checked": {}}

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"routines": [], "checked": {}}


# -------------------------
# 保存
# -------------------------
def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()

today = datetime.now().strftime("%Y-%m-%d")

if today not in data["checked"]:
    data["checked"][today] = {}

st.title("✅ Routine Check")
st.caption("今日の積み重ねが未来を作る。")

st.divider()

# -------------------------
# ルーティン表示
# -------------------------

st.subheader("今日のルーティン")

completed = 0

for routine in data["routines"]:

    checked = data["checked"][today].get(routine, False)

    result = st.checkbox(
        routine,
        value=checked,
        key=routine
    )

    data["checked"][today][routine] = result

    if result:
        completed += 1

save_data(data)


# -------------------------
# 達成率
# -------------------------

total = len(data["routines"])

if total > 0:
    percent = int((completed / total) * 100)
else:
    percent = 0

st.divider()

st.subheader("達成率")

st.progress(percent / 100)

st.write(f"{completed} / {total} 完了 ({percent}%)")


# -------------------------
# 追加
# -------------------------

st.divider()

st.subheader("ルーティン追加")

new_routine = st.text_input("新しいルーティン")

if st.button("追加"):

    if new_routine and new_routine not in data["routines"]:
        data["routines"].append(new_routine)
        save_data(data)
        st.rerun()


# -------------------------
# 削除
# -------------------------

st.subheader("ルーティン削除")

delete = st.selectbox("削除する項目", [""] + data["routines"])

if st.button("削除"):

    if delete in data["routines"]:
        data["routines"].remove(delete)

        for date in data["checked"]:
            if delete in data["checked"][date]:
                del data["checked"][date][delete]

        save_data(data)
        st.rerun()


st.divider()

st.caption("Day81 Routine Check")
