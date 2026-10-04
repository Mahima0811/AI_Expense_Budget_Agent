"""
AI Expense & Budget Intelligence
Multi-Agent Personal Finance Decision Support System
"""

import time
import tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import analytics
import agents

# ---------------------------------------------------------
# Page Config & High-End Dark Fintech Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Expense & Budget Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* 1. Eliminate blank white header space */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Dark Fintech Core App Theme */
    .stApp {
        background-color: #0b0f17;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Hero Header Container */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
    }

    /* Equal-Height KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 16px;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        box-sizing: border-box;
        margin-bottom: 12px;
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-value {
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .text-emerald { color: #34d399; }
    .text-rose { color: #f87171; }
    .text-blue { color: #60a5fa; }
    .text-slate { color: #94a3b8; }
    
    /* Workflow Agent Cards (Role, Input, Process, Output, Status) */
    .workflow-card-detailed {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 18px;
        min-height: 230px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }
    .agent-field {
        font-size: 0.78rem;
        color: #cbd5e1;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .agent-field-label {
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.4px;
    }
    
    /* Status Badges */
    .badge-completed {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-running {
        background: rgba(59, 130, 246, 0.25);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.5);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-waiting {
        background: rgba(107, 114, 128, 0.2);
        color: #9ca3af;
        border: 1px solid rgba(107, 114, 128, 0.4);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-failed {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
    
    /* Data Handoff Banner */
    .handoff-banner {
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 10px;
        padding: 12px 18px;
        color: #93c5fd;
        font-size: 0.88rem;
        font-weight: 600;
        margin: 14px 0;
        text-align: center;
    }

    /* Action Card */
    .action-card {
        background: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .action-number {
        font-size: 1.1rem;
        font-weight: 800;
        color: #10B981;
        margin-right: 8px;
    }

    /* Footer */
    .footer-container {
        text-align: center;
        padding: 25px 10px;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 35px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: CONTROL CENTER
# ---------------------------------------------------------
st.sidebar.title("🎛️ CONTROL CENTER")
st.sidebar.caption("Multi-Agent Financial Intelligence")
st.sidebar.markdown("---")

st.sidebar.subheader("📂 Transaction Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Expense CSV", type=["csv"])
st.sidebar.caption("Default: sample_data.csv (61 Days)")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Financial Parameters")
curr_choice = st.sidebar.selectbox("Currency", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"], index=0)
symbol = curr_choice.split("(")[1].replace(")", "")

monthly_income = st.sidebar.number_input("Monthly Income", min_value=1000.0, value=100000.0, step=5000.0)
monthly_budget = st.sidebar.number_input("Monthly Budget", min_value=1000.0, value=50000.0, step=5000.0)

st.sidebar.markdown("---")
run_analysis_btn = st.sidebar.button("🚀 RUN AI ANALYSIS", width="stretch", type="primary")

# ---------------------------------------------------------
# Data Loading & Validation
# ---------------------------------------------------------
def get_csv_filepath():
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.getvalue())
            return tmp.name
    return "sample_data.csv"

data_file = get_csv_filepath()

try:
    preview_df = analytics.load_transactions(data_file)
    valid_data = True
except Exception as err:
    valid_data = False
    st.error(f"❌ Invalid Dataset Error: {str(err)}")
    st.stop()

# ---------------------------------------------------------
# 1. HEADER HERO SECTION
# ---------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div>
                <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #f8fafc;">AI Expense & Budget Intelligence</h1>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 1.0rem;">Multi-Agent Personal Finance Decision Support</p>
            </div>
            <div>
                <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px 18px; border-radius: 30px; font-size: 0.85rem; font-weight: 600;">
                    ● System Ready | Python Analytics Active | 4-Agent Orchestration Ready
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Helper function to render high-contrast, equal-height KPI cards
def render_kpi_card(title, value, subtitle="", text_color_class="text-blue", is_html=False):
    val_content = value if is_html else f'<div class="kpi-value">{value}</div>'
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            {val_content}
            <div class="kpi-sub {text_color_class}">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# 2. DATASET OVERVIEW (Exactly 4 Equal Cards)
# ---------------------------------------------------------
st.markdown("## 📋 DATASET OVERVIEW")
ov1, ov2, ov3, ov4 = st.columns(4)

with ov1:
    render_kpi_card("TOTAL TRANSACTIONS", f"{len(preview_df)}", "transactions", "text-blue")
with ov2:
    start_date = preview_df["date"].min().strftime("%b %d, %Y")
    end_date = preview_df["date"].max().strftime("%b %d, %Y")
    date_html = f'<div style="font-size: 0.90rem; font-weight: 800; color: #ffffff; line-height: 1.25; white-space: nowrap;">{start_date}<br><span style="color: #60a5fa; font-weight: 700;">→</span> {end_date}</div>'
    render_kpi_card("DATA PERIOD", date_html, "Multi-Month Span", "text-slate", is_html=True)
with ov3:
    total_val = preview_df["amount"].sum()
    render_kpi_card("HISTORICAL SPEND", f"{symbol}{total_val:,.0f}", "Historical spend", "text-emerald")
with ov4:
    cat_count = preview_df['category'].nunique()
    render_kpi_card("CATEGORIES TRACKED", f"{cat_count}", "expense groups", "text-blue")

with st.expander("🔍 Preview Transaction Source Data", expanded=False):
    st.dataframe(preview_df.head(15), width="stretch")

st.markdown("---")

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "agent_statuses" not in st.session_state:
    st.session_state.agent_statuses = {
        "agent1": "WAITING",
        "agent2": "WAITING",
        "agent3": "WAITING",
        "agent4": "WAITING",
    }
    st.session_state.has_run = False
    st.session_state.a1_out = None
    st.session_state.a2_out = None
    st.session_state.a3_out = None
    st.session_state.a4_out = None

# Helper to render 4 Workflow Cards (Role, Input, Process, Output, Status)
def render_workflow_cards(statuses):
    w1, w2, w3, w4 = st.columns(4)
    agents_info = [
        (
            "AGENT 1",
            "Transaction Analyst",
            "Transaction history",
            "Spending analysis",
            "Spending intelligence",
            statuses["agent1"],
        ),
        (
            "AGENT 2",
            "Anomaly Detector",
            "Data + Agent 1",
            "Anomaly detection",
            "Anomaly intelligence",
            statuses["agent2"],
        ),
        (
            "AGENT 3",
            "Budget Planner",
            "Agents 1–2 + budget",
            "Budget optimization",
            "Monthly budget plan",
            statuses["agent3"],
        ),
        (
            "AGENT 4",
            "Financial Advisor",
            "Agents 1–3",
            "Decision synthesis",
            "Action plan",
            statuses["agent4"],
        ),
    ]
    cols = [w1, w2, w3, w4]
    for idx, (num, role, inp, proc, out, st_val) in enumerate(agents_info):
        with cols[idx]:
            if st_val == "COMPLETED":
                b_html = '<span class="badge-completed">✓ COMPLETED</span>'
            elif st_val == "RUNNING":
                b_html = '<span class="badge-running">⏳ RUNNING</span>'
            elif st_val == "FAILED":
                b_html = '<span class="badge-failed">✕ FAILED</span>'
            else:
                b_html = '<span class="badge-waiting">⏸ WAITING</span>'
            
            card_html = (
                f'<div class="workflow-card-detailed">'
                f'<div style="font-size: 0.8rem; font-weight: 800; color: #60a5fa;">{num}</div>'
                f'<h4 style="margin: 4px 0 10px 0; color: #f8fafc; font-size: 1.0rem;">{role}</h4>'
                f'<div class="agent-card-content">'
                f'<div class="agent-field"><span class="agent-field-label">Input:</span> {inp}</div>'
                f'<div class="agent-field"><span class="agent-field-label">Process:</span> {proc}</div>'
                f'<div class="agent-field"><span class="agent-field-label">Output:</span> {out}</div>'
                f'</div>'
                f'<div class="status-badge-container">{b_html}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. LIVE MULTI-AGENT WORKFLOW & SEQUENTIAL EXECUTION
# ---------------------------------------------------------
st.markdown("## ⚡ LIVE MULTI-AGENT WORKFLOW")

workflow_placeholder = st.empty()
handoff_placeholder = st.empty()
log_placeholder = st.empty()

# Handle Button Click / Fresh Execution
if run_analysis_btn:
    # Clear stale outputs
    st.session_state.has_run = False
    st.session_state.a1_out = None
    st.session_state.a2_out = None
    st.session_state.a3_out = None
    st.session_state.a4_out = None

    statuses = {
        "agent1": "WAITING",
        "agent2": "WAITING",
        "agent3": "WAITING",
        "agent4": "WAITING",
    }

    # Load factual calculations
    df = analytics.load_transactions(data_file)
    summary = analytics.calculate_summary(df)
    cat_breakdown = analytics.get_category_breakdown(df)
    trend_data = analytics.get_trend_data(df)
    budget_metrics = analytics.calculate_budget_metrics(df, monthly_income, monthly_budget)

    # -----------------------------------------------------
    # STEP 1: Transaction Analyst Agent
    # -----------------------------------------------------
    statuses["agent1"] = "RUNNING"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.info("🔍 **AGENT 1: Transaction Analyst** reading transaction history and calculating spending patterns...")
    time.sleep(0.7)

    with log_placeholder.container():
        st.info("🔍 **AGENT 1: Transaction Analyst** building category intelligence and normalizing multi-month spend...")
    time.sleep(0.7)

    a1_out = agents.transaction_analyst_agent(summary, cat_breakdown, trend_data, monthly_income, monthly_budget)
    st.session_state.a1_out = a1_out

    statuses["agent1"] = "COMPLETED"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.success("✓ **Agent 1 (Transaction Analyst)** completed spending analysis.")
    
    with handoff_placeholder.container():
        st.markdown(
            '<div class="handoff-banner">📦 <strong>HANDOFF TO AGENT 2</strong><br><small>Transaction analysis completed • Context passed: transaction summary, category breakdown, spending trend, budget relationship</small></div>',
            unsafe_allow_html=True,
        )
    time.sleep(0.9)

    # -----------------------------------------------------
    # STEP 2: Anomaly Detection Agent
    # -----------------------------------------------------
    statuses["agent2"] = "RUNNING"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.info("🚨 **AGENT 2: Anomaly Detector** receiving Agent 1 intelligence. Scanning transactions for unusual behavior...")
    time.sleep(0.7)

    with log_placeholder.container():
        st.info("🚨 **AGENT 2: Anomaly Detector** scoring transaction anomalies using robust statistical methods...")
    time.sleep(0.7)

    a2_out = agents.run_anomaly_detection(df, analysis_context=a1_out)
    st.session_state.a2_out = a2_out

    statuses["agent2"] = "COMPLETED"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.success(f"✓ **Agent 2 (Anomaly Detector)** completed! Flagged {a2_out['anomaly_count']} unusual items.")
    
    with handoff_placeholder.container():
        st.markdown(
            '<div class="handoff-banner">📦 <strong>HANDOFF TO AGENT 3</strong><br><small>Context passed: spending intelligence, anomaly intelligence, current income, current budget</small></div>',
            unsafe_allow_html=True,
        )
    time.sleep(0.9)

    # -----------------------------------------------------
    # STEP 3: Budget Planner Agent
    # -----------------------------------------------------
    statuses["agent3"] = "RUNNING"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.info("📊 **AGENT 3: Budget Planner** receiving upstream intelligence. Evaluating affordability and spending ceilings...")
    time.sleep(0.7)

    with log_placeholder.container():
        st.info("📊 **AGENT 3: Budget Planner** optimizing category-wise budgets and savings/deficit metrics...")
    time.sleep(0.7)

    a3_out = agents.run_budget_planner(monthly_income, monthly_budget, analysis_context=a1_out, anomaly_context=a2_out)
    st.session_state.a3_out = a3_out

    statuses["agent3"] = "COMPLETED"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.success("✓ **Agent 3 (Budget Planner)** completed budget optimization.")
    
    with handoff_placeholder.container():
        st.markdown(
            '<div class="handoff-banner">📦 <strong>HANDOFF TO AGENT 4</strong><br><small>Context passed: Agent 1 analysis, Agent 2 anomaly findings, Agent 3 budget plan</small></div>',
            unsafe_allow_html=True,
        )
    time.sleep(0.9)

    # -----------------------------------------------------
    # STEP 4: Financial Advisor Agent
    # -----------------------------------------------------
    statuses["agent4"] = "RUNNING"
    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.info("🤖 **AGENT 4: Financial Advisor** synthesizing multi-agent intelligence and prioritizing financial risks...")
    time.sleep(0.7)

    with log_placeholder.container():
        st.info("🤖 **AGENT 4: Financial Advisor** generating decision recommendations and executive action plan...")
    time.sleep(0.7)

    a4_out = agents.run_financial_advisor(analysis_context=a1_out, anomaly_context=a2_out, budget_context=a3_out)
    st.session_state.a4_out = a4_out

    statuses["agent4"] = "COMPLETED"
    st.session_state.agent_statuses = statuses
    st.session_state.has_run = True

    # Save data contexts to session state
    st.session_state.df = df
    st.session_state.summary = summary
    st.session_state.cat_breakdown = cat_breakdown
    st.session_state.trend_data = trend_data
    st.session_state.budget_metrics = budget_metrics

    with workflow_placeholder.container():
        render_workflow_cards(statuses)

    with log_placeholder.container():
        st.success("✅ **MULTI-AGENT DECISION COMPLETE** — Scroll down to review complete financial decision support output.")
    
    handoff_placeholder.empty()

else:
    # Render static workflow cards based on current session state
    with workflow_placeholder.container():
        render_workflow_cards(st.session_state.agent_statuses)

    if not st.session_state.has_run:
        with log_placeholder.container():
            st.info("▶️ Click **🚀 RUN AI ANALYSIS** in the sidebar to execute the four-agent intelligent pipeline.")

st.markdown("---")

# ---------------------------------------------------------
# Render Analysis Results (Only when analysis has run)
# ---------------------------------------------------------
if st.session_state.has_run and st.session_state.a4_out is not None:
    df = st.session_state.df
    summary = st.session_state.summary
    cat_breakdown = st.session_state.cat_breakdown
    trend_data = st.session_state.trend_data
    a1_out = st.session_state.a1_out
    a2_out = st.session_state.a2_out
    a3_out = st.session_state.a3_out
    a4_out = st.session_state.a4_out

    effective_ceiling = min(monthly_income, monthly_budget)

    # ---------------------------------------------------------
    # 4. EXECUTIVE FINANCIAL KPIS (2 Rows of 3 Cards Each)
    # ---------------------------------------------------------
    st.markdown("## 📈 EXECUTIVE FINANCIAL KPIS")
    st.markdown('<span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">🔍 FACTUAL / PYTHON ANALYSIS</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 1
    r1_col1, r1_col2, r1_col3 = st.columns(3)
    with r1_col1:
        months_cnt = summary.get('months_spanned', 2.0)
        render_kpi_card("Total Spending", f"{symbol}{summary['total_expenses']:,.2f}", f"{months_cnt} Months Total Spend", "text-blue")
    with r1_col2:
        render_kpi_card("Monthly Income", f"{symbol}{monthly_income:,.2f}", "Input Baseline", "text-emerald")
    with r1_col3:
        render_kpi_card("Monthly Budget", f"{symbol}{monthly_budget:,.2f}", f"Ceiling: {symbol}{effective_ceiling:,.0f}", "text-blue")

    # ROW 2
    r2_col1, r2_col2, r2_col3 = st.columns(3)
    with r2_col1:
        rem = effective_ceiling - a3_out['recommended_total_budget']
        c_class = "text-emerald" if rem >= 0 else "text-rose"
        render_kpi_card("Budget Remaining", f"{symbol}{rem:,.2f}", "Vs Rec. Monthly Budget", c_class)
    with r2_col2:
        sav_val = a3_out['expected_savings']
        sav_label = "Expected Monthly Savings" if sav_val >= 0 else "Projected Monthly Deficit"
        c_class = "text-emerald" if sav_val >= 0 else "text-rose"
        render_kpi_card(sav_label, f"{symbol}{sav_val:,.2f}", f"{a3_out['expected_savings_rate']:.1f}% Rate", c_class)
    with r2_col3:
        anom_cnt = a2_out['anomaly_count']
        c_class = "text-rose" if anom_cnt > 0 else "text-emerald"
        render_kpi_card("Detected Anomalies", f"{anom_cnt}", f"{a2_out['anomaly_rate']:.1f}% Anomaly Rate", c_class)

    # Infeasible & Overbudget Warning Banners
    if a3_out.get("is_infeasible"):
        st.error(
            f"⚠️ **INFEASIBLE BUDGET ALERT:** Target budget ({symbol}{monthly_budget:,.2f}) is below essential spending baseline ({symbol}{a3_out.get('essential_baseline_total', 0):,.2f}). "
            f"Essential living costs exceed ceiling by {symbol}{(a3_out.get('essential_baseline_total', 0) - effective_ceiling):,.2f}. Spending reductions or budget increase required."
        )
    elif monthly_budget > monthly_income:
        st.warning(
            f"⚠️ **Target Budget Notice:** Your target monthly budget ({symbol}{monthly_budget:,.2f}) exceeds monthly income ({symbol}{monthly_income:,.2f}). "
            f"An affordability ceiling of {symbol}{monthly_income:,.2f} has been enforced."
        )

    if a3_out['expected_savings'] < 0:
        st.error(
            f"🚨 **Monthly Deficit Alert:** Recommended monthly budget ({symbol}{a3_out['recommended_total_budget']:,.2f}) exceeds monthly income ({symbol}{monthly_income:,.2f}) by {symbol}{abs(a3_out['expected_savings']):,.2f}."
        )

    st.markdown("---")

    # ---------------------------------------------------------
    # 5. SPENDING ANALYTICS / CHARTS
    # ---------------------------------------------------------
    st.markdown("## 📊 SPENDING ANALYTICS")
    st.markdown('<span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">🔍 FACTUAL / PYTHON ANALYSIS</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### A. Spending by Category")
        if not cat_breakdown.empty:
            fig_bar = px.bar(
                cat_breakdown.sort_values(by="amount", ascending=False),
                x="category",
                y="amount",
                text_auto=".2s",
                color="amount",
                color_continuous_scale="Viridis",
                labels={"category": "Category", "amount": f"Amount ({symbol})"},
            )
            fig_bar.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", size=11),
                xaxis=dict(tickfont=dict(color="#f8fafc", size=10), gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(tickfont=dict(color="#f8fafc", size=10), gridcolor="rgba(255,255,255,0.08)"),
                showlegend=False,
            )
            st.plotly_chart(fig_bar, width="stretch")

    with c2:
        st.markdown("#### B. Spending Trend")
        if not trend_data.empty:
            fig_line = px.area(
                trend_data,
                x="date_str",
                y="cumulative_amount",
                labels={"date_str": "Date", "cumulative_amount": f"Cumulative Spend ({symbol})"},
                color_discrete_sequence=["#3B82F6"],
            )
            fig_line.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", size=11),
                xaxis=dict(tickfont=dict(color="#f8fafc", size=10), gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(tickfont=dict(color="#f8fafc", size=10), gridcolor="rgba(255,255,255,0.08)"),
            )
            st.plotly_chart(fig_line, width="stretch")

    with c3:
        st.markdown("#### C. Category Share")
        if not cat_breakdown.empty:
            fig_donut = px.pie(
                cat_breakdown,
                names="category",
                values="amount",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_donut.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", size=11),
                legend=dict(
                    font=dict(color="#f8fafc", size=10),
                    orientation="h",
                    yanchor="top",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                ),
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig_donut, width="stretch")

    st.markdown("---")

    # ---------------------------------------------------------
    # 6. ANOMALY FINDINGS
    # ---------------------------------------------------------
    st.markdown("## 🚨 ANOMALY FINDINGS")
    st.caption("Anomalies are identified using deterministic statistical analysis. AI is used only to interpret the findings.")
    
    anom_top_c1, anom_top_c2, anom_top_c3 = st.columns(3)
    with anom_top_c1:
        anom_cnt = a2_out['anomaly_count']
        c_class = "text-rose" if anom_cnt > 0 else "text-emerald"
        render_kpi_card("FLAGGED ANOMALIES", f"{anom_cnt}", "Flagged Items", c_class)
    with anom_top_c2:
        render_kpi_card("ANOMALY RATE", f"{a2_out['anomaly_rate']:.1f}%", "Vs Total Transactions", "text-blue")
    with anom_top_c3:
        highest_anom_val = a2_out['anomalies'][0]['amount'] if a2_out.get('anomalies') else 0.0
        render_kpi_card("HIGHEST ANOMALY VALUE", f"{symbol}{highest_anom_val:,.2f}", "Single Highest Spike", "text-rose" if highest_anom_val > 0 else "text-emerald")

    st.info(f"**AI Risk Evaluation:** {a2_out['llm_explanation']}")

    if a2_out.get("anomalies"):
        anom_table_df = pd.DataFrame(a2_out["anomalies"])[["severity", "date", "category", "description", "amount", "payment_method", "reason"]]
        st.dataframe(anom_table_df, width="stretch")
    else:
        st.success("✓ All transactions fall within expected spending patterns. No anomalies detected.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 7. BUDGET PLAN
    # ---------------------------------------------------------
    st.markdown("## 📊 BUDGET PLAN")
    st.markdown(
        f"**Target Budget:** `{symbol}{monthly_budget:,.2f}` | "
        f"**Effective Ceiling:** `{symbol}{effective_ceiling:,.2f}` | "
        f"**Recommended Monthly Budget:** `{symbol}{a3_out['recommended_total_budget']:,.2f}` | "
        f"**Savings Rate:** `{a3_out['expected_savings_rate']:.1f}%`"
    )
    st.markdown(f"**Planner Rationale:** {a3_out.get('rationale', '')}")

    cb_df = pd.DataFrame(a3_out.get("category_budgets", []))
    if not cb_df.empty:
        fig_bv = go.Figure()
        fig_bv.add_trace(go.Bar(name="Historical Monthly Baseline", x=cb_df["category"], y=cb_df["historical_spend"], marker_color="#9CA3AF"))
        fig_bv.add_trace(go.Bar(name="Recommended Budget", x=cb_df["category"], y=cb_df["recommended_budget"], marker_color="#10B981"))
        fig_bv.update_layout(
            title=dict(text="Recommended Budget vs Historical Monthly Baseline", font=dict(color="#f8fafc", size=15)),
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", size=11),
            xaxis=dict(
                title=dict(text="Category", font=dict(color="#94a3b8")),
                tickfont=dict(color="#f8fafc", size=11),
                gridcolor="rgba(255, 255, 255, 0.08)",
            ),
            yaxis=dict(
                title=dict(text=f"Amount ({symbol})", font=dict(color="#94a3b8")),
                tickfont=dict(color="#f8fafc", size=11),
                gridcolor="rgba(255, 255, 255, 0.08)",
            ),
            legend=dict(
                font=dict(color="#f8fafc", size=11),
                bgcolor="rgba(30, 41, 59, 0.7)",
                bordercolor="rgba(255,255,255,0.12)",
                borderwidth=1,
            ),
            height=380,
        )
        st.plotly_chart(fig_bv, width="stretch")

        display_cb_df = cb_df.rename(
            columns={
                "priority": "Priority",
                "category": "Category",
                "historical_spend": "Historical Monthly Baseline",
                "recommended_budget": "Recommended Budget",
                "adjustment_amount": "Difference",
                "adjustment_percentage": "Adjustment %",
                "reason": "Rationale",
            }
        )
        st.dataframe(
            display_cb_df[["Priority", "Category", "Historical Monthly Baseline", "Recommended Budget", "Difference", "Adjustment %", "Rationale"]],
            width="stretch",
        )

    st.markdown("---")

    # ---------------------------------------------------------
    # 8. AI FINANCIAL ADVISOR & RECOMMENDATIONS
    # ---------------------------------------------------------
    st.markdown("## 🎯 AI FINANCIAL ADVISOR")
    st.caption("Turning multi-agent intelligence into financial decisions")
    st.markdown('<span style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">🤖 AI-GENERATED INTERPRETATION</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.info(f"**Executive Summary:** {a4_out['executive_summary']}")

    adv1, adv2 = st.columns(2)

    with adv1:
        st.markdown("### 📌 Major Findings & Observations")
        for kf in a4_out.get("key_findings", []):
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid #3B82F6; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <strong style="color: #f8fafc;">{kf['title']}</strong> <span style="font-size: 0.8rem; color: #60a5fa; float: right;">[{kf['priority']}]</span><br>
                    <span style="font-size: 0.88rem; color: #cbd5e1;">{kf['explanation']}</span><br>
                    <small style="color: #94a3b8;">Supporting Metric: {kf['supporting_metric']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with adv2:
        st.markdown("### 🎯 Prioritized Recommendations")
        for pa in a4_out.get("priority_actions", []):
            p_color = "#f87171" if pa['priority'] == "High" else "#34d399"
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid {p_color}; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <strong style="color: #f8fafc;">{pa['action']}</strong> <span style="font-size: 0.8rem; color: {p_color}; float: right;">[{pa['priority']} PRIORITY]</span><br>
                    <span style="font-size: 0.88rem; color: #cbd5e1;"><strong>Reason:</strong> {pa['reason']}</span><br>
                    <small style="color: #34d399;"><strong>Expected Impact:</strong> {pa['expected_impact']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    rf_col1, rf_col2 = st.columns(2)

    with rf_col1:
        st.markdown("### 🚨 Spending Risks & Flags")
        for rf in a4_out.get("risk_flags", []):
            st.error(f"⚠️ {rf}")

    with rf_col2:
        st.markdown("### 💡 Positive Signals")
        for pb in a4_out.get("positive_behaviors", []):
            st.success(f"✓ {pb}")

    st.markdown("---")
    
    # ---------------------------------------------------------
    # 9. YOUR ACTION PLAN (Executive Shortlist 3-5 Actions)
    # ---------------------------------------------------------
    st.markdown("## 📋 YOUR ACTION PLAN")
    st.caption("Prioritized short-term execution roadmap")

    next_steps = a4_out.get("next_steps", [])
    if next_steps:
        act_cols = st.columns(min(len(next_steps), 5))
        for i, ns in enumerate(next_steps[:5]):
            with act_cols[i % len(act_cols)]:
                st.markdown(
                    f"""
                    <div class="action-card">
                        <span class="action-number">0{i+1}</span>
                        <span style="font-size: 0.92rem; font-weight: 600; color: #f8fafc;">{ns}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ---------------------------------------------------------
    # 10. DOWNLOAD REPORT SECTION
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("## 📥 DOWNLOAD ANALYSIS REPORT")

    def generate_full_markdown_report():
        sav_label = "Expected Monthly Savings" if a3_out['expected_savings'] >= 0 else "Projected Monthly Deficit"
        rep = f"""# AI Expense & Budget Intelligence - Comprehensive Advisory Report

## Executive Overview
- **Total Historical Expenses:** {symbol}{summary['total_expenses']:,.2f} (over {summary.get('months_spanned', 2.0)} months)
- **Monthly Income:** {symbol}{monthly_income:,.2f}
- **Monthly Target Budget:** {symbol}{monthly_budget:,.2f}
- **Effective Spending Ceiling:** {symbol}{effective_ceiling:,.2f}
- **Recommended Monthly Budget:** {symbol}{a3_out['recommended_total_budget']:,.2f}
- **{sav_label}:** {symbol}{a3_out['expected_savings']:,.2f} ({a3_out['expected_savings_rate']}%)
- **Anomalies Detected:** {a2_out['anomaly_count']} flagged items ({a2_out['anomaly_rate']}%)

---

## 1. Executive Financial Action Plan (Agent 4)
**Summary:** {a4_out['executive_summary']}

### Priority Actions:
"""
        for pa in a4_out.get("priority_actions", []):
            rep += f"- [{pa['priority']}] {pa['action']} | Reason: {pa['reason']} (Impact: {pa['expected_impact']})\n"

        rep += "\n### Next Steps Action Plan:\n"
        for ns in a4_out.get("next_steps", []):
            rep += f"- {ns}\n"

        rep += f"""
---

## 2. Agent 1 — Transaction Analyst Findings
{a1_out['spending_behavior']}

---

## 3. Agent 2 — Anomaly Detector Findings
{a2_out['llm_explanation']}

---

## 4. Agent 3 — Budget Planner Allocation
{a3_out['rationale']}

---
*Report generated by AI Expense & Budget Intelligence Decision Support System.*
"""
        return rep

    st.download_button(
        label="📥 DOWNLOAD COMPLETE FINANCIAL ADVISORY REPORT (.MD)",
        data=generate_full_markdown_report(),
        file_name="AI_Financial_Advisory_Report.md",
        mime="text/markdown",
        width="stretch",
        type="primary",
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer-container">
        <strong>AI Expense & Budget Intelligence</strong> | Sequential Multi-Agent Decision Support System<br>
        <span style="color: #475569;">Python-driven analytics • Multi-agent orchestration • Explainable financial reasoning</span>
    </div>
    """,
    unsafe_allow_html=True,
)
