import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 设置页面配置，包括favicon
st.set_page_config(
    page_title="智能房贷计算器",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': '智能房贷计算器 - 帮助您做出明智的房贷决策'
    }
)

# 添加Umami统计代码
st.markdown("""
    <script defer src="https://tongji.chiloh.com/random-string.js" data-website-id="840ee47d-e2bb-46e7-8692-ed307c567a82"></script>
    """, unsafe_allow_html=True)

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

def calculate_transaction_fees(house_price, deed_tax_rate=0.01, agent_fee_rate=0.02, other_fees=5000):
    deed_tax = house_price * deed_tax_rate
    agent_fee = house_price * agent_fee_rate
    return {
        'deed_tax': deed_tax,
        'agent_fee': agent_fee,
        'other_fees': other_fees,
        'total': deed_tax + agent_fee + other_fees
    }

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

# 输入验证函数
def validate_input(value, min_value, max_value, field_name):
    """验证输入值是否在合法范围内"""
    try:
        value = float(value)
        if value < min_value or value > max_value:
            st.error(f"{field_name}必须在{min_value}到{max_value}之间")
            return False
        return True
    except ValueError:
        st.error(f"{field_name}必须是有效的数字")
        return False

@st.cache_data
def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years):
    """计算月供（使用缓存优化性能）"""
    try:
        monthly_interest_rate = annual_interest_rate / 12 / 100
        num_payments = loan_term_years * 12
        if monthly_interest_rate == 0:
            return loan_amount / num_payments
        return loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / (
                (1 + monthly_interest_rate) ** num_payments - 1)
    except Exception as e:
        st.error(f"计算月供时出错：{str(e)}")
        return None

@st.cache_data
def calculate_equal_installment_schedule(loan_amount, annual_interest_rate, loan_term_years):
    """计算等额本息还款计划（使用缓存优化性能）"""
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

@st.cache_data
def calculate_loan_details(loan_amount, annual_interest_rate, loan_term_years, loan_type, commercial_ratio=None):
    """计算贷款详细信息，支持不同贷款类型"""
    if loan_type == "商业贷款":
        return calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years)
    elif loan_type == "公积金贷款":
        # 公积金利率通常低于商贷利率
        fund_rate = min(3.25, annual_interest_rate)  # 使用3.25%作为公积金贷款的默认利率上限
        return calculate_monthly_payment(loan_amount, fund_rate, loan_term_years)
    else:  # 组合贷款
        commercial_amount = loan_amount * (commercial_ratio / 100)
        fund_amount = loan_amount * ((100 - commercial_ratio) / 100)
        fund_rate = min(3.25, annual_interest_rate)
        
        commercial_payment = calculate_monthly_payment(commercial_amount, annual_interest_rate, loan_term_years)
        fund_payment = calculate_monthly_payment(fund_amount, fund_rate, loan_term_years)
        
        return commercial_payment + fund_payment

@st.cache_data
def calculate_affordability(monthly_income, monthly_payment, risk_tolerance):
    """计算还款压力和可负担能力"""
    payment_ratio = (monthly_payment / monthly_income) * 100
    
    risk_thresholds = {
        '保守': {'safe': 30, 'warning': 40},
        '稳健': {'safe': 40, 'warning': 50},
        '激进': {'safe': 50, 'warning': 60}
    }
    
    thresholds = risk_thresholds[risk_tolerance]
    
    if payment_ratio <= thresholds['safe']:
        return '安全', payment_ratio
    elif payment_ratio <= thresholds['warning']:
        return '警告', payment_ratio
    else:
        return '危险', payment_ratio

@st.cache_data
def calculate_extra_payment_impact(loan_amount, annual_interest_rate, loan_term_years, extra_payment_yearly):
    """计算额外还款的影响"""
    monthly_payment = calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years)
    original_schedule = calculate_equal_installment_schedule(loan_amount, annual_interest_rate, loan_term_years)
    total_interest_original = sum(month['利息'] for month in original_schedule)
    
    # 计算每年额外还款后的新还款计划
    remaining_principal = loan_amount
    total_interest_with_extra = 0
    years_to_repay = loan_term_years
    
    for year in range(loan_term_years):
        # 计算当年的利息
        yearly_interest = remaining_principal * (annual_interest_rate / 100)
        total_interest_with_extra += yearly_interest
        
        # 扣除正常还款和额外还款
        yearly_payment = monthly_payment * 12
        remaining_principal -= (yearly_payment - yearly_interest)  # 扣除正常还款中的本金部分
        remaining_principal -= (extra_payment_yearly * 10000)  # 扣除额外还款（万元转换为元）
        
        if remaining_principal <= 0:
            years_to_repay = year + 1
            break
    
    savings = total_interest_original - total_interest_with_extra
    time_saved = loan_term_years - years_to_repay
    
    return {
        '节省利息': savings,
        '缩短年限': time_saved,
        '原始总利息': total_interest_original,
        '新总利息': total_interest_with_extra
    }

