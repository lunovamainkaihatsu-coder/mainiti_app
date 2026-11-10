import json
import os
import uuid
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title='自分の武器、何個ある？', page_icon='⚔️', layout='wide')
PATH = Path(__file__).parent / 'data' / 'weapons.json'
CATEGORIES = ['💻 技術', '💼 仕事', '💬 コミュニケーション', '🧠 思考力', '🎨 創造力', '🏠 生活', '💪 身体・健康', '📦 その他']
GOAL_STATUSES = ['未着手', '進行中', '達成', '保留']
TABLES = ('skills', 'evidences', 'combinations', 'growth_logs', 'goals')

def blank():
    return {key: [] for key in TABLES}

def uid():
    return str(uuid.uuid4())

def now():
    return datetime.now().isoformat(timespec='seconds')

def validate(db):
    if not isinstance(db, dict) or any(not isinstance(db.get(k), list) for k in TABLES):
        raise ValueError('必要なデータ配列が不足しています。')
    ids = []
    for k in TABLES:
        for x in db[k]:
            if not isinstance(x, dict) or not isinstance(x.get('id'), str) or not x['id']:
                raise ValueError(f'{k}に不正なレコードがあります。')
            ids.append(x['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('IDが重複しています。')
    skills = {x['id'] for x in db['skills']}
    for x in db['skills']:
        if not isinstance(x.get('name'), str) or not x['name'].strip():
            raise ValueError('スキル名が不正です。')
        if x.get('category') not in CATEGORIES:
            raise ValueError('カテゴリーが不正です。')
        for key in ('level', 'confidence'):
            if type(x.get(key)) is not int or not 1 <= x[key] <= 5:
                raise ValueError('スキル評価が不正です。')
    for k in ('evidences', 'growth_logs', 'goals'):
        for x in db[k]:
            if x.get('skill_id') not in skills:
                raise ValueError(f'{k}に存在しないスキルへの参照があります。')
    for x in db['combinations']:
        if not isinstance(x.get('skill_ids'), list) or not 2 <= len(set(x['skill_ids'])) <= 3 or any(i not in skills for i in x['skill_ids']):
            raise ValueError('組み合わせのスキル参照が不正です。')
    for x in db['growth_logs']:
        for k in ('level', 'confidence'):
            if type(x.get(k)) is not int or not 1 <= x[k] <= 5:
                raise ValueError('成長記録の評価が不正です。')
    for x in db['goals']:
        if x.get('status') not in GOAL_STATUSES:
            raise ValueError('目標ステータスが不正です。')
    return db

def save():
    validate(data)
    PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PATH.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PATH)

def add(table, fields):
    data[table].append({'id': uid(), 'created_at': now(), **fields})
    save()
    st.rerun()

def get_skill(sid):
    return next((s for s in data['skills'] if s['id'] == sid), None)

def skill_label(s):
    return f"{s['name']} [{s['id'][:8]}]"

def pick_skill(key):
    if not data['skills']:
        st.info('まず「⚔️ 武器を登録」からスキルを追加してね。')
        return None
    options = {skill_label(s): s['id'] for s in data['skills']}
    label = st.selectbox('対象のスキル', list(options), key=key)
    return get_skill(options[label])

def related(table, sid):
    return [x for x in data[table] if x.get('skill_id') == sid]

def delete_record(table, record):
    rid = record['id']
    data[table] = [x for x in data[table] if x['id'] != rid]
    if table == 'skills':
        for k in ('evidences', 'growth_logs', 'goals'):
            data[k] = [x for x in data[k] if x['skill_id'] != rid]
        data['combinations'] = [x for x in data['combinations'] if rid not in x['skill_ids']]
    save()
    st.rerun()

st.title('⚔️💎 自分の武器、何個ある？')
st.caption('Day317 / 365 — 自分の可能性を、もっと知ろう。')
st.write('スキル・経験・強みを集めて、**自分だけの能力図鑑**を育てよう！')

if PATH.exists():
    try:
        with PATH.open(encoding='utf-8') as f:
            data = validate(json.load(f))
    except (ValueError, OSError, json.JSONDecodeError) as e:
        st.error(f'保存データを読み込めません。元のファイルは変更していません：{e}')
        st.stop()
else:
    data = blank()
    save()

tabs = st.tabs(['🏠 ホーム', '⚔️ 武器を登録', '🏆 活用実績', '🧩 スキル合成', '📚 自分の武器庫', '📈 成長・育成', '📊 能力分析', '🛠️ 管理'])

with tabs[0]:
    st.subheader('🏠 マイ能力ダッシュボード')
    c = st.columns(4)
    for col, label, count in zip(c, ['登録スキル', '活用実績', 'スキル合成', '育成中の目標'], [len(data['skills']), len(data['evidences']), len(data['combinations']), sum(g['status'] == '進行中' for g in data['goals'])]):
        col.metric(label, count)
    st.markdown('### 最近登録した武器')
    for s in sorted(data['skills'], key=lambda x: x['created_at'], reverse=True)[:6]:
        with st.container(border=True):
            st.markdown(f"**{s['name']}**　{'❤️' if s.get('favorite') else ''}")
            st.caption(f"{s['category']}｜習熟度 Lv.{s['level']} / 5｜自信度 {s['confidence']} / 5")
            st.write(s.get('can_do') or 'できることを追加してみよう。')
    if not data['skills']:
        st.info('最初の武器を登録しよう！ 小さな得意も立派なスキルだよ。')

with tabs[1]:
    st.subheader('⚔️ 新しい武器を登録')
    with st.form('new_skill', clear_on_submit=True):
        name = st.text_input('スキル名 *', placeholder='例：Pythonプログラミング')
        category = st.selectbox('カテゴリー', CATEGORIES)
        c1, c2 = st.columns(2)
        with c1:
            level = st.slider('習熟度', 1, 5, 2)
        with c2:
            confidence = st.slider('自信度', 1, 5, 3)
        origin = st.text_area('習得のきっかけ')
        can_do = st.text_area('できること')
        use_case = st.text_area('活用できる場面')
        next_step = st.text_area('これからの目標')
        favorite = st.checkbox('❤️ お気に入り')
        if st.form_submit_button('⚔️ 武器を保存', type='primary'):
            if not name.strip():
                st.warning('スキル名を入力してね。')
            else:
                add('skills', dict(name=name.strip(), category=category, level=level, confidence=confidence, origin=origin, can_do=can_do, use_case=use_case, next_step=next_step, favorite=favorite))

with tabs[2]:
    st.subheader('🏆 スキルを使えた証拠')
    skill = pick_skill('evidence_skill')
    if skill:
        with st.form('new_evidence', clear_on_submit=True):
            d = st.date_input('実績の日付', value=date.today(), max_value=date.today())
            scene = st.text_input('どんな場面？ *')
            action = st.text_area('自分が取った行動')
            result = st.text_area('結果・成果')
            rating = st.slider('自己評価', 1, 5, 3)
            if st.form_submit_button('🏆 実績を保存', type='primary'):
                if not scene.strip():
                    st.warning('場面を入力してね。')
                else:
                    add('evidences', dict(skill_id=skill['id'], date=str(d), scene=scene.strip(), action=action, result=result, rating=rating))
        st.markdown('### 保存した実績')
        for x in sorted(related('evidences', skill['id']), key=lambda a: a['date'], reverse=True):
            with st.container(border=True):
                st.markdown(f"**{x['date']}｜{x['scene']}**")
                st.write(x.get('action', ''))
                st.write(x.get('result', ''))
                st.caption(f"自己評価：{x['rating']} / 5")

with tabs[3]:
    st.subheader('🧩 スキルを組み合わせて可能性を発見')
    if len(data['skills']) < 2:
        st.info('2つ以上のスキルを登録すると使えるよ。')
    else:
        options = {skill_label(s): s['id'] for s in data['skills']}
        with st.form('new_combination', clear_on_submit=True):
            selected = st.multiselect('組み合わせる武器（2〜3個）', list(options), max_selections=3)
            title = st.text_input('組み合わせ名 *')
            idea = st.text_area('何ができそう？')
            feasibility = st.slider('実現可能性', 1, 5, 3)
            trial = st.text_area('まず試してみたいこと')
            if st.form_submit_button('🧩 組み合わせを保存', type='primary'):
                if len(selected) < 2 or not title.strip():
                    st.warning('2つ以上の武器と組み合わせ名を入力してね。')
                else:
                    add('combinations', dict(skill_ids=[options[x] for x in selected], title=title.strip(), idea=idea, feasibility=feasibility, trial=trial))
    for x in data['combinations']:
        with st.container(border=True):
            st.markdown(f"**✨ {x['title']}**")
            st.caption(' ＋ '.join(get_skill(sid)['name'] for sid in x['skill_ids']))
            st.write(x.get('idea', ''))
            st.caption(f"実現可能性 {x['feasibility']} / 5")
            if x.get('trial'):
                st.write('次の一歩：', x['trial'])

with tabs[4]:
    st.subheader('📚 自分の武器庫')
    query = st.text_input('🔍 名前やできることで検索')
    c1, c2, c3 = st.columns(3)
    with c1:
        category_filter = st.selectbox('カテゴリー', ['すべて'] + CATEGORIES)
    with c2:
        minimum = st.selectbox('習熟度', ['すべて', 'Lv.1以上', 'Lv.2以上', 'Lv.3以上', 'Lv.4以上', 'Lv.5のみ'])
    with c3:
        fav_only = st.checkbox('❤️ お気に入りのみ')
    filtered = []
    for s in data['skills']:
        if query.lower() not in (s['name'] + ' ' + s.get('can_do', '') + ' ' + s.get('use_case', '')).lower():
            continue
        if category_filter != 'すべて' and s['category'] != category_filter:
            continue
        if minimum != 'すべて' and s['level'] < int(minimum[3]):
            continue
        if fav_only and not s.get('favorite'):
            continue
        filtered.append(s)
    st.caption(f'{len(filtered)}件')
    for s in filtered:
        with st.container(border=True):
            st.markdown(f"### {'❤️ ' if s.get('favorite') else ''}{s['name']}")
            st.caption(s['category'])
            st.progress(s['level'] / 5, text=f"習熟度 Lv.{s['level']} / 5")
            st.progress(s['confidence'] / 5, text=f"自信度 {s['confidence']} / 5")
            st.write('できること：', s.get('can_do') or '未記入')
            st.write('活用場面：', s.get('use_case') or '未記入')
            st.caption(f"活用実績 {len(related('evidences', s['id']))}件")

with tabs[5]:
    st.subheader('📈 成長記録と育成目標')
    skill = pick_skill('growth_skill')
    if skill:
        sub1, sub2 = st.tabs(['📈 成長を記録', '🎯 育成目標'])
        with sub1:
            with st.form('new_growth', clear_on_submit=True):
                d = st.date_input('記録日', value=date.today(), max_value=date.today())
                level = st.slider('現在の習熟度', 1, 5, skill['level'])
                confidence = st.slider('現在の自信度', 1, 5, skill['confidence'])
                achievement = st.text_area('新しくできるようになったこと')
                challenge = st.text_area('次の課題')
                if st.form_submit_button('📈 成長を保存', type='primary'):
                    data['growth_logs'].append({'id': uid(), 'created_at': now(), 'skill_id': skill['id'], 'date': str(d), 'level': level, 'confidence': confidence, 'achievement': achievement, 'challenge': challenge})
                    skill['level'], skill['confidence'] = level, confidence
                    save()
                    st.rerun()
            history = sorted(related('growth_logs', skill['id']), key=lambda x: (x['date'], x['created_at']))
            if history:
                df = pd.DataFrame([{'日付': x['date'], '習熟度': x['level'], '自信度': x['confidence']} for x in history])
                st.line_chart(df.set_index('日付'))
                for x in reversed(history):
                    with st.expander(f"{x['date']}｜Lv.{x['level']}｜自信 {x['confidence']}"):
                        st.write('成長：', x.get('achievement') or '未記入')
                        st.write('課題：', x.get('challenge') or '未記入')
        with sub2:
            with st.form('new_goal', clear_on_submit=True):
                title = st.text_input('育成目標 *')
                deadline = st.date_input('期限', value=date.today())
                target_level = st.slider('目標習熟度', 1, 5, min(skill['level'] + 1, 5))
                criteria = st.text_area('達成条件')
                plan = st.text_area('取り組むこと')
                status = st.selectbox('進捗', GOAL_STATUSES)
                if st.form_submit_button('🎯 目標を保存', type='primary'):
                    if not title.strip():
                        st.warning('目標名を入力してね。')
                    else:
                        add('goals', dict(skill_id=skill['id'], title=title.strip(), deadline=str(deadline), target_level=target_level, criteria=criteria, plan=plan, status=status))
            for x in related('goals', skill['id']):
                with st.container(border=True):
                    st.markdown(f"**{x['title']}**　{ x['status'] }")
                    st.caption(f"期限：{x['deadline']}｜目標 Lv.{x['target_level']}")
                    st.write(x.get('criteria', ''))
                    st.write(x.get('plan', ''))

with tabs[6]:
    st.subheader('📊 能力分析ダッシュボード')
    if not data['skills']:
        st.info('スキルを登録すると分析が表示されるよ。')
    else:
        st.markdown('### カテゴリー別スキル数')
        st.bar_chart(pd.Series(Counter(s['category'] for s in data['skills']), name='スキル数'))
        st.markdown('### 習熟度の分布')
        st.bar_chart(pd.Series({f'Lv.{i}': sum(s['level'] == i for s in data['skills']) for i in range(1, 6)}, name='件数'))
        if data['evidences']:
            st.markdown('### 活用実績ランキング')
            counts = Counter(e['skill_id'] for e in data['evidences'])
            df = pd.DataFrame([{'スキル': get_skill(sid)['name'], '実績件数': n} for sid, n in counts.items()])
            st.dataframe(df.sort_values('実績件数', ascending=False), hide_index=True, use_container_width=True)
        if data['growth_logs']:
            st.markdown('### 成長記録の推移（全スキル平均）')
            df = pd.DataFrame([{'日付': x['date'], '習熟度': x['level'], '自信度': x['confidence']} for x in data['growth_logs']])
            st.line_chart(df.groupby('日付')[['習熟度', '自信度']].mean().sort_index())
            st.caption('同じ日に記録したスキルの平均値です。個別の成長推移は「成長・育成」で確認できます。')
        if data['goals']:
            st.markdown('### 目標の進捗')
            st.bar_chart(pd.Series(Counter(g['status'] for g in data['goals']), name='件数'))

with tabs[7]:
    st.subheader('🛠️ 編集・削除・バックアップ')
    labels = {'skills': '⚔️ スキル', 'evidences': '🏆 活用実績', 'combinations': '🧩 組み合わせ', 'growth_logs': '📈 成長記録', 'goals': '🎯 育成目標'}
    table = st.selectbox('編集するデータ', TABLES, format_func=lambda k: labels[k])
    records = data[table]
    if records:
        def record_label(x):
            return f"{x.get('name') or x.get('title') or x.get('scene') or x.get('date') or '記録'} [{x['id'][:8]}]"
        opts = {record_label(x): x['id'] for x in records}
        chosen = st.selectbox('対象の記録', list(opts), key=f'manage_{table}')
        record = next(x for x in records if x['id'] == opts[chosen])
        st.caption('名前・評価・内容などを編集できるよ。関連付けやIDは保護されます。')
        fields = [k for k in record if k not in ('id', 'created_at', 'updated_at', 'skill_id', 'skill_ids')]
        with st.form(f'edit_{table}_{record["id"]}'):
            changes = {}
            for k in fields:
                v = record[k]
                if k == 'category':
                    changes[k] = st.selectbox(k, CATEGORIES, index=CATEGORIES.index(v))
                elif k == 'status':
                    changes[k] = st.selectbox(k, GOAL_STATUSES, index=GOAL_STATUSES.index(v))
                elif isinstance(v, bool):
                    changes[k] = st.checkbox(k, value=v)
                elif isinstance(v, int):
                    changes[k] = st.number_input(k, min_value=1 if k in ('level', 'confidence', 'rating', 'feasibility', 'target_level') else 0, max_value=5 if k in ('level', 'confidence', 'rating', 'feasibility', 'target_level') else None, value=v, step=1)
                elif isinstance(v, str) and k in ('date', 'deadline'):
                    changes[k] = str(st.date_input(k, value=date.fromisoformat(v)))
                else:
                    changes[k] = st.text_area(k, value=str(v or ''))
            if st.form_submit_button('💾 変更を保存', type='primary'):
                if table == 'skills' and not changes.get('name', '').strip():
                    st.warning('スキル名は空にできません。')
                else:
                    record.update(changes)
                    record['updated_at'] = now()
                    save()
                    st.rerun()
        st.warning('スキルを削除すると関連する実績・成長記録・目標・組み合わせも削除されます。')
        confirm = st.checkbox('この記録を削除することを確認しました', key=f'delete_{record["id"]}')
        if st.button('🗑️ 記録を削除', disabled=not confirm):
            delete_record(table, record)
    else:
        st.info('この種類の記録はまだありません。')
    st.divider()
    st.subheader('💾 バックアップ')
    st.download_button('⬇️ JSONバックアップをダウンロード', json.dumps(data, ensure_ascii=False, indent=2), file_name=f'my_weapons_{date.today()}.json', mime='application/json')
    st.subheader('📤 JSONから復元')
    st.warning('復元すると現在の全データが置き換わります。先にバックアップを取ってね。')
    uploaded = st.file_uploader('バックアップJSONを選択', type=['json'])
    if uploaded is not None:
        try:
            restored = validate(json.loads(uploaded.getvalue().decode('utf-8')))
            st.success('データ形式OK：' + ' / '.join(f'{labels[k]} {len(restored[k])}件' for k in TABLES))
            agreed = st.checkbox('現在のデータを置き換えることに同意します')
            if st.button('📤 復元を実行', disabled=not agreed, type='primary'):
                data = restored
                save()
                st.rerun()
        except (UnicodeDecodeError, ValueError, TypeError) as e:
            st.error(f'復元できません：{e}')

st.divider()
st.caption('Day317 / 365 — 自分の可能性を、もっと知ろう。⚔️💎')
