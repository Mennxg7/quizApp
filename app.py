import streamlit as st
import random, json, os

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")

@st.cache_data
def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()

st.set_page_config(page_title="刷题系统", layout="centered")
st.title("刷题系统（Streamlit 版本）")

total = len(questions)
single_count = sum(1 for q in questions if q['qtype']=='single')
multi_count = sum(1 for q in questions if q['qtype']=='multiple')

st.sidebar.markdown("### 题库信息")
st.sidebar.write(f"题目总数: {total}")
st.sidebar.write(f"单选: {single_count}，多选: {multi_count}")

qtype = st.selectbox("选择题型", ["全部", "单选", "多选"])
count = st.number_input("题数", min_value=1, max_value=total, value=min(20, total))
shuffle = st.checkbox("打乱顺序", value=True)

if st.button("开始刷题"):
    if qtype == "单选":
        pool = [q for q in questions if q['qtype']=='single']
    elif qtype == "多选":
        pool = [q for q in questions if q['qtype']=='multiple']
    else:
        pool = questions.copy()
    if shuffle:
        random.shuffle(pool)
    pool = pool[:count]
    # initialize session state
    st.session_state['pool'] = pool
    st.session_state['index'] = 0
    st.session_state['correct'] = 0
    st.session_state['history'] = []

# quiz flow
if 'pool' in st.session_state and st.session_state.get('index',0) < len(st.session_state['pool']):
    q = st.session_state['pool'][st.session_state['index']]
    st.write(f"**第 {st.session_state['index']+1} / {len(st.session_state['pool'])} 题**")
    st.write(q['question'])
    opts = q.get('options', {})
    choices = list(opts.keys())
    choices.sort()
    if q['qtype'] == 'multiple':
        selected = st.multiselect("请选择（多选）", options=choices, format_func=lambda x: f"{x}. {opts[x]}")
    else:
        selected = st.radio("请选择（单选）", options=choices, format_func=lambda x: f"{x}. {opts[x]}")
    if st.button("提交/下一题"):
        user = ','.join(sorted([s.strip().upper() for s in selected])) if isinstance(selected, list) else (selected.strip().upper() if isinstance(selected, str) else '')
        corr = q.get('answer','').upper().replace('，',',')
        user_set = set([x for x in user.split(',') if x])
        corr_set = set([x for x in corr.split(',') if x])
        is_correct = user_set == corr_set
        if is_correct:
            st.session_state['correct'] += 1
        st.session_state['history'].append({'id': q['id'], 'question': q['question'], 'user': user, 'correct': corr, 'is_correct': is_correct})
        st.session_state['index'] += 1
        st.experimental_rerun()

# show results
if 'pool' in st.session_state and st.session_state.get('index',0) >= len(st.session_state['pool']):
    st.success("已完成全部题目！")
    correct = st.session_state.get('correct',0)
    total_done = len(st.session_state['pool'])
    pct = round(100.0 * correct / total_done, 2) if total_done>0 else 0.0
    st.write(f"得分: {correct} / {total_done} （{pct}%）")
    st.write("答题详情：")
    for i, h in enumerate(st.session_state.get('history',[])):
        mark = '✔' if h['is_correct'] else '✖'
        st.write(f"{i+1}. {h['question']}    你的答案: {h['user']}    正确: {h['correct']}    {mark}")
    if st.button("Again !"):
        del st.session_state['pool']
        del st.session_state['index']
        del st.session_state['correct']
        del st.session_state['history']
        st.experimental_rerun()
