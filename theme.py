"""
主题配置文件
"""

THEME = {
    'primary': '#1f77b4',
    'success': '#2ecc71',
    'warning': '#f1c40f',
    'error': '#e74c3c',
    'info': '#3498db'
}

CUSTOM_CSS = f"""
<style>
.stMetric {{
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
}}

.stMetric:hover {{
    box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
}}

div[data-testid="stMetricValue"] {{
    font-size: 2rem;
    font-weight: bold;
}}

div[data-testid="stMetricDelta"] {{
    font-size: 1rem;
    color: #666;
}}

.stAlert {{
    border-radius: 0.5rem;
    margin: 1rem 0;
}}
</style>
"""
