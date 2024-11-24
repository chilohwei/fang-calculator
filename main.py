import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from theme import THEME, CUSTOM_CSS
from components import (
    metric_card,
    info_card,
    validate_input,
    format_currency,
    calculate_pressure_level,
    generate_loan_advice
)

# 设置页面配置（必须是第一个Streamlit命令）
st.set_page_config(
    page_title="房贷计算器",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用自定义CSS样式
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 侧边栏输入参数
with st.sidebar:
    st.markdown("## 🏠 房贷计算器")
    st.markdown("智能计算您的房贷方案")
    st.markdown("---")

    # 1. 房屋信息
    st.markdown("### 📋 房屋信息")
    
    house_price = st.number_input(
        "房屋总价(万元)",
        min_value=1.0,
        max_value=10000.0,
        value=180.0,
        step=1.0,
        format="%.1f",
        help="请输入房屋总价，单位为万元"
    )

    col1, col2 = st.columns(2)
    with col1:
        down_payment_ratio = st.number_input(
            "首付比例(%)",
            min_value=20,
            max_value=80,
            value=30,
            step=5,
            format="%d",
            help="一般商业贷款最低首付比例为30%，公积金贷款最低20%"
        )
    with col2:
        down_payment = st.text_input(
            "首付金额(万元)",
            value=f"{house_price * down_payment_ratio / 100:.1f}",
            disabled=True,
            help="根据房价和首付比例自动计算"
        )

    loan_amount = st.text_input(
        "贷款金额(万元)",
        value=f"{house_price * (1 - down_payment_ratio / 100):.1f}",
        disabled=True,
        help="贷款金额 = 房屋总价 - 首付金额"
    )

    st.markdown("---")

    # 2. 贷款类型
    st.markdown("### 💰 贷款类型")
    loan_type = st.selectbox(
        "选择贷款类型",
        options=["商业贷款", "公积金贷款", "组合贷款"],
        index=0,
        help="不同贷款类型的利率和政策会有所不同"
    )

    if loan_type == "组合贷款":
        st.markdown("#### 组合贷款配置")
        commercial_ratio = st.slider(
            "商贷比例(%)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            help="商业贷款占总贷款的比例"
        )
        st.text(f"公积金贷款比例: {100 - commercial_ratio}%")

    # 3. 贷款参数
    st.markdown("### ⚙️ 贷款参数")
    
    # 3.1 贷款年限
    loan_years = st.select_slider(
        "贷款年限(年)",
        options=[5, 10, 15, 20, 25, 30],
        value=30,
        help="贷款期限越长，月供越低，但支付的总利息会更多"
    )
    st.text(f"还款期数: {loan_years * 12}期")

    # 3.2 利率设置
    st.markdown("#### 利率设置")
    if loan_type == "商业贷款":
        annual_rate = st.number_input(
            "商贷年利率(%)",
            min_value=2.0,
            max_value=8.0,
            value=3.2,
            step=0.01,
            format="%.2f",
            help="商业贷款基准利率3.20%，可上浮或下浮"
        )
    elif loan_type == "公积金贷款":
        annual_rate = st.number_input(
            "公积金年利率(%)",
            min_value=2.0,
            max_value=4.0,
            value=2.85,
            step=0.01,
            format="%.2f",
            help="公积金贷款利率一般低于商业贷款"
        )
    else:  # 组合贷款
        col1, col2 = st.columns(2)
        with col1:
            commercial_rate = st.number_input(
                "商贷年利率(%)",
                min_value=2.0,
                max_value=8.0,
                value=3.2,
                step=0.01,
                format="%.2f"
            )
        with col2:
            fund_rate = st.number_input(
                "公积金年利率(%)",
                min_value=2.0,
                max_value=4.0,
                value=2.6,
                step=0.01,
                format="%.2f"
            )
        # 计算加权平均利率
        annual_rate = (commercial_rate * commercial_ratio + fund_rate * (100 - commercial_ratio)) / 100
        st.text(f"加权平均年利率: {annual_rate:.2f}%")

    # 4. 还款方式
    st.markdown("### 💳 还款方式")
    payment_method = st.radio(
        "选择还款方式",
        options=["等额本息", "等额本金"],
        index=0,
        help="等额本息每月还款金额固定，等额本金每月还款金额递减"
    )

    # 5. 收入参数
    st.markdown("### 👥 家庭收入")
    income_type = st.radio(
        "收入类型",
        options=["税后月收入", "税前年收入"],
        index=0,
        horizontal=True
    )

    if income_type == "税后月收入":
        monthly_income = st.number_input(
            "税后月收入(元)",
            min_value=1000.0,
            max_value=1000000.0,
            value=20000.0,
            step=1000.0,
            format="%.0f",
            help="填写家庭月总收入（税后）"
        )
    else:
        yearly_income = st.number_input(
            "税前年收入(万元)",
            min_value=1.0,
            max_value=1000.0,
            value=30.0,
            step=1.0,
            format="%.1f",
            help="填写家庭年总收入（税前）"
        )
        monthly_income = yearly_income * 10000 * 0.8 / 12  # 简单估算税后月收入

    # 6. 高级选项
    with st.expander("🔧 高级选项", expanded=False):
        st.markdown("#### 提前还款设置")
        enable_prepayment = st.checkbox(
            "计划提前还款",
            value=False,
            help="设置提前还款计划以计算节省的利息"
        )
        
        if enable_prepayment:
            prepayment_year = st.slider(
                "预计提前还款时间(年)",
                min_value=1,
                max_value=loan_years,
                value=5,
                help="从开始还款算起，预计几年后提前还款"
            )
            prepayment_amount = st.number_input(
                "提前还款金额(万元)",
                min_value=1.0,
                max_value=float(loan_amount),
                value=10.0,
                step=1.0,
                format="%.1f"
            )

        st.markdown("#### 利率调整")
        expect_rate_change = st.checkbox(
            "预期利率调整",
            value=False,
            help="设置预期的利率调整以评估影响"
        )
        
        if expect_rate_change:
            rate_change_year = st.slider(
                "预计调整时间(年)",
                min_value=1,
                max_value=loan_years,
                value=1
            )
            rate_change = st.slider(
                "利率调整幅度(%)",
                min_value=-2.0,
                max_value=2.0,
                value=0.0,
                step=0.1
            )

        st.markdown("#### 收入预期")
        income_growth = st.slider(
            "年收入增长率(%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            help="预期每年的收入增长率"
        )

    # 7. 风险承受度
    st.markdown("### ⚠️ 风险评估")
    risk_tolerance = st.select_slider(
        "风险承受度",
        options=["保守", "稳健", "激进"],
        value="稳健",
        help="影响月供收入比的评估标准"
    )

    # 添加重置按钮
    if st.button("↺ 重置所有参数"):
        st.rerun()

    # 添加版本信息
    st.markdown("---")
    st.markdown("##### v1.0.0 | Made with ❤️ by Chiloh")

# 计算核心指标
loan_amount = house_price * (1 - down_payment_ratio / 100) * 10000
monthly_payment = loan_amount * (annual_rate / 100 / 12) * (1 + annual_rate / 100 / 12)**(loan_years * 12) / ((1 + annual_rate / 100 / 12)**(loan_years * 12) - 1)
payment_ratio = monthly_payment / monthly_income

# 显示核心指标卡片
col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "贷款金额",
        f"{loan_amount/10000:.1f}万元",
        f"首付{house_price * down_payment_ratio / 100:.1f}万元"
    )

