import streamlit as st
import time
import random

st.set_page_config(layout="wide")

# ------------------------
# 初期化
# ------------------------
if "player_y" not in st.session_state:
    st.session_state.player_y = 200   # プレイヤーの高さ
if "velocity" not in st.session_state:
    st.session_state.velocity = 0
if "obstacles" not in st.session_state:
    st.session_state.obstacles = []   # 障害物リスト
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "frames_since_spawn" not in st.session_state:
    st.session_state.frames_since_spawn = 100  # しばらく出さないように大きめ

# ------------------------
# 地面判定（ここより下なら着地とみなす）
# ------------------------
GROUND_Y = 250
ON_GROUND_THRESHOLD = 248  # ほぼ地面

def on_ground():
    return st.session_state.player_y >= ON_GROUND_THRESHOLD

# ------------------------
# ボタン入力（ワンボタン）
# ------------------------
jump_pressed = st.button("JUMP!")

# JUMPが押されたら上向きの速度を与える（空中では跳べない）
if jump_pressed and not st.session_state.game_over and on_ground():
    st.session_state.velocity = -12

canvas = st.empty()

# ------------------------
# ゲーム更新
# ------------------------
if not st.session_state.game_over:
    # 重力
    st.session_state.velocity += 1
    st.session_state.player_y += st.session_state.velocity

    # 画面内にクランプ（上:20, 下:GROUND_Y）
    if st.session_state.player_y < 20:
        st.session_state.player_y = 20
        st.session_state.velocity = 0
    if st.session_state.player_y > GROUND_Y:
        st.session_state.player_y = GROUND_Y
        st.session_state.velocity = 0

    # フレームカウンタ
    st.session_state.frames_since_spawn += 1

    # 難易度に応じたスピード（スコアが上がると速くなる）
    # 500点ごとに +1
    base_speed = 6 + st.session_state.score // 500

    # 障害物生成
    # 一定フレーム以上空いていて、さらに確率チェックを通ったら生成
    spawn_interval_frames = 25  # 最低でもこれだけは空ける（約0.75秒）
    spawn_prob = 0.25           # 条件を満たした時の生成確率

    if st.session_state.frames_since_spawn >= spawn_interval_frames:
        if random.random() < spawn_prob:
            st.session_state.obstacles.append({"x": 800})
            st.session_state.frames_since_spawn = 0

    # 障害物移動
    for obs in st.session_state.obstacles:
        obs["x"] -= base_speed

    # 画面外の障害物を削除
    st.session_state.obstacles = [
        o for o in st.session_state.obstacles if o["x"] > -40
    ]

    # スコア加算
    st.session_state.score += 1

    # 当たり判定（ざっくり）
    for obs in st.session_state.obstacles:
        # プレイヤーのxは 50px 固定、幅20pxとみなす
        # 地面付近（>220）にいるときにぶつかったらアウト
        if 50 < obs["x"] < 70 and st.session_state.player_y > 220:
            st.session_state.game_over = True
            break

# ------------------------
# 背景色（スコアで変化）
# ------------------------
score = st.session_state.score
if score < 500:
    bg_color = "#ffffff"   # 白：序盤
elif score < 1500:
    bg_color = "#eef7ff"   # ちょい青：だんだん集中
else:
    bg_color = "#ffeef7"   # ピンク寄り：かなり頑張ってるゾーン

# ------------------------
# 描画
# ------------------------
html = f"""
<div style='position:relative;width:800px;height:300px;
            background:{bg_color};border:2px solid #000;'>
    <!-- プレイヤー（ルナっぽい水色の丸） -->
    <div style='position:absolute;left:50px;top:{st.session_state.player_y}px;
                width:22px;height:22px;border-radius:50%;
                background:#7fc8ff;border:2px solid #004466;'></div>
"""

for obs in st.session_state.obstacles:
    html += f"""
    <div style='position:absolute;left:{obs["x"]}px;top:260px;
                width:20px;height:40px;background:#222222;'></div>
    """

html += f"""
    <!-- スコア表示 -->
    <div style='position:absolute;left:10px;top:10px;font-size:20px;'>
        Score: {st.session_state.score}
    </div>
</div>
"""

canvas.html(html)

# ------------------------
# ゲームオーバー処理 or ループ
# ------------------------
if st.session_state.game_over:
    st.write("### 💀 GAME OVER!")
    st.write(f"スコア：{st.session_state.score}")

    if st.button("Restart"):
        st.session_state.player_y = 200
        st.session_state.velocity = 0
        st.session_state.obstacles = []
        st.session_state.score = 0
        st.session_state.game_over = False
        st.session_state.frames_since_spawn = 100
        st.rerun()
else:
    # ゲーム継続中は少し待ってから自動で再描画
    time.sleep(0.03)
    st.rerun()
