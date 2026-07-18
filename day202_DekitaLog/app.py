import json
import os
import uuid
from datetime import date, datetime

import streamlit as st


st.set_page_config(
    page_title="できたログ",
    page_icon="✅",
    layout="centered"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "achievements.json"
)


def save_achievements(achievements):
    """達成記録をJSONへ保存する"""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            achievements,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_achievements():
    """達成記録をJSONから読み込む"""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        save_achievements([])
        return []

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    save_achievements([])
    return []


def add_achievement(
    achievements,
    achievement_date,
    content
):
    """新しい達成記録を追加する"""
    new_achievement = {
        "id": str(uuid.uuid4()),
        "date": str(achievement_date),
        "content": content,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    achievements.append(new_achievement)
    save_achievements(achievements)


def delete_achievement(
    achievements,
    achievement_id
):
    """指定した達成記録を削除する"""
    updated_achievements = [
        achievement
        for achievement in achievements
        if achievement.get("id")
        != achievement_id
    ]

    save_achievements(updated_achievements)


achievements = load_achievements()

achievements = sorted(
    achievements,
    key=lambda achievement: (
        achievement.get("date", ""),
        achievement.get("created_at", "")
    ),
    reverse=True
)


st.title("✅ できたログ")
st.caption(
    "今日できたことを、"
    "ひとつだけ記録しよう。"
)


total_count = len(achievements)

today_count = sum(
    1
    for achievement in achievements
    if achievement.get("date")
    == str(date.today())
)


col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🏆 これまでの達成",
        f"{total_count}個"
    )

with col2:
    st.metric(
        "🌱 今日の達成",
        f"{today_count}個"
    )


st.divider()


st.header("✍️ 今日できたこと")

with st.form(
    "achievement_form",
    clear_on_submit=True
):
    achievement_date = st.date_input(
        "日付",
        value=date.today()
    )

    content = st.text_input(
        "できたこと",
        placeholder=(
            "例：アプリを1つ更新した"
        )
    )

    submitted = st.form_submit_button(
        "✅ 記録する",
        use_container_width=True
    )

    if submitted:
        cleaned_content = content.strip()

        if not cleaned_content:
            st.error(
                "できたことを入力してください。"
            )

        else:
            add_achievement(
                achievements=achievements,
                achievement_date=achievement_date,
                content=cleaned_content
            )

            st.success(
                "今日の達成を記録しました！"
            )

            st.rerun()


st.divider()


st.header("📖 これまでのできたこと")

if not achievements:
    st.info(
        "まだ記録がありません。"
        "小さな達成から残してみよう！"
    )

else:
    search_word = st.text_input(
        "🔍 検索",
        placeholder="記録内容を検索"
    )

    filtered_achievements = achievements

    if search_word:
        keyword = search_word.lower()

        filtered_achievements = [
            achievement
            for achievement
            in achievements
            if keyword
            in achievement.get(
                "content",
                ""
            ).lower()
        ]

    st.write(
        f"表示件数："
        f"**{len(filtered_achievements)}件**"
    )

    if not filtered_achievements:
        st.warning(
            "条件に一致する記録がありません。"
        )

    for achievement in filtered_achievements:
        achievement_id = achievement.get(
            "id",
            ""
        )

        achievement_date = achievement.get(
            "date",
            "日付不明"
        )

        content = achievement.get(
            "content",
            ""
        )

        with st.container(border=True):
            text_col, button_col = st.columns(
                [4, 1]
            )

            with text_col:
                st.subheader(
                    f"✅ {content}"
                )

                st.caption(
                    f"📅 {achievement_date}"
                )

            with button_col:
                delete_button = st.button(
                    "🗑️",
                    key=f"delete_{achievement_id}",
                    help="この記録を削除"
                )

                if delete_button:
                    delete_achievement(
                        achievements,
                        achievement_id
                    )

                    st.rerun()


st.divider()

if total_count == 0:
    st.info(
        "最初の一歩を記録してみよう。"
    )

elif total_count < 10:
    st.success(
        "少しずつ達成が"
        "積み上がっています！🌱"
    )

elif total_count < 50:
    st.success(
        "たくさんの『できた』が"
        "集まってきました！🔥"
    )

else:
    st.success(
        "ここまで積み上げた記録は、"
        "大きな自信になります！🏆"
    )