with col2:
    metric_card(
        "参考月供",
        f"{monthly_payment:.0f}元",
        f"占收入{payment_ratio:.1%}"
    )

with col3:
    pressure_level, color = calculate_pressure_level(payment_ratio)
    metric_card(
        "还款压力",
        pressure_level,
        "建议月供不超过收入50%"
    )

# 生成还款计划
schedule = []
remaining = loan_amount
total_interest = 0

for i in range(loan_years * 12):
    interest = remaining * (annual_rate / 100 / 12)
    principal = monthly_payment - interest
    remaining = max(0, remaining - principal)
    total_interest += interest
    
    schedule.append({
        '期数': i + 1,
        '月供': monthly_payment,
        '本金': principal,
        '利息': interest,
        '剩余本金': remaining
    })

schedule_df = pd.DataFrame(schedule)

# 成本分析卡片
cost_cols = st.columns(3)
with cost_cols[0]:
    st.info(f"""
        💰 **贷款成本**
        - 贷款总额：{loan_amount/10000:.1f}万元
        - 利息总额：{total_interest/10000:.1f}万元
        - 还款总额：{(loan_amount + total_interest)/10000:.1f}万元
    """)
with cost_cols[1]:
    st.info(f"""
        📊 **月供构成**
        - 月供金额：{monthly_payment:.0f}元
        - 首月本金：{schedule_df.iloc[0]['本金']:.0f}元
        - 首月利息：{schedule_df.iloc[0]['利息']:.0f}元
    """)
with cost_cols[2]:
    st.info(f"""
        📅 **还款周期**
        - 还款期限：{loan_years}年
        - 还款期数：{loan_years * 12}期
        - 年化利率：{annual_rate}%
    """)

