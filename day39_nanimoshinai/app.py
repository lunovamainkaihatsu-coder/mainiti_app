import streamlit as st

st.set_page_config(
    page_title="今日は何もしない宣言",
    layout="centered"
)

st.markdown(
    """
    <style>
    body {
        background-color: #0f1117;
        color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("今日は何もしない宣言")

st.write("")
st.write("何もしない日があっても、問題ありません。")
st.write("理由も、成果も、記録もいりません。")
st.write("")

if "declared" not in st.session_state:
    st.session_state.declared = False

if not st.session_state.declared:
    if st.button("今日は何もしません"):
        st.session_state.declared = True
        st.rerun()
else:
    st.write("")
    st.write("了解しました。")
    st.write("今日は、何もしなくて大丈夫です。")