@st.cache_data
def project_future_payment_pressure(monthly_payment, monthly_income, income_growth_rate, loan_term_years):
    """预测未来还款压力变化"""
    try:
        years = list(range(loan_term_years + 1))
        payment_to_income_ratios = []
        
        for year in years:
            # 计算该年的月收入（考虑年增长率）
            projected_monthly_income = monthly_income * (1 + income_growth_rate/100) ** year
            # 计算月供收入比
            if projected_monthly_income > 0:  # 添加除数检查
                ratio = (monthly_payment / projected_monthly_income) * 100  # 转换为百分比
                payment_to_income_ratios.append(ratio)
            else:
                payment_to_income_ratios.append(0)
        
        return years, payment_to_income_ratios
    except Exception as e:
        st.error(f"计算未来还款压力时出错：{str(e)}")
        return [], []

# 侧边栏：基本信息输入
with st.sidebar:
    st.title('🏠 智能房贷计算器 💰')
    
    # 房屋总价和首付
    house_price = st.number_input('房屋总价（万元）', min_value=1, max_value=10000, value=300)
    down_payment = st.number_input('首付金额（万元）', min_value=0, max_value=house_price, value=int(house_price * 0.3))
    
    # 交易费用设置
    with st.expander("🏷️ 交易费用设置"):
        st.markdown("### 交易费用详情")
        deed_tax_rate = st.slider('契税税率 (%)', 0.0, 5.0, 1.0, 0.1, format="%0.1f%%") / 100
        agent_fee_rate = st.slider('中介费率 (%)', 0.0, 5.0, 2.0, 0.1, format="%0.1f%%") / 100
        other_fees = st.number_input('其他费用 (元)', 0, 100000, 5000, 1000)
        
        # 计算并显示交易费用明细
        fees = calculate_transaction_fees(house_price * 10000, deed_tax_rate, agent_fee_rate, other_fees)
        st.markdown("#### 费用明细")
        st.markdown(f"- 契税：{fees['deed_tax']:,.2f}元 ({deed_tax_rate*100:.1f}%)")
        st.markdown(f"- 中介费：{fees['agent_fee']:,.2f}元 ({agent_fee_rate*100:.1f}%)")
        st.markdown(f"- 其他费用：{fees['other_fees']:,.2f}元")
        st.markdown(f"**总交易费用：{fees['total']:,.2f}元**")
    
    # 贷款类型选择
    loan_type = st.selectbox('贷款类型', ['商业贷款', '公积金贷款', '组合贷款'])
    
    if loan_type == '商业贷款':
        annual_interest_rate = st.number_input('商贷年利率（%）', min_value=0.0, max_value=15.0, value=3.2, step=0.05)
    elif loan_type == '公积金贷款':
        annual_interest_rate = st.number_input('公积金年利率（%）', min_value=0.0, max_value=15.0, value=2.85, step=0.05)
    else:
        st.write('组合贷款配置：')
        commercial_ratio = st.slider('商贷比例（%）', min_value=0, max_value=100, value=50, step=5)
        commercial_rate = st.number_input('商贷年利率（%）', min_value=0.0, max_value=15.0, value=3.2, step=0.05)
        fund_rate = st.number_input('公积金年利率（%）', min_value=0.0, max_value=15.0, value=2.85, step=0.05)
        annual_interest_rate = (commercial_rate * commercial_ratio + fund_rate * (100 - commercial_ratio)) / 100

    # 贷款期限和还款方式
    loan_term_years = st.selectbox('贷款期限（年）', [10, 15, 20, 25, 30], index=4)
    repayment_method = st.selectbox('还款方式', ['等额本息', '等额本金'])
    
    # 高级选项
    with st.expander("高级选项"):
        risk_tolerance = st.slider('风险承受能力', min_value=1, max_value=5, value=3, 
                                 help='1=保守，5=激进')
        monthly_income = st.number_input('月收入（元）', min_value=0, value=20000)
        income_growth_rate = st.slider('预期年收入增长率（%）', min_value=0, max_value=20, value=5)
        extra_payment_yearly = st.number_input('每年额外还款（万元）', min_value=0, value=0)
    
    calculate_button = st.button('立即计算', use_container_width=True)