# 多维度图表分析
tab1, tab2, tab3, tab4 = st.tabs(["月供构成", "累计收益", "压力分析", "对比分析"])

with tab1:
    # 月供构成趋势图
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=schedule_df['期数'],
        y=schedule_df['本金'],
        name='月供本金',
        fill='tonexty',
        line=dict(color=THEME['primary'])
    ))
    fig1.add_trace(go.Scatter(
        x=schedule_df['期数'],
        y=schedule_df['利息'],
        name='月供利息',
        fill='tonexty',
        line=dict(color=THEME['info'])
    ))
    fig1.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="还款期数",
        yaxis_title="金额（元）",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    # 累计收益分析
    cumsum_df = schedule_df.copy()
    cumsum_df['累计还款'] = cumsum_df['月供'].cumsum()
    cumsum_df['累计本金'] = cumsum_df['本金'].cumsum()
    cumsum_df['累计利息'] = cumsum_df['利息'].cumsum()
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=cumsum_df['期数'],
        y=cumsum_df['累计还款'],
        name='累计还款',
        line=dict(color=THEME['primary'])
    ))
    fig2.add_trace(go.Scatter(
        x=cumsum_df['期数'],
        y=cumsum_df['累计本金'],
        name='累计本金',
        line=dict(color=THEME['success'])
    ))
    fig2.add_trace(go.Scatter(
        x=cumsum_df['期数'],
        y=cumsum_df['累计利息'],
        name='累计利息',
        line=dict(color=THEME['warning'])
    ))
    fig2.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="还款期数",
        yaxis_title="金额（元）",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    # 还款压力分析
    if 'income_growth' in locals():
        years = list(range(loan_years + 1))
        monthly_incomes = [monthly_income * (1 + income_growth/100) ** year for year in years]
        payment_ratios = [(monthly_payment / income) * 100 for income in monthly_incomes]
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=years,
            y=payment_ratios,
            name='月供收入比',
            line=dict(color=THEME['primary'])
        ))
        # 添加压力等级区域
        fig3.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0)
        fig3.add_hrect(y0=30, y1=50, fillcolor="yellow", opacity=0.1, line_width=0)
        fig3.add_hrect(y0=50, y1=100, fillcolor="red", opacity=0.1, line_width=0)
        
        fig3.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="年份",
            yaxis_title="月供收入比(%)",
            yaxis_range=[0, 100],
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # 添加压力等级说明
        st.markdown("""
        压力等级说明：
        - 🟢 <30%：压力较小
        - 🟡 30-50%：压力适中
        - 🔴 >50%：压力较大
        """)

with tab4:
    # 不同还款方式对比
    equal_principal_payments = []
    equal_principal_interests = []
    remaining_principal = loan_amount
    
    for i in range(loan_years * 12):
        principal = loan_amount / (loan_years * 12)
        interest = remaining_principal * (annual_rate / 100 / 12)
        payment = principal + interest
        remaining_principal -= principal
        
        equal_principal_payments.append(payment)
        equal_principal_interests.append(interest)
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=list(range(1, loan_years * 12 + 1)),
        y=[monthly_payment] * (loan_years * 12),
        name='等额本息',
        line=dict(color=THEME['primary'])
    ))
    fig4.add_trace(go.Scatter(
        x=list(range(1, loan_years * 12 + 1)),
        y=equal_principal_payments,
        name='等额本金',
        line=dict(color=THEME['info'])
    ))
    fig4.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="还款期数",
        yaxis_title="月供金额（元）",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # 对比分析说明
    total_interest_equal_installment = total_interest
    total_interest_equal_principal = sum(equal_principal_interests)
    
    st.info(f"""
        💡 **还款方式对比**
        - 等额本息总利息：{total_interest_equal_installment/10000:.1f}万元
        - 等额本金总利息：{total_interest_equal_principal/10000:.1f}万元
        - 利息差额：{(total_interest_equal_installment - total_interest_equal_principal)/10000:.1f}万元
        
        等额本息：每月还款额固定，前期利息占比大，后期本金占比大。
        等额本金：每月本金固定，利息逐月递减，前期还款压力大，但总利息较少。
    """)

# 还款建议
advice = generate_loan_advice(monthly_payment, monthly_income, loan_years, total_interest)
st.success(advice)

# 还款计划明细（可折叠）
if st.checkbox("查看完整还款计划"):
    st.dataframe(
        schedule_df.style.format({
            '月供': '{:.0f}',
            '本金': '{:.0f}',
            '利息': '{:.0f}',
            '剩余本金': '{:.0f}'
        }),
        use_container_width=True
    )
