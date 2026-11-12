import json
import uuid
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title='未来の自分に必要なもの', page_icon='🎒', layout='wide')
DATA = Path(__file__).parent / 'data' / 'future_prep.json'
KINDS = ['visions', 'requirements', 'actions', 'milestones', 'messages']
CATS = ['知識・スキル', '経験・実績', 'お金・資源', '環境・時間', '人とのつながり', '心身・習慣']
V_CATS = ['仕事・事業', '学習', '暮らし', '家族・人間関係', '健康', 'その他']
STATUSES = ['未着手', '進行中', '完了', '保留']

def empty():
    return {k: [] for k in KINDS}

def validate(obj):
    if not isinstance(obj, dict) or any(not isinstance(obj.get(k), list) for k in KINDS):
        raise ValueError('データ形式が正しくありません。')
    for k in KINDS:
        if any(not isinstance(x, dict) or not isinstance(x.get('id'), str) for x in obj[k]):
            raise ValueError(f'{k} のデータが不正です。')
    return {k: obj[k] for k in KINDS}

def load():
    if DATA.exists():
        try:
            return validate(json.loads(DATA.read_text(encoding='utf-8')))
        except (ValueError, OSError) as exc:
            st.error(f'保存データを読み込めません: {exc}')
            st.stop()
    return empty()

