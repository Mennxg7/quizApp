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

# 侧边栏信息
total = len(questions)
single_count = sum(1 for q in questions if q['qtype'] == 'single')
multi_count = sum(1 for q in questions if q['qtype'] == 'multiple')

st.sidebar.markdown("### 题库信息")
st.sidebar.write(f"题目总数: {total}")
st.sidebar.write(f"单选: {single_count}，多选: {multi_count}")

# 选择与启动
qtype = st.selectbox("选择题型", ["全部", "单选", "多选"])
count = st.number_input("题数", min_value=1, max_value=total, value=min(20, total))
shuffle = st.checkbox("打乱顺序", value=True)

if st.button("开始刷题"):
    if qtype == "单选":
        pool = [q for q in questions if q['qtype'] == 'single']
    elif qtype == "多选":
        pool = [q for q in questions if q['qtype'] == 'multiple']
    else:
        pool = questions.copy()

    if shuffle:
        random.shuffle(pool)
    pool = pool[:count]

    st.session_state['pool'] = pool
    st.session_state['index'] = 0
    st.session_state['correct'] = 0
    st.session_state['history'] = []
    st.session_state['show_feedback'] = False   # 是否显示当前题反馈（答错时）
    st.session_state['feedback_correct'] = ""   # 当前题正确答案（字符串，如 "A,B"）
    st.session_state['last_user_answer'] = ""   # 当前题用户答案字符串
    st.rerun()

# 主作答区
if 'pool' in st.session_state and st.session_state.get('index', 0) < len(st.session_state['pool']):
    idx = st.session_state['index']
    q = st.session_state['pool'][idx]

    st.write(f"**第 {idx + 1} / {len(st.session_state['pool'])} 题**")
    st.write(q['question'])
    opts = q.get('options', {})
    choices = list(opts.keys())
    choices.sort()

    if not choices:
        st.warning("本题没有选项数据，请检查题库。")
    else:
        # 当显示反馈时，禁用选择控件
        disabled = bool(st.session_state.get('show_feedback', False))

        # 渲染选择控件
        if q['qtype'] == 'multiple':
            selected = st.multiselect(
                "请选择（多选）",
                options=choices,
                format_func=lambda x: f"{x}. {opts[x]}",
                disabled=disabled
            )
        else:
            selected = st.radio(
                "请选择（单选）",
                options=choices,
                format_func=lambda x: f"{x}. {opts[x]}",
                disabled=disabled,
                index=None  # 默认不选
            )

        # 如果在显示反馈（答错场景），展示正确答案并提供“下一题”按钮
        if st.session_state.get('show_feedback', False):
            corr = st.session_state.get('feedback_correct', '')
            corr_set = [x for x in corr.split(',') if x]
            # 组合“正确答案：A. 文本, B. 文本”这样的展示
            corr_text = "，".join([f"{c}. {opts.get(c, '')}" for c in corr_set])
            st.error(f"答错啦，正确答案是：{corr}（{corr_text}）")

            if st.button("下一题"):
                # 跳到下一题并清理反馈状态
                st.session_state['index'] += 1
                st.session_state['show_feedback'] = False
                st.session_state['feedback_correct'] = ""
                st.session_state['last_user_answer'] = ""
                st.rerun()
        else:
            # 提交按钮（未显示反馈时才出现）
            if st.button("提交"):
                # 统一字符串化
                if isinstance(selected, list):
                    user = ','.join(sorted([s.strip().upper() for s in selected]))
                elif isinstance(selected, str) and selected:
                    user = selected.strip().upper()
                else:
                    user = ""  # 未选择视为空

                corr = q.get('answer', '').upper().replace('，', ',')
                user_set = set([x for x in user.split(',') if x])
                corr_set = set([x for x in corr.split(',') if x])
                is_correct = user_set == corr_set

                # 记录历史（每题只记一次）
                st.session_state['history'].append({
                    'id': q.get('id'),
                    'question': q['question'],
                    'user': user,
                    'correct': corr,
                    'is_correct': is_correct
                })

                if is_correct:
                    st.session_state['correct'] += 1
                    st.session_state['index'] += 1
                    st.rerun()
                else:
                    # 展示反馈但不前进，等用户手动点“下一题”
                    st.session_state['show_feedback'] = True
                    st.session_state['feedback_correct'] = corr
                    st.session_state['last_user_answer'] = user
                    st.rerun()

# 完成页
if 'pool' in st.session_state and st.session_state.get('index', 0) >= len(st.session_state['pool']):
    st.success("已完成全部题目！")
    correct = st.session_state.get('correct', 0)
    total_done = len(st.session_state['pool'])
    pct = round(100.0 * correct / total_done, 2) if total_done > 0 else 0.0
    st.write(f"得分: {correct} / {total_done} （{pct}%）")
    st.write("答题详情：")
    for i, h in enumerate(st.session_state.get('history', [])):
        mark = '✔' if h['is_correct'] else '✖'
        st.write(f"{i + 1}. {h['question']}    你的答案: {h['user']}    正确: {h['correct']}    {mark}")

    if st.button("再来一轮"):
        for key in ['pool', 'index', 'correct', 'history', 'show_feedback', 'feedback_correct', 'last_user_answer']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
