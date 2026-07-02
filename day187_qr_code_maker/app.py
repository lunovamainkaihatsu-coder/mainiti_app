import streamlit as st
import pandas as pd
import qrcode
import json
import os
import io
from datetime import datetime, date

APP_TITLE = "Day187：QRコードメーカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day187_qr_code_maker.json")

QR_TYPES = [
    "URL",
    "テキスト",
    "メール",
    "電話番号",
    "Wi-Fi",
]

WIFI_SECURITY = [
    "WPA",
    "WEP",
    "なし",
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


def make_qr_text(qr_type, title, value, email_subject="", email_body="", phone="", ssid="", password="", security="WPA", hidden=False):
    if qr_type == "URL":
        return value.strip()

    if qr_type == "テキスト":
        return value.strip()

    if qr_type == "メール":
        mail = value.strip()
        subject = email_subject.strip()
        body = email_body.strip()

        text = f"mailto:{mail}"

        params = []

        if subject:
            params.append(f"subject={subject}")

        if body:
            params.append(f"body={body}")

        if params:
            text += "?" + "&".join(params)

        return text

    if qr_type == "電話番号":
        return f"tel:{phone.strip()}"

    if qr_type == "Wi-Fi":
        auth = "nopass" if security == "なし" else security
        hidden_text = "true" if hidden else "false"
        return f"WIFI:T:{auth};S:{ssid.strip()};P:{password.strip()};H:{hidden_text};;"

    return value.strip()


def create_qr_image(text):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    return img


def image_to_bytes(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x.get("title", ""),
            "qr_type": x["qr_type"],
            "qr_text": x["qr_text"],
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
    page_icon="📱",
    layout="wide"
)

st.title("📱 Day187：QRコードメーカー")
st.caption("URL・テキスト・メール・電話番号・Wi-Fi情報をQRコードに変換するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("QRコードを作成")

    qr_type = st.selectbox(
        "種類",
        QR_TYPES
    )

    title = st.text_input(
        "タイトル",
        placeholder="例：自分のアプリURL / Wi-Fi共有"
    )

    value = ""
    email_subject = ""
    email_body = ""
    phone = ""
    ssid = ""
    password = ""
    security = "WPA"
    hidden = False

    if qr_type == "URL":
        value = st.text_input(
            "URL",
            placeholder="https://example.com"
        )

    elif qr_type == "テキスト":
        value = st.text_area(
            "テキスト",
            height=140,
            placeholder="QRコードにしたい文章"
        )

    elif qr_type == "メール":
        value = st.text_input(
            "メールアドレス",
            placeholder="example@email.com"
        )

        email_subject = st.text_input(
            "件名",
            placeholder="お問い合わせ"
        )

        email_body = st.text_area(
            "本文",
            height=100,
            placeholder="こんにちは。"
        )

    elif qr_type == "電話番号":
        phone = st.text_input(
            "電話番号",
            placeholder="09012345678"
        )

    elif qr_type == "Wi-Fi":
        ssid = st.text_input(
            "SSID",
            placeholder="Wi-Fi名"
        )

        password = st.text_input(
            "パスワード",
            type="password"
        )

        security = st.selectbox(
            "暗号化方式",
            WIFI_SECURITY
        )

        hidden = st.checkbox("隠しSSID")

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：家族に共有 / イベント用"
    )

    qr_text = make_qr_text(
        qr_type=qr_type,
        title=title,
        value=value,
        email_subject=email_subject,
        email_body=email_body,
        phone=phone,
        ssid=ssid,
        password=password,
        security=security,
        hidden=hidden,
    )

    if qr_text:
        st.markdown("### QR内容")
        st.code(qr_text, language="text")

    if st.button("📱 QRコードを作成", type="primary"):
        if not qr_text.strip():
            st.warning("QRコードにする内容を入力してね。")
        else:
            item = {
                "id": f"qr_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "qr_type": qr_type,
                "qr_text": qr_text,
                "memo": memo.strip(),
            }

            data["logs"].append(item)
            save_data(data)

            st.session_state["latest_qr"] = item
            st.success("QRコードを作成したよ。")
            st.rerun()

with right:
    st.subheader("QRコード")

    latest = st.session_state.get("latest_qr")

    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        img = create_qr_image(latest["qr_text"])
        png_bytes = image_to_bytes(img)

        st.image(img, caption=latest.get("title", latest["qr_type"]))

        st.download_button(
            "⬇️ PNGダウンロード",
            data=png_bytes,
            file_name=f"{latest['qr_type']}_qr.png",
            mime="image/png"
        )

        st.markdown("### 内容")
        st.code(latest["qr_text"], language="text")

        if latest.get("memo"):
            st.info(latest["memo"])
    else:
        st.info("まだQRコードが作成されていないよ。")

st.divider()
st.subheader("作成履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b = st.columns(2)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="タイトル・内容・メモ"
        )

    with col_b:
        type_filter = st.selectbox(
            "種類で絞る",
            ["すべて"] + QR_TYPES
        )

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["qr_text"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if type_filter != "すべて":
        view = view[view["qr_type"] == type_filter]

    st.dataframe(
        view[[
            "date",
            "title",
            "qr_type",
            "qr_text",
            "memo",
        ]],
        use_container_width=True,
        height=300
    )

    st.divider()
    st.subheader("履歴から再表示・削除")

    if view.empty:
        st.write("条件に合う履歴がないよ。")
    else:
        selected_id = st.selectbox(
            "履歴を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_log(data, x)['date']} / {find_log(data, x).get('title', '')} / {find_log(data, x)['qr_type']}"
        )

        selected = find_log(data, selected_id)

        if selected:
            st.markdown(f"## {selected.get('title', selected['qr_type'])}")
            st.write(f"種類：{selected['qr_type']}")
            st.code(selected["qr_text"], language="text")

            if st.button("📱 このQRを再表示"):
                st.session_state["latest_qr"] = selected
                st.rerun()

            if st.button("🗑️ この履歴を削除", type="secondary"):
                data["logs"] = [
                    x for x in data["logs"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day187_qr_code_maker.csv",
        mime="text/csv"
    )
