import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day188：ファイル名一括リネーマー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day188_bulk_file_renamer.json")

MODES = [
    "接頭辞・接尾辞追加",
    "文字置換",
    "連番リネーム",
]

TARGET_EXTENSIONS = [
    "すべて",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".txt",
    ".csv",
    ".py",
    ".md",
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


def list_files(folder_path, target_ext):
    if not os.path.isdir(folder_path):
        return []

    files = []

    for name in os.listdir(folder_path):
        path = os.path.join(folder_path, name)

        if os.path.isfile(path):
            base, ext = os.path.splitext(name)

            if target_ext == "すべて" or ext.lower() == target_ext.lower():
                files.append(name)

    return sorted(files)


def make_new_name(
    old_name,
    mode,
    prefix,
    suffix,
    replace_from,
    replace_to,
    serial_base,
    serial_start,
    serial_digits,
    index
):
    base, ext = os.path.splitext(old_name)

    if mode == "接頭辞・接尾辞追加":
        return f"{prefix}{base}{suffix}{ext}"

    if mode == "文字置換":
        new_base = base.replace(replace_from, replace_to)
        return f"{new_base}{ext}"

    if mode == "連番リネーム":
        number = serial_start + index
        return f"{serial_base}_{str(number).zfill(serial_digits)}{ext}"

    return old_name


def make_preview(
    folder_path,
    files,
    mode,
    prefix,
    suffix,
    replace_from,
    replace_to,
    serial_base,
    serial_start,
    serial_digits
):
    rows = []

    for i, old_name in enumerate(files):
        new_name = make_new_name(
            old_name=old_name,
            mode=mode,
            prefix=prefix,
            suffix=suffix,
            replace_from=replace_from,
            replace_to=replace_to,
            serial_base=serial_base,
            serial_start=serial_start,
            serial_digits=serial_digits,
            index=i
        )

        rows.append({
            "old_name": old_name,
            "new_name": new_name,
            "old_path": os.path.join(folder_path, old_name),
            "new_path": os.path.join(folder_path, new_name),
            "changed": old_name != new_name,
        })

    return pd.DataFrame(rows)


def safe_rename(preview_df):
    changed = 0
    skipped = 0
    errors = []

    for _, row in preview_df.iterrows():
        old_path = row["old_path"]
        new_path = row["new_path"]

        if old_path == new_path:
            skipped += 1
            continue

        if not os.path.exists(old_path):
            skipped += 1
            errors.append(f"元ファイルが見つからない：{old_path}")
            continue

        if os.path.exists(new_path):
            skipped += 1
            errors.append(f"同名ファイルが存在するためスキップ：{new_path}")
            continue

        try:
            os.rename(old_path, new_path)
            changed += 1
        except Exception as e:
            skipped += 1
            errors.append(f"{old_path} → {new_path} / {e}")

    return changed, skipped, errors


def to_log_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "date": x["date"],
            "folder_path": x["folder_path"],
            "mode": x["mode"],
            "changed_count": x["changed_count"],
            "skipped_count": x["skipped_count"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📂",
    layout="wide"
)

st.title("📂 Day188：ファイル名一括リネーマー")
st.caption("フォルダ内のファイル名を、プレビュー確認してから一括変更するアプリ。")

st.warning("注意：実際にファイル名を変更するアプリです。最初はテスト用フォルダで試してね。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("リネーム設定")

    folder_path = st.text_input(
        "対象フォルダパス",
        placeholder=r"例：C:\Users\ユーザー名\Pictures\test"
    )

    target_ext = st.selectbox(
        "対象拡張子",
        TARGET_EXTENSIONS
    )

    mode = st.selectbox(
        "変更モード",
        MODES
    )

    prefix = ""
    suffix = ""
    replace_from = ""
    replace_to = ""
    serial_base = "file"
    serial_start = 1
    serial_digits = 3

    if mode == "接頭辞・接尾辞追加":
        prefix = st.text_input(
            "接頭辞",
            placeholder="例：旅行_"
        )

        suffix = st.text_input(
            "接尾辞",
            placeholder="例：_完成"
        )

    elif mode == "文字置換":
        replace_from = st.text_input(
            "置換前",
            placeholder="例：IMG"
        )

        replace_to = st.text_input(
            "置換後",
            placeholder="例：photo"
        )

    elif mode == "連番リネーム":
        serial_base = st.text_input(
            "ベース名",
            value="image"
        )

        serial_start = st.number_input(
            "開始番号",
            min_value=0,
            value=1,
            step=1
        )

        serial_digits = st.number_input(
            "桁数",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：画像生成素材を整理"
    )

with right:
    st.subheader("対象ファイル")

    if not folder_path.strip():
        st.info("フォルダパスを入力してね。")
        files = []
    elif not os.path.isdir(folder_path):
        st.error("フォルダが見つからないよ。パスを確認してね。")
        files = []
    else:
        files = list_files(folder_path, target_ext)

        st.metric("対象ファイル数", len(files))

        if files:
            st.dataframe(
                pd.DataFrame({"file_name": files}),
                use_container_width=True,
                height=260
            )
        else:
            st.info("対象ファイルが見つからないよ。")

st.divider()
st.subheader("変更プレビュー")

preview_df = pd.DataFrame()

if folder_path.strip() and os.path.isdir(folder_path) and files:
    preview_df = make_preview(
        folder_path=folder_path,
        files=files,
        mode=mode,
        prefix=prefix,
        suffix=suffix,
        replace_from=replace_from,
        replace_to=replace_to,
        serial_base=serial_base,
        serial_start=int(serial_start),
        serial_digits=int(serial_digits),
    )

    changed_preview = preview_df[preview_df["changed"] == True]

    c1, c2 = st.columns(2)

    with c1:
        st.metric("変更予定", len(changed_preview))

    with c2:
        st.metric("変更なし", len(preview_df) - len(changed_preview))

    st.dataframe(
        preview_df[["old_name", "new_name", "changed"]],
        use_container_width=True,
        height=320
    )

    duplicate_names = preview_df["new_name"].duplicated().sum()

    if duplicate_names > 0:
        st.error("変更後ファイル名に重複があるよ。設定を見直してね。")
    else:
        st.success("変更後ファイル名の重複はなさそう。")

    st.divider()

    confirm = st.checkbox("プレビューを確認したので、一括変更を許可する")

    if st.button("📂 一括リネーム実行", type="primary"):
        if not confirm:
            st.warning("実行前に確認チェックを入れてね。")
        elif duplicate_names > 0:
            st.error("変更後ファイル名に重複があるため実行できないよ。")
        else:
            changed, skipped, errors = safe_rename(preview_df)

            log = {
                "id": f"rename_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "folder_path": folder_path,
                "mode": mode,
                "changed_count": int(changed),
                "skipped_count": int(skipped),
                "memo": memo.strip(),
                "errors": errors,
            }

            data["logs"].append(log)
            save_data(data)

            st.success(f"{changed}件リネームしたよ。")
            if skipped:
                st.warning(f"{skipped}件スキップしたよ。")

            if errors:
                with st.expander("エラー詳細"):
                    for e in errors:
                        st.write(e)

            st.rerun()
else:
    st.info("対象フォルダとファイルが見つかると、ここにプレビューが出るよ。")

st.divider()
st.subheader("実行履歴")

log_df = to_log_df(data)

if log_df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        log_df[[
            "date",
            "folder_path",
            "mode",
            "changed_count",
            "skipped_count",
            "memo",
        ]],
        use_container_width=True,
        height=260
    )

    csv = log_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ 履歴CSVダウンロード",
        data=csv,
        file_name="day188_bulk_file_renamer_logs.csv",
        mime="text/csv"
    )
