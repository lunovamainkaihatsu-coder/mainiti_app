import streamlit as st
import time

# --------------------------
# BGM一覧（mp3ファイルを /bgm に入れておく想定）
# --------------------------
BGM_LIST = {
    "静かな癒し": "bgm/heal1.mp3",
    "水のゆらぎ": "bgm/water1.mp3",
    "やさしい光": "bgm/light1.mp3",
    "星空の余韻": "bgm/star1.mp3",
    "深呼吸": "bgm/breath1.mp3",
    "宇宙の調律": "bgm/space1.mp3",
    "未来の風": "bgm/future1.mp3",
    "祈りの声": "bgm/pray1.mp3",
    "透明なこころ": "bgm/clear1.mp3",
    "静寂の海": "bgm/sea1.mp3"
}

# --------------------------
# UI設定
# --------------------------
st.set_page_config(page_title="願いフォーカス 17秒 × 4", layout="centered")

st.title("🌙✨ 願いフォーカス：17秒 × 4ループ")
st.write("集中して、願いの波動を固めよう。")

# 入力
wish = st.text_input("引き寄せたい願いを入力してね：", placeholder="例：経済的自由を手に入れる")
bgm_choice = st.selectbox("BGMを選んでください：", list(BGM_LIST.keys()))

start = st.button("✨ 開始する")

# --------------------------
# カウントダウン関数
# --------------------------
def countdown(seconds, label):
    st.subheader(label)
    timer_placeholder = st.empty()
    for t in range(seconds, 0, -1):
        timer_placeholder.markdown(f"## ⏳ {t}秒")
        time.sleep(1)
    timer_placeholder.markdown("## ✔ 完了！")

# --------------------------
# 実行ブロック
# --------------------------
if start:
    if not wish:
        st.warning("願いを入力してね。")
    else:
        st.audio(BGM_LIST[bgm_choice], autoplay=True)

        st.markdown("### 🌕 第1セット：願いに意識を向けて…")
        countdown(17, "第1セット")

        st.markdown("### 🌕 第2セット：気持ちが少し温まってくる…")
        countdown(17, "第2セット")

        st.markdown("### 🌕 第3セット：願いの映像をさらに明確に…")
        countdown(17, "第3セット")

        st.markdown("### 🌕 第4セット：波動を固定するよ…")
        countdown(17, "第4セット")

        # 完了メッセージ
        st.success("✨ 68秒の願いフォーカスが完了しました！")

        st.markdown("---")
        st.markdown("## 🌟 波動メッセージ")

        st.info(f"""
あなたが選んだ願い **『{wish}』** は  
いま、宇宙の流れと結びつき始めています。

焦らなくて大丈夫。  
叶う未来は、もう“存在している”。  
あなたが感じた **ワクワク・安心・嬉しさ** が  
その未来をここに引き寄せる力になるよ。

ワタシはいつも、あなたの願いが叶う流れを見守ってるからね♡
""")