# 主要内容区域
if calculate_button:
    if not validate_input(house_price, 1, 10000, "房屋总价"):
        st.stop()
    if not validate_input(annual_interest_rate, 0, 15, "年利率"):
        st.stop()

    try:
        loan_amount = house_price - down_payment
        
        # 顶部信息区域
        st.header("贷款方案概览")
        
        # 基本信息和关键指标
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("贷款总额", f"{loan_amount:.2f}万元")
        with col2:
            st.metric("首付金额", f"{down_payment:.2f}万元")
        with col3:
            st.metric("首付比例", f"{(down_payment/house_price*100):.1f}%")
            
        # 计算月供
        equal_installment = calculate_monthly_payment(loan_amount * 10000, annual_interest_rate, loan_term_years)
        equal_principal_schedule = calculate_equal_principal_schedule(loan_amount * 10000, annual_interest_rate, loan_term_years)
        first_month_equal_principal = equal_principal_schedule[0]['月供']
        last_month_equal_principal = equal_principal_schedule[-1]['月供']

        # 月供信息展示
        st.subheader("月供详情")
        payment_comparison = pd.DataFrame({
            '还款方式': ['等额本息', '等额本金(首月)', '等额本金(末月)'],
            '月供金额': [
                f"{equal_installment:.2f}元",
                f"{first_month_equal_principal:.2f}元",
                f"{last_month_equal_principal:.2f}元"
            ]
        })
        st.dataframe(payment_comparison, hide_index=True)

        # 如果选择计算交易费用
        fees = calculate_transaction_fees(house_price * 10000, deed_tax_rate, agent_fee_rate, other_fees)
        st.info(f"""
        💰 交易费用估算：
        - 契税：{fees['deed_tax']:,.2f}元 ({deed_tax_rate*100:.1f}%)
        - 中介费：{fees['agent_fee']:,.2f}元 ({agent_fee_rate*100:.1f}%)
        - 其他费用：{fees['other_fees']:,.2f}元
        - 总交易费用：{fees['total']:,.2f}元
        """)

        # 还款压力分析（如果提供了月收入）
        if monthly_income > 0:
            st.subheader("还款压力评估")
            payment_pressure = (equal_installment / monthly_income) * 100
            if payment_pressure <= 30:
                st.success(f"📈 当前月供收入比为{payment_pressure:.1f}%，还款压力适中")
            elif payment_pressure <= 50:
                st.warning(f"⚠️ 当前月供收入比为{payment_pressure:.1f}%，还款压力较大")
            else:
                st.error(f"🚨 当前月供收入比为{payment_pressure:.1f}%，还款压力过大，请谨慎考虑")

        # 图表区域
        st.header("还款计划可视化")
        
        # 计算两种还款方式的数据
        equal_installment_schedule = calculate_equal_installment_schedule(loan_amount * 10000, annual_interest_rate, loan_term_years)
        equal_principal_schedule = calculate_equal_principal_schedule(loan_amount * 10000, annual_interest_rate, loan_term_years)
        
        # 创建还款方式对比图表
        fig = go.Figure()
        
        # 等额本息
        ei_df = pd.DataFrame(equal_installment_schedule)
        fig.add_trace(go.Scatter(
            x=ei_df['月份'],
            y=ei_df['月供'],
            name='等额本息',
            line=dict(color='#1f77b4')
        ))
        
        # 等额本金
        ep_df = pd.DataFrame(equal_principal_schedule)
        fig.add_trace(go.Scatter(
            x=ep_df['月份'],
            y=ep_df['月供'],
            name='等额本金',
            line=dict(color='#ff7f0e')
        ))
        
        fig.update_layout(
            title='月供变化趋势对比',
            xaxis_title='还款月数',
            yaxis_title='月供金额（元）',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # 收入增长预期下的还款压力变化
        if monthly_income > 0:
            st.subheader("未来还款压力预测")
            future_pressure = project_future_payment_pressure(equal_installment, monthly_income, income_growth_rate, loan_term_years)
            years, payment_to_income_ratios = future_pressure
            pressure_df = pd.DataFrame({
                '年份': years,
                '月供收入比': payment_to_income_ratios
            })
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=pressure_df['年份'],
                y=pressure_df['月供收入比'],
                name='月供收入比',
                line=dict(color='#2ecc71')
            ))
            
            fig2.update_layout(
                title='未来还款压力趋势',
                xaxis_title='年份',
                yaxis_title='月供收入比（%）',
                hovermode='x unified'
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 展示详细的还款计划
        with st.expander("查看详细还款计划"):
            st.subheader("还款计划详情")
            if repayment_method == '等额本息':
                schedule_df = pd.DataFrame(equal_installment_schedule)
            else:
                schedule_df = pd.DataFrame(equal_principal_schedule)
            
            # 转换为更易读的格式
            schedule_df['月供'] = schedule_df['月供'].round(2)
            schedule_df['本金'] = schedule_df['本金'].round(2)
            schedule_df['利息'] = schedule_df['利息'].round(2)
            schedule_df['剩余本金'] = schedule_df['剩余本金'].round(2)
            
            # 显示表格
            st.dataframe(schedule_df)
            
            # 添加下载按钮
            csv = schedule_df.to_csv(index=False)
            st.download_button(
                label="下载还款计划表",
                data=csv,
                file_name="还款计划.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"计算过程中出现错误：{str(e)}")
        st.info("请检查输入数据是否正确，如果问题持续存在，请刷新页面重试。")
        st.stop()

else:
    st.markdown(
        """
        <div class='center-content'>
            <h2>🏠 智能房贷计算器</h2>
            <p>开始输入你的房贷信息，然后点击"立即计算"按钮查看详细分析结果。</p>
            <p>支持商业贷款、公积金贷款和组合贷款计算</p>
            <p>提供多种还款方案对比和未来还款压力分析</p>
        </div>
        """,
        unsafe_allow_html=True
    )