def save():
    DATA.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA.with_suffix('.tmp')
    tmp.write_text(json.dumps(st.session_state.db, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(DATA)

def add(kind, payload):
    st.session_state.db[kind].append({'id': uuid.uuid4().hex, 'created': datetime.now().isoformat(timespec='seconds'), **payload})
    save()
    st.success('保存したよ！')

def choose_vision(label='関連する未来', key='vision'):
    vs = st.session_state.db['visions']
    if not vs:
        st.info('先に「理想の未来」タブで目標を登録してね。')
        return None
    ids = [v['id'] for v in vs]
    names = {v['id']: v.get('title', '無題') for v in vs}
    return st.selectbox(label, ids, format_func=lambda i: names.get(i, '削除された目標'), key=key)

def vname(vid):
    return next((v.get('title', '無題') for v in st.session_state.db['visions'] if v['id'] == vid), '削除された目標')

def progress(v_id):
    reqs = [r for r in st.session_state.db['requirements'] if r.get('vision_id') == v_id]
    if not reqs:
        return None
    weights = [max(1, int(r.get('importance', 1))) for r in reqs]
    return sum(int(r.get('level', 1)) / 5 * w for r, w in zip(reqs, weights)) / sum(weights)

if 'db' not in st.session_state:
    st.session_state.db = load()
db = st.session_state.db
st.title('🎒🌱 未来の自分に必要なもの')
st.caption('Day319 / 365 — 夢と今日の小さな準備をつなぐアプリ')
tabs = st.tabs(['🏠 ホーム', '🌈 理想の未来', '🎒 必要なもの', '📊 ギャップ分析', '🪴 小さな準備', '🗺️ ロードマップ', '📈 未来準備分析', '🛠️ 管理'])

with tabs[0]:
    st.subheader('未来への準備状況')
    cols = st.columns(4)
    for col, (label, kind) in zip(cols, [('未来の目標', 'visions'), ('必要な準備', 'requirements'), ('小さな行動', 'actions'), ('マイルストーン', 'milestones')]):
        col.metric(label, len(db[kind]))
    if not db['visions']:
        st.info('まず「🌈 理想の未来」で目標を登録しよう！')
    for v in db['visions']:
        st.markdown(f"#### {'⭐ ' if v.get('favorite') else ''}{v.get('title', '無題')}")
        st.caption(f"{v.get('category', 'その他')} ・ 期限 {v.get('deadline', '未設定')}")
        p = progress(v['id'])
        st.progress(p if p is not None else int(v.get('readiness', 0))/100, text=f"準備度 {round((p if p is not None else int(v.get('readiness', 0))/100)*100)}% {'（必要なものから算出）' if p is not None else '（自己評価）'}")
    pending = [a for a in db['actions'] if a.get('status') != '完了']
    if pending:
        st.subheader('次にできること')
        for a in sorted(pending, key=lambda x: x.get('due', '9999'))[:5]:
            st.write(f"・{a.get('title', '')} — {vname(a.get('vision_id'))} / {a.get('due', '期限なし')}")

with tabs[1]:
    st.subheader('理想の未来を描く')
    with st.form('new_vision', clear_on_submit=True):
        title = st.text_input('目標名 *')
        category = st.selectbox('カテゴリー', V_CATS)
        ideal = st.text_area('実現したい未来の姿')
        reason = st.text_area('なぜ実現したい？')
        deadline = st.date_input('目標期限', value=date.today())
        priority = st.slider('優先度', 1, 5, 3)
        readiness = st.slider('現在の準備度（自己評価）', 0, 100, 0)
        favorite = st.checkbox('お気に入り')
        if st.form_submit_button('未来を登録', type='primary'):
            if title.strip():
                add('visions', dict(title=title.strip(), category=category, ideal=ideal, reason=reason, deadline=str(deadline), priority=priority, readiness=readiness, favorite=favorite))
            else:
                st.warning('目標名を入力してね。')
    for v in db['visions']:
        with st.expander(f"{'⭐ ' if v.get('favorite') else ''}{v.get('title')} — {v.get('deadline')}"):
            st.write(v.get('ideal', ''))
            st.caption(v.get('reason', ''))

with tabs[2]:
    st.subheader('未来に必要なもの')
    vid = choose_vision(key='reqvision')
    if vid:
        with st.form('new_requirement', clear_on_submit=True):
            title = st.text_input('必要なもの *')
            category = st.selectbox('分類', CATS)
            why = st.text_area('必要な理由')
            importance = st.slider('重要度', 1, 5, 4)
            level = st.slider('現在の充足度', 1, 5, 1)
            target = st.text_input('目指す状態')
            if st.form_submit_button('必要なものを登録', type='primary'):
                if title.strip():
                    add('requirements', dict(vision_id=vid, title=title.strip(), category=category, why=why, importance=importance, level=level, target=target))
                else:
                    st.warning('名前を入力してね。')
    for r in db['requirements']:
        with st.expander(f"{r.get('title')} — {vname(r.get('vision_id'))}"):
            st.write(f"分類：{r.get('category')} / 重要度：{r.get('importance')} / 充足度：{r.get('level')}")
            st.write(r.get('why', ''))
            st.caption('目標：' + r.get('target', ''))

with tabs[3]:
    st.subheader('不足度 × 重要度')
    if db['requirements']:
        rows = []
        for r in db['requirements']:
            gap = 5 - int(r.get('level', 1))
            rows.append({'未来': vname(r.get('vision_id')), '必要なもの': r.get('title'), '分類': r.get('category'), '充足度': r.get('level'), '重要度': r.get('importance'), '不足度': gap, '優先スコア': gap * int(r.get('importance', 1))})
        df = pd.DataFrame(rows).sort_values('優先スコア', ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index('必要なもの')['優先スコア'])
        st.caption('優先スコア = (5 − 現在の充足度) × 重要度。判断の参考値であり、絶対的な優先順位ではないよ。')
    else:
        st.info('必要なものを登録すると、ギャップを分析できるよ。')

with tabs[4]:
    st.subheader('今日できる小さな準備')
    vid = choose_vision(key='actvision')
    if vid:
        with st.form('new_action', clear_on_submit=True):
            title = st.text_input('行動名 *')
            minutes = st.number_input('所要時間（分）', min_value=1, value=15)
            due = st.date_input('実施期限', value=date.today())
            difficulty = st.slider('難易度', 1, 5, 2)
            note = st.text_area('メモ')
            if st.form_submit_button('行動を追加', type='primary'):
                if title.strip():
                    add('actions', dict(vision_id=vid, title=title.strip(), minutes=int(minutes), due=str(due), difficulty=difficulty, status='未着手', note=note))
                else:
                    st.warning('行動名を入力してね。')
    for a in db['actions']:
        with st.expander(f"{a.get('title')} — {a.get('status', '未着手')}"):
            st.caption(f"{vname(a.get('vision_id'))} / {a.get('minutes', 0)}分 / 期限 {a.get('due')}")
            status = st.selectbox('実施状況', STATUSES, index=STATUSES.index(a.get('status', '未着手')) if a.get('status') in STATUSES else 0, key='action_status_'+a['id'])
            if st.button('状態を保存', key='action_save_'+a['id']):
                a['status'] = status
                save()
                st.success('更新したよ！')

with tabs[5]:
    st.subheader('未来へのロードマップ')
    vid = choose_vision(key='milevision')
    if vid:
        with st.form('new_milestone', clear_on_submit=True):
            title = st.text_input('中間目標 *')
            due = st.date_input('達成期限', value=date.today())
            condition = st.text_area('達成条件')
            if st.form_submit_button('マイルストーンを追加', type='primary'):
                if title.strip():
                    add('milestones', dict(vision_id=vid, title=title.strip(), due=str(due), condition=condition, status='未着手'))
                else:
                    st.warning('中間目標名を入力してね。')
    for m in sorted(db['milestones'], key=lambda x: x.get('due', '9999')):
        with st.expander(f"{m.get('due')}｜{m.get('title')}｜{m.get('status')}"):
            st.write(m.get('condition', ''))
            status = st.selectbox('進捗', STATUSES, index=STATUSES.index(m.get('status', '未着手')) if m.get('status') in STATUSES else 0, key='milestone_status_'+m['id'])
            if st.button('進捗を保存', key='milestone_save_'+m['id']):
                m['status'] = status
                save()
                st.success('更新したよ！')
    st.divider()
    st.subheader('✉️ 未来の自分へのメッセージ')
    msgvid = choose_vision('関連する未来', key='msgvision')
    if msgvid:
        with st.form('new_message', clear_on_submit=True):
            body = st.text_area('未来の自分へ伝えたいこと *')
            open_date = st.date_input('読み返す日', value=date.today())
            if st.form_submit_button('メッセージを保存'):
                if body.strip():
                    add('messages', dict(vision_id=msgvid, body=body.strip(), open_date=str(open_date)))
                else:
                    st.warning('メッセージを入力してね。')
    for m in db['messages']:
        if m.get('open_date', '') <= str(date.today()):
            with st.expander(f"✉️ {vname(m.get('vision_id'))} — {m.get('open_date')}"):
                st.write(m.get('body'))
        else:
            st.write(f"🔒 {m.get('open_date')} に読めるメッセージ — {vname(m.get('vision_id'))}")

with tabs[6]:
    st.subheader('未来準備の分析')
    if db['requirements']:
        df = pd.DataFrame([{'分類': r.get('category', 'その他'), '充足度': int(r.get('level', 1)), '不足度': 5-int(r.get('level', 1))} for r in db['requirements']])
        st.write('カテゴリー別の平均充足度')
        st.bar_chart(df.groupby('分類')['充足度'].mean())
    else:
        st.info('必要なものを登録すると分析が表示されるよ。')
    if db['actions']:
        completed = sum(a.get('status') == '完了' for a in db['actions'])
        st.metric('行動達成率', f'{completed / len(db["actions"]):.0%}', f'{completed}/{len(db["actions"])} 件完了')
    if db['milestones']:
        completed = sum(m.get('status') == '完了' for m in db['milestones'])
        st.metric('マイルストーン達成率', f'{completed / len(db["milestones"]):.0%}', f'{completed}/{len(db["milestones"])} 件完了')
    if db['visions']:
        st.write('未来別の準備度')
        st.bar_chart(pd.DataFrame([{'未来': v.get('title'), '準備度': round(100*(progress(v['id']) if progress(v['id']) is not None else int(v.get('readiness', 0))/100))} for v in db['visions']]).set_index('未来'))

with tabs[7]:
    st.subheader('データ管理')
    labels = {'visions':'未来の目標', 'requirements':'必要なもの', 'actions':'小さな行動', 'milestones':'マイルストーン', 'messages':'メッセージ'}
    kind = st.selectbox('編集するデータ', KINDS, format_func=lambda x: labels[x])
    items = db[kind]
    if items:
        ids = [x['id'] for x in items]
        selected = st.selectbox('対象を選択', ids, format_func=lambda i: next((x.get('title', x.get('body', '')[:30]) for x in items if x['id'] == i), '不明'))
        record = next(x for x in items if x['id'] == selected)
        st.caption('JSON形式で内容を編集できるよ。idとcreatedは変更しないでね。')
        edited = st.text_area('編集内容（JSON）', value=json.dumps(record, ensure_ascii=False, indent=2), height=260, key='edit_'+kind+'_'+selected)
        c1, c2 = st.columns(2)
        if c1.button('編集を保存', key='edit_save'):
            try:
                obj = json.loads(edited)
                if not isinstance(obj, dict) or obj.get('id') != selected or obj.get('created') != record.get('created'):
                    raise ValueError('idまたはcreatedが変更されています。')
                if kind != 'visions' and obj.get('vision_id') not in {v['id'] for v in db['visions']}:
                    raise ValueError('関連する未来のIDが正しくありません。')
                record.clear()
                record.update(obj)
                save()
                st.success('更新したよ！')
            except (ValueError, json.JSONDecodeError) as exc:
                st.error(f'保存できません: {exc}')
        confirm = c2.checkbox('削除を確認', key='delete_confirm_'+selected)
        if c2.button('選択データを削除', disabled=not confirm):
            db[kind] = [x for x in items if x['id'] != selected]
            if kind == 'visions':
                for child_kind in KINDS[1:]:
                    db[child_kind] = [x for x in db[child_kind] if x.get('vision_id') != selected]
            save()
            st.rerun()
    else:
        st.info('この種類のデータはまだないよ。')
    st.divider()
    st.subheader('バックアップ・復元')
    st.download_button('📥 JSONバックアップをダウンロード', json.dumps(db, ensure_ascii=False, indent=2).encode('utf-8'), file_name='future_prep_backup.json', mime='application/json')
    upload = st.file_uploader('復元するJSONファイルを選択', type=['json'])
    if upload:
        try:
            restored = validate(json.loads(upload.getvalue().decode('utf-8')))
            st.warning('復元すると現在のデータは上書きされるよ。先にバックアップを取ってね。')
            if st.checkbox('上書きを了承する') and st.button('バックアップから復元', type='primary'):
                st.session_state.db = restored
                save()
                st.rerun()
        except (UnicodeDecodeError, ValueError) as exc:
            st.error(f'ファイルを読み込めません: {exc}')
