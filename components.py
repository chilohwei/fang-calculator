"""
自定义组件模块
"""
import streamlit as st
from theme import THEME

def metric_card(label, value, description=""):
    """显示指标卡片"""
    st.metric(label=label, value=value, delta=description)

def info_card(title, content, type="info"):
    """显示信息卡片"""
    if type == "success":
        st.success(f"**{title}**\n\n{content}")
    elif type == "warning":
        st.warning(f"**{title}**\n\n{content}")
    elif type == "error":
        st.error(f"**{title}**\n\n{content}")
    else:
        st.info(f"**{title}**\n\n{content}")

def validate_input(value, min_value, max_value):
    """验证输入值是否在有效范围内"""
    return min(max(value, min_value), max_value)

def format_currency(amount):
    """格式化货币显示"""
    return f"¥{amount:,.2f}"

def calculate_pressure_level(payment_ratio):
    """计算还款压力等级"""
    if payment_ratio <= 0.3:
        return "轻松", "success"
    elif payment_ratio <= 0.5:
        return "适中", "info"
    elif payment_ratio <= 0.7:
        return "较重", "warning"
    else:
        return "严重", "error"

def generate_loan_advice(monthly_payment, monthly_income, loan_years, total_interest):
    """生成贷款建议"""
    payment_ratio = monthly_payment / monthly_income
    advice = []
    
    if payment_ratio > 0.5:
        advice.append("• 当前月供收入比过高，建议考虑增加首付或延长贷款期限")
    
    if loan_years > 20:
        advice.append("• 贷款期限较长，总支付利息较高，建议在经济条件允许的情况下考虑缩短期限")
    
    if payment_ratio <= 0.3:
        advice.append("• 当前还款压力较小，可以考虑增加月供以减少总利息支出")
    
    if not advice:
        advice.append("• 当前贷款方案较为合理，建议按计划执行")
    
    return "\n".join(advice)
