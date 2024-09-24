import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 设置页面配置，包括favicon
st.set_page_config(page_title="智能房贷计算器", page_icon="🏠", layout="wide")

# 样式设置
st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stSelectbox > div > div > select {
        font-size: 16px;
    }
    .stSlider > div > div > div > div {
        font-size: 16px;
    }
    .stButton > button {
        font-size: 16px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .formula {
        font-family: monospace;
        background-color: #e6e6e6;
        padding: 5px;
        border-radius: 3px;
    }
    .stDataFrame {
        width: 100% !important;
    }
    .bounce {
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-30px);
        }
        60% {
            transform: translateY(-15px);
        }
    }
    .center-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        color: #888;
        text-align: center;
    }
    .recommendation {
        background-color: #e6f3ff;
        border-left: 5px solid #2196F3;
        padding: 10px;
        margin-bottom: 10px;
    }
    .tips {
        background-color: #fff9e6;
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 计算函数
def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    num_payments = loan_term_years * 12
    if monthly_interest_rate == 0:
        return loan_amount / num_payments
    return loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / (
            (1 + monthly_interest_rate) ** num_payments - 1)

def calculate_equal_installment_schedule(loan_amount, annual_interest_rate, loan_term_years):
    monthly_payment = calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years)
    schedule = []
    remaining_balance = loan_amount
    monthly_interest_rate = annual_interest_rate / 12 / 100

    for month in range(1, loan_term_years * 12 + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        schedule.append({
            '月份': month,
            '月供': monthly_payment,
            '本金': principal_payment,
            '利息': interest_payment,
            '剩余本金': remaining_balance
        })
    return schedule

def calculate_equal_principal_schedule(loan_amount, annual_interest_rate, loan_term_years):
    monthly_principal = loan_amount / (loan_term_years * 12)
    schedule = []
    remaining_balance = loan_amount
    monthly_interest_rate = annual_interest_rate / 12 / 100

    for month in range(1, loan_term_years * 12 + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        monthly_payment = monthly_principal + interest_payment
        remaining_balance -= monthly_principal
        schedule.append({
            '月份': month,
            '月供': monthly_payment,
            '本金': monthly_principal,
            '利息': interest_payment,
            '剩余本金': remaining_balance
        })
    return schedule

def calculate_transaction_fees(house_price):
    deed_tax = house_price * 0.03
    agent_fee = house_price * 0.02
    other_fees = 5000
    return deed_tax + agent_fee + other_fees

def find_best_loan_strategy(house_price, down_payment_min, down_payment_max, loan_term_options, annual_interest_rate):
    best_strategy = None
    min_monthly_payment = float('inf')

    for down_payment in np.arange(down_payment_min, down_payment_max + 1, 10000):
        for loan_term in loan_term_options:
            loan_amount = house_price - down_payment
            monthly_payment = calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term)

            if monthly_payment < min_monthly_payment:
                min_monthly_payment = monthly_payment
                best_strategy = {
                    'down_payment': down_payment,
                    'loan_term': loan_term,
                    'monthly_payment': monthly_payment,
                    'loan_amount': loan_amount
                }

    return best_strategy

# 侧边栏：基本信息输入
with st.sidebar:
    st.title('🏠 智能房贷计算器 💰')
    st.header('基本信息')
    house_price = st.number_input('房产总价 (万元)', min_value=10, max_value=5000, value=160, step=10) * 10000
    down_payment_min = st.number_input('最低首付金额 (万元)', min_value=0, max_value=int(house_price / 10000),
                                       value=int(house_price * 0.2 / 10000), step=10) * 10000
    down_payment_max = st.number_input('最高首付金额 (万元)', min_value=int(down_payment_min / 10000),
                                       max_value=int(house_price / 10000), value=int(house_price * 0.4 / 10000),
                                       step=10) * 10000
    property_type = st.selectbox('房产类型', ['新房', '二手房'])
    house_status = st.selectbox('房产状态', ['首套房', '二套房'])
    loan_term_options = [10, 15, 20, 25, 30]
    loan_type = st.radio('贷款类型', ['商业贷款', '公积金贷款', '组合贷款'])

    # 根据选择自动填写默认利率
    if loan_type == '商业贷款':
        if house_status == '首套房':
            default_interest_rate = 3.55
        else:
            default_interest_rate = 3.9
    elif loan_type == '公积金贷款':
        if house_status == '首套房':
            default_interest_rate = 2.85
        else:
            default_interest_rate = 3.325
    else:
        if house_status == '首套房':
            default_interest_rate = 2.85 * 0.5 + 3.55 * 0.5  # 组合贷款的利率为比例加权平均
        else:
            default_interest_rate = 3.325 * 0.5 + 3.9 * 0.5  # 组合贷款的利率为比例加权平均

    annual_interest_rate = st.number_input('年利率 (%)', min_value=2.0, max_value=10.0, value=default_interest_rate,
                                           step=0.01)
    calculate_button = st.button('立即计算')

# 主界面：计算结果展示
if calculate_button:
    st.subheader('最佳贷款策略')

    best_strategy = find_best_loan_strategy(house_price, down_payment_min, down_payment_max, loan_term_options, annual_interest_rate)

    st.markdown(f"""
    <div class="recommendation">
        <h4>推荐方案：</h4>
        <p>首付金额: <b>{best_strategy['down_payment'] / 10000:.2f}</b> 万元 (首付比例: <b>{best_strategy['down_payment'] / house_price * 100:.2f}%</b>)</p>
        <p>贷款金额: <b>{best_strategy['loan_amount'] / 10000:.2f}</b> 万元</p>
        <p>贷款期限: <b>{best_strategy['loan_term']}</b> 年</p>
        <p>每月还款: <b>{best_strategy['monthly_payment']:.2f}</b> 元</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tips">
        <h4>为什么选择这个方案？</h4>
        <ul>
            <li>在满足您设定的首付范围内，这个方案可以使每月还款额最低。</li>
            <li>较长的贷款期限可以降低月供压力，但也意味着总利息支出会增加。</li>
            <li>这个方案在首付、贷款期限和月供之间取得了较好的平衡。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader('贷款概况')

    loan_amount = best_strategy['loan_amount']
    loan_term_years = best_strategy['loan_term']
    best_down_payment = best_strategy['down_payment']
    transaction_fees = calculate_transaction_fees(house_price)
    leverage_ratio = loan_amount / (best_down_payment + transaction_fees) * 100  # 转换为百分比

    st.markdown(f"""
    <div class="info-box">
        <p>首付金额: <b>{best_down_payment / 10000:.2f}</b> 万元 (首付比例: <b>{best_down_payment / house_price * 100:.2f}%</b>)</p>
        <p>贷款金额: <b>{loan_amount / 10000:.2f}</b> 万元</p>
        <p>交易费用: <b>{transaction_fees / 10000:.2f}</b> 万元</p>
        <p>杠杆率: <b>{leverage_ratio:.2f}%</b></p>
    </div>

    <p>计算公式：</p>
    <p class="formula">首付金额 = 房产总价 × 首付比例</p>
    <p class="formula">贷款金额 = 房产总价 - 首付金额</p>
    <p class="formula">交易费用 = 契税 + 中介费 + 其他费用</p>
    <p class="formula">杠杆率 = 贷款金额 / (首付金额 + 交易费用) × 100%</p>
    """, unsafe_allow_html=True)

    st.subheader('贷款建议')
    st.markdown(f"""
    根据您提供的信息，我们建议的最佳贷款策略如上所示。以下是一些额外的建议：
    """)

    if leverage_ratio > 400:
        st.warning('您的杠杆率较高，请注意控制风险。考虑增加首付比例或选择更便宜的房产。')
    elif leverage_ratio < 200:
        st.success('您的杠杆率较低，财务状况良好。可以考虑增加投资多元化，或选择更高质量的房产。')
    else:
        st.info('您的杠杆率处于合理范围。请确保月供不超过家庭收入的30%。')

    if loan_term_years > 20:
        st.info('长期贷款可以降低月供压力，但总利息较高。如果经济条件允许，可以考虑提前还款以减少利息支出。')

    if loan_type == '组合贷款':
        st.info('组合贷款可以平衡利率，但请注意公积金贷款额度限制和申请流程可能更复杂。')

    st.subheader('还款方式对比')
    # 还款方式对比
    equal_installment_schedule = calculate_equal_installment_schedule(loan_amount, annual_interest_rate, loan_term_years)
    equal_principal_schedule = calculate_equal_principal_schedule(loan_amount, annual_interest_rate, loan_term_years)

    data = {
        '还款方式': ['等额本息', '等额本金'],
        '首月还款': [equal_installment_schedule[0]['月供'], equal_principal_schedule[0]['月供']],
        '末月还款': [equal_installment_schedule[-1]['月供'], equal_principal_schedule[-1]['月供']],
        '总利息': [sum(month['利息'] for month in equal_installment_schedule),
                   sum(month['利息'] for month in equal_principal_schedule)]
    }
    df = pd.DataFrame(data)
    df['首月还款'] = df['首月还款'].apply(lambda x: f"{x:.2f}")
    df['末月还款'] = df['末月还款'].apply(lambda x: f"{x:.2f}")
    df['总利息'] = df['总利息'].apply(lambda x: f"{x / 10000:.2f}万")

    st.table(df.set_index('还款方式'))
    st.markdown("""
    **建议：**
    1. 如果您的收入稳定且预期不会有大幅增长，可以选择等额本息，便于长期规划。
    2. 如果您预期未来收入会持续增长，可以选择等额本金，减少总利息支出。
    3. 无论选择哪种方式，都要确保月供不超过家庭收入的30%，以防止过高的还款压力。
    4. 如果经济条件允许，可以考虑选择等额本金，并在前期做好资金储备，以应对较高的月供。
    """)


    def plot_repayment_schedule(df, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['月供'],
            name='月供',
            line=dict(color='blue'),
            hovertemplate='月份: %{x}<br>月供: ¥%{y:.2f}'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['本金'],
            name='本金',
            line=dict(color='green'),
            hovertemplate='月份: %{x}<br>本金: ¥%{y:.2f}'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['利息'],
            name='利息',
            line=dict(color='red'),
            hovertemplate='月份: %{x}<br>利息: ¥%{y:.2f}'
        ))
        fig.update_layout(
            title=title,
            xaxis_title='月份',
            yaxis_title='金额 (元)',
            hovermode='x unified',
            hoverlabel=dict(bgcolor="white", font_size=12),
            yaxis=dict(tickformat=',.0f')
        )
        return fig


    def display_schedule(df, title):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(df.style.format({
                '月供': '{:.2f}',
                '本金': '{:.2f}',
                '利息': '{:.2f}',
                '剩余本金': '{:.2f}'
            }))
        with col2:
            st.plotly_chart(plot_repayment_schedule(df, title), use_container_width=True)


    df_equal_installment = pd.DataFrame(equal_installment_schedule)
    df_equal_installment['月份'] = df_equal_installment['月份'].astype(int)
    df_equal_installment = df_equal_installment.set_index('月份')

    df_equal_principal = pd.DataFrame(equal_principal_schedule)
    df_equal_principal['月份'] = df_equal_principal['月份'].astype(int)
    df_equal_principal = df_equal_principal.set_index('月份')

    tab1, tab2 = st.tabs(["等额本息还款计划", "等额本金还款计划"])
    with tab1:
        display_schedule(df_equal_installment, '等额本息还款计划')
    with tab2:
        display_schedule(df_equal_principal, '等额本金还款计划')

else:
    st.markdown(
        """
        <div class='center-content'>
            <p>开始输入你的房贷信息，然后点击"立即计算"按钮查看详细结果。</p>
            <p>我们将为您提供：</p>
            <ul>
                <li>最佳贷款策略</li>
                <li>贷款概况分析</li>
                <li>个性化贷款建议</li>
                <li>还款方式对比</li>
                <li>详细还款计划</li>
            </ul>
            <p>让我们帮助您做出明智的房贷决策!</p>
        </div>
        """,
        unsafe_allow_html=True
    )
