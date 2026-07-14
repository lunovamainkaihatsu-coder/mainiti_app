import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


APP_TITLE = "Day196：植物管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day196_plant_manager.json")

PLANT_TYPES = [
    "観葉植物",
    "多肉植物",
    "サボテン",
    "花",
    "ハーブ",
    "野菜",
    "果樹",
    "その他",
]

LOCATIONS = [
    "リビング",
    "寝室",
    "玄関",
    "ベランダ",
    "庭",
    "キッチン",
    "窓辺",
    "その他",
]

HEALTH_STATUS = [
    "🟢 元気",
    "🟡 少し心配",
    "🔴 元気がない",
    "🌱 成長中",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "plants": [],
                    "care_logs": [],
                    "growth_logs": [],
                },
                file,
                ensure_ascii=False,
                indent=2,
            )


def load_data():
    ensure_storage()

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = {
            "plants": [],
            "care_logs": [],
            "growth_logs": [],
        }

    data.setdefault("plants", [])
    data.setdefault("care_logs", [])
    data.setdefault("growth_logs", [])

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text():
    return date.today().isoformat()


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


def next_date(last_date, interval_days):
    return parse_date(last_date) + timedelta(days=int(interval_days))


def days_until(last_date, interval_days):
    return (next_date(last_date, interval_days) - date.today()).days


def timing_status(days, icon):
    if days < 0:
        return f"🔴 {icon} {abs(days)}日超過"

    if days == 0:
        return f"🟠 {icon} 今日"

    if days <= 3:
        return f"🟡 {icon} あと{days}日"

    return f"🟢 {icon} あと{days}日"


def overall_status(water_days, fertilizer_days, health):
    if health == "🔴 元気がない":
        return "🔴 要確認"

    if water_days < 0 or fertilizer_days < 0:
        return "🔴 お世話が必要"

    if water_days <= 1 or fertilizer_days <= 3:
        return "🟡 そろそろ"

    return "🟢 良好"


def find_plant(data, plant_id):
    for plant in data["plants"]:
        if plant["id"] == plant_id:
            return plant

    return None


def to_plant_df(data):
    rows = []

    for plant in data["plants"]:
        water_days = days_until(
            plant.get("last_watered", today_text()),
            plant.get("water_interval", 7),
        )

        fertilizer_days = days_until(
            plant.get("last_fertilized", today_text()),
            plant.get("fertilizer_interval", 30),
        )

        rows.append(
            {
                "id": plant["id"],
                "created_at": plant["created_at"],
                "name": plant["name"],
                "plant_type": plant["plant_type"],
                "location": plant["location"],
                "purchase_date": plant.get("purchase_date", ""),
                "health": plant.get("health", "🟢 元気"),
                "last_watered": plant.get("last_watered", ""),
                "next_water": next_date(
                    plant.get("last_watered", today_text()),
                    plant.get("water_interval", 7),
                ).isoformat(),
                "water_days": water_days,
                "water_status": timing_status(water_days, "水やり"),
                "last_fertilized": plant.get("last_fertilized", ""),
                "next_fertilizer": next_date(
                    plant.get("last_fertilized", today_text()),
                    plant.get("fertilizer_interval", 30),
                ).isoformat(),
                "fertilizer_days": fertilizer_days,
                "fertilizer_status": timing_status(
                    fertilizer_days,
                    "肥料",
                ),
                "status": overall_status(
                    water_days,
                    fertilizer_days,
                    plant.get("health", "🟢 元気"),
                ),
                "favorite": bool(plant.get("favorite", False)),
                "memo": plant.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        status_order = {
            "🔴 要確認": 0,
            "🔴 お世話が必要": 1,
            "🟡 そろそろ": 2,
            "🟢 良好": 3,
        }

        df["status_order"] = df["status"].map(status_order).fillna(9)

        df = df.sort_values(
            [
                "status_order",
                "water_days",
                "fertilizer_days",
                "favorite",
                "created_at",
            ],
            ascending=[True, True, True, False, False],
        )

    return df


def to_care_log_df(data):
    rows = []

    for log in data["care_logs"]:
        rows.append(
            {
                "created_at": log["created_at"],
                "date": log["date"],
                "plant_name": log["plant_name"],
                "care_type": log["care_type"],
                "memo": log.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def to_growth_log_df(data):
    rows = []

    for log in data["growth_logs"]:
        rows.append(
            {
                "created_at": log["created_at"],
                "date": log["date"],
                "plant_name": log["plant_name"],
                "health": log.get("health", ""),
                "height_cm": float(log.get("height_cm", 0)),
                "memo": log.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 Day196：植物管理アプリ")
st.caption(
    "植物ごとの水やり・肥料・健康状態・成長記録をまとめて管理するアプリ。"
)

data = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🌱 植物管理",
        "💧 お世話記録",
        "📈 成長記録",
        "📜 履歴",
    ]
)

with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("植物を登録")

        name = st.text_input(
            "植物名",
            placeholder="例：ガジュマル / パキラ / バジル",
        )

        plant_type = st.selectbox(
            "種類",
            PLANT_TYPES,
        )

        location = st.selectbox(
            "設置場所",
            LOCATIONS,
        )

        purchase_date = st.date_input(
            "購入日・植えた日",
            value=date.today(),
        )

        water_interval = st.number_input(
            "水やり頻度（日ごと）",
            min_value=1,
            max_value=365,
            value=7,
            step=1,
        )

        last_watered = st.date_input(
            "最終水やり日",
            value=date.today(),
        )

        fertilizer_interval = st.number_input(
            "肥料頻度（日ごと）",
            min_value=1,
            max_value=730,
            value=30,
            step=1,
        )

        last_fertilized = st.date_input(
            "最終肥料日",
            value=date.today(),
        )

        health = st.selectbox(
            "健康状態",
            HEALTH_STATUS,
        )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder="例：直射日光を避ける / 土が乾いてから水やり",
        )

        favorite = st.checkbox("⭐ 大切な植物")

        water_next = last_watered + timedelta(days=int(water_interval))
        fertilizer_next = last_fertilized + timedelta(
            days=int(fertilizer_interval)
        )

        st.info(
            f"次回水やり：{water_next.isoformat()} / "
            f"次回肥料：{fertilizer_next.isoformat()}"
        )

        if st.button("🌱 植物を登録", type="primary"):
            if not name.strip():
                st.warning("植物名を入れてね。")
            else:
                plant = {
                    "id": f"plant_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_text(),
                    "name": name.strip(),
                    "plant_type": plant_type,
                    "location": location,
                    "purchase_date": purchase_date.isoformat(),
                    "water_interval": int(water_interval),
                    "last_watered": last_watered.isoformat(),
                    "fertilizer_interval": int(fertilizer_interval),
                    "last_fertilized": last_fertilized.isoformat(),
                    "health": health,
                    "memo": memo.strip(),
                    "favorite": favorite,
                }

                data["plants"].append(plant)
                save_data(data)

                st.success("植物を登録したよ。")
                st.rerun()

    with right:
        st.subheader("植物ダッシュボード")

        df = to_plant_df(data)

        if df.empty:
            st.info("まだ植物が登録されていないよ。")
        else:
            urgent = len(
                df[
                    df["status"].isin(
                        [
                            "🔴 要確認",
                            "🔴 お世話が必要",
                        ]
                    )
                ]
            )

            water_today = len(df[df["water_days"] <= 0])
            fertilizer_today = len(df[df["fertilizer_days"] <= 0])

            c1, c2 = st.columns(2)

            with c1:
                st.metric("植物数", len(df))
                st.metric("要確認", urgent)

            with c2:
                st.metric("水やり予定", water_today)
                st.metric("肥料予定", fertilizer_today)

            st.divider()
            st.subheader("優先してお世話する植物")

            care_needed = df[
                (df["water_days"] <= 3)
                | (df["fertilizer_days"] <= 3)
                | (
                    df["status"].isin(
                        [
                            "🔴 要確認",
                            "🔴 お世話が必要",
                        ]
                    )
                )
            ]

            if care_needed.empty:
                st.success("急ぎのお世話はなさそう。みんな元気そう！")
            else:
                st.dataframe(
                    care_needed[
                        [
                            "name",
                            "plant_type",
                            "location",
                            "water_status",
                            "fertilizer_status",
                            "health",
                            "status",
                        ]
                    ],
                    use_container_width=True,
                    height=260,
                )

    st.divider()
    st.subheader("植物一覧")

    df = to_plant_df(data)

    if df.empty:
        st.write("まだ植物一覧が空だよ。")
    else:
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            keyword = st.text_input(
                "検索",
                placeholder="植物名・メモ",
            )

        with col_b:
            type_filter = st.selectbox(
                "種類で絞る",
                ["すべて"] + PLANT_TYPES,
            )

        with col_c:
            location_filter = st.selectbox(
                "場所で絞る",
                ["すべて"] + LOCATIONS,
            )

        fav_only = st.checkbox("⭐ 大切な植物だけ表示")

        view = df.copy()

        if keyword.strip():
            query = keyword.strip()

            view = view[
                view["name"].fillna("").str.contains(
                    query,
                    case=False,
                    na=False,
                )
                | view["memo"].fillna("").str.contains(
                    query,
                    case=False,
                    na=False,
                )
            ]

        if type_filter != "すべて":
            view = view[view["plant_type"] == type_filter]

        if location_filter != "すべて":
            view = view[view["location"] == location_filter]

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(
            view[
                [
                    "name",
                    "plant_type",
                    "location",
                    "health",
                    "last_watered",
                    "next_water",
                    "water_status",
                    "last_fertilized",
                    "next_fertilizer",
                    "fertilizer_status",
                    "status",
                    "favorite",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=340,
        )

        st.divider()
        st.subheader("詳細・更新")

        if view.empty:
            st.write("条件に合う植物がないよ。")
        else:
            selected_id = st.selectbox(
                "植物を選ぶ",
                view["id"].tolist(),
                format_func=lambda plant_id: (
                    f"{find_plant(data, plant_id)['name']} / "
                    f"{find_plant(data, plant_id)['location']}"
                ),
            )

            plant = find_plant(data, selected_id)

            if plant:
                water_days = days_until(
                    plant.get("last_watered", today_text()),
                    plant.get("water_interval", 7),
                )

                fertilizer_days = days_until(
                    plant.get("last_fertilized", today_text()),
                    plant.get("fertilizer_interval", 30),
                )

                st.markdown(f"## {plant['name']}")
                st.write(f"種類：{plant['plant_type']}")
                st.write(f"場所：{plant['location']}")
                st.write(f"健康状態：{plant.get('health', '🟢 元気')}")
                st.info(timing_status(water_days, "水やり"))
                st.info(timing_status(fertilizer_days, "肥料"))

                if plant.get("memo"):
                    st.write(plant["memo"])

                c1, c2, c3 = st.columns(3)

                with c1:
                    new_water_interval = st.number_input(
                        "水やり頻度更新",
                        min_value=1,
                        max_value=365,
                        value=int(plant.get("water_interval", 7)),
                        step=1,
                        key=f"water_interval_{plant['id']}",
                    )

                with c2:
                    new_fertilizer_interval = st.number_input(
                        "肥料頻度更新",
                        min_value=1,
                        max_value=730,
                        value=int(
                            plant.get(
                                "fertilizer_interval",
                                30,
                            )
                        ),
                        step=1,
                        key=f"fertilizer_interval_{plant['id']}",
                    )

                with c3:
                    new_health = st.selectbox(
                        "健康状態更新",
                        HEALTH_STATUS,
                        index=HEALTH_STATUS.index(
                            plant.get("health", "🟢 元気")
                        ),
                        key=f"health_{plant['id']}",
                    )

                new_favorite = st.checkbox(
                    "⭐ 大切な植物",
                    value=bool(plant.get("favorite", False)),
                    key=f"favorite_{plant['id']}",
                )

                if st.button("📝 植物情報を更新"):
                    plant["water_interval"] = int(
                        new_water_interval
                    )
                    plant["fertilizer_interval"] = int(
                        new_fertilizer_interval
                    )
                    plant["health"] = new_health
                    plant["favorite"] = new_favorite
                    plant["updated_at"] = now_text()

                    save_data(data)

                    st.success("植物情報を更新したよ。")
                    st.rerun()

                if st.button(
                    "🗑️ この植物を削除",
                    type="secondary",
                ):
                    data["plants"] = [
                        item
                        for item in data["plants"]
                        if item["id"] != selected_id
                    ]

                    data["care_logs"] = [
                        item
                        for item in data["care_logs"]
                        if item.get("plant_id") != selected_id
                    ]

                    data["growth_logs"] = [
                        item
                        for item in data["growth_logs"]
                        if item.get("plant_id") != selected_id
                    ]

                    save_data(data)

                    st.warning("植物を削除したよ。")
                    st.rerun()

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ 植物一覧CSVダウンロード",
            data=csv,
            file_name="day196_plant_manager.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("お世話を記録")

    df = to_plant_df(data)

    if df.empty:
        st.info("先に植物を登録してね。")
    else:
        selected_id = st.selectbox(
            "植物",
            df["id"].tolist(),
            format_func=lambda plant_id: (
                f"{find_plant(data, plant_id)['name']} / "
                f"{find_plant(data, plant_id)['location']}"
            ),
            key="care_plant",
        )

        plant = find_plant(data, selected_id)

        care_type = st.radio(
            "お世話内容",
            [
                "💧 水やり",
                "🌿 肥料",
                "🪴 植え替え",
                "✂️ 剪定",
                "☀️ 場所移動",
                "その他",
            ],
            horizontal=True,
        )

        care_date = st.date_input(
            "お世話した日",
            value=date.today(),
        )

        care_memo = st.text_area(
            "お世話メモ",
            height=100,
            placeholder="例：土が乾いていた / 液体肥料を使用",
        )

        if st.button("🌱 お世話を記録", type="primary"):
            if care_type == "💧 水やり":
                plant["last_watered"] = care_date.isoformat()

            if care_type == "🌿 肥料":
                plant["last_fertilized"] = care_date.isoformat()

            plant["updated_at"] = now_text()

            log = {
                "id": f"care_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_text(),
                "date": care_date.isoformat(),
                "plant_id": plant["id"],
                "plant_name": plant["name"],
                "care_type": care_type,
                "memo": care_memo.strip(),
            }

            data["care_logs"].append(log)
            save_data(data)

            st.success("お世話を記録したよ。")
            st.rerun()

with tab3:
    st.subheader("成長を記録")

    df = to_plant_df(data)

    if df.empty:
        st.info("先に植物を登録してね。")
    else:
        selected_id = st.selectbox(
            "植物",
            df["id"].tolist(),
            format_func=lambda plant_id: (
                f"{find_plant(data, plant_id)['name']} / "
                f"{find_plant(data, plant_id)['plant_type']}"
            ),
            key="growth_plant",
        )

        plant = find_plant(data, selected_id)

        growth_date = st.date_input(
            "記録日",
            value=date.today(),
            key="growth_date",
        )

        growth_health = st.selectbox(
            "健康状態",
            HEALTH_STATUS,
            index=HEALTH_STATUS.index(
                plant.get("health", "🟢 元気")
            ),
            key="growth_health",
        )

        height_cm = st.number_input(
            "高さ・大きさ（cm）",
            min_value=0.0,
            value=0.0,
            step=0.5,
        )

        growth_memo = st.text_area(
            "成長メモ",
            height=120,
            placeholder="例：新芽が出た / 葉が2枚増えた / 少し元気がない",
        )

        if st.button("📈 成長記録を保存", type="primary"):
            plant["health"] = growth_health
            plant["updated_at"] = now_text()

            log = {
                "id": f"growth_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_text(),
                "date": growth_date.isoformat(),
                "plant_id": plant["id"],
                "plant_name": plant["name"],
                "health": growth_health,
                "height_cm": float(height_cm),
                "memo": growth_memo.strip(),
            }

            data["growth_logs"].append(log)
            save_data(data)

            st.success("成長記録を保存したよ。")
            st.rerun()

with tab4:
    care_df = to_care_log_df(data)
    growth_df = to_growth_log_df(data)

    st.subheader("お世話履歴")

    if care_df.empty:
        st.write("まだお世話履歴がないよ。")
    else:
        st.dataframe(
            care_df[
                [
                    "date",
                    "plant_name",
                    "care_type",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=260,
        )

        care_csv = care_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ お世話履歴CSV",
            data=care_csv,
            file_name="day196_plant_care_logs.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("成長履歴")

    if growth_df.empty:
        st.write("まだ成長履歴がないよ。")
    else:
        st.dataframe(
            growth_df[
                [
                    "date",
                    "plant_name",
                    "health",
                    "height_cm",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=260,
        )

        growth_csv = growth_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ 成長履歴CSV",
            data=growth_csv,
            file_name="day196_plant_growth_logs.csv",
            mime="text/csv",
        )
