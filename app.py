import pandas as pd
import plotly.express as px
import streamlit as st
from finpilott import agent, core, report, sample
from finpilott.core import inr

st.set_page_config(page_title="FinPilot | Student Finance", page_icon="💸", layout="wide")

# ---------- Demo-first state ----------
S = st.session_state
if "raw" not in S or S.raw is None:
    S.raw = sample.demo()
if "corrections" not in S:
    S.corrections = {}
if "manual_entries" not in S:
    S.manual_entries = []
if "goals" not in S:
    S.goals = [
        {"name": "Laptop", "target": 120000.0, "saved": 30000.0, "monthly": 5000.0},
        {"name": "Emergency fund", "target": 50000.0, "saved": 10000.0, "monthly": 2000.0},
    ]

# Quotes are chosen randomly when a fresh Streamlit session opens.
# Streamlit reruns preserve these values in session_state, so they stay stable during interaction.
HEADER_QUOTES = [
    "Your money should have a plan, not just a balance.",
    "Small money decisions today create bigger possibilities tomorrow.",
    "Spend with purpose. Save with confidence. Live with freedom.",
    "Every rupee tells a story. Make yours count.",
    "You don't need more money to start. You need more clarity.",
    "Your future self will thank you for the choices you make today.",
    "Financial freedom begins with understanding where your money goes.",
    "Be the CEO of your money, one decision at a time.",
    "Don't just track your money. Make your money work for your goals.",
]
SIDEBAR_QUOTES = [
    "Know your spending. Own your choices.",
]
import random
if "header_quote" not in S:
    S.header_quote = random.choice(HEADER_QUOTES)
if "sidebar_quote" not in S:
    S.sidebar_quote = random.choice(SIDEBAR_QUOTES)

# ---------- Styling ----------
st.markdown("""
<style>
:root { --ink:#14213d; --muted:#667085; --line:#e6eaf0; --blue:#4f46e5; --teal:#0f9f8f; }
.stApp {background:#f7f9fc;color:var(--ink);}
[data-testid="stAppViewContainer"] {background:#f7f9fc;}
.block-container {padding-top:1.3rem;padding-bottom:2.5rem;max-width:1500px;}
[data-testid="stHeader"] {background:rgba(247,249,252,.92);}
div[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #e7ebf2;}
div[data-testid="stSidebar"] > div:first-child {padding-top:1.15rem;}
div[data-testid="stMetric"] {background:#ffffff;border:1px solid #e7ebf2;padding:18px 18px 15px;border-radius:16px;box-shadow:0 5px 18px rgba(20,33,61,.045);min-height:112px;}
[data-testid="stMetricLabel"] {font-weight:650;color:#667085;}
[data-testid="stMetricValue"] {color:#14213d;font-size:1.75rem;font-weight:750;}
[data-testid="stMetricDelta"] {font-size:.82rem;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius:17px;border-color:#e5eaf1;background:#ffffff;box-shadow:0 4px 16px rgba(20,33,61,.025);}
.hero {padding:26px 30px;border-radius:22px;background:#ffffff;color:#14213d;margin-bottom:16px;box-shadow:0 8px 28px rgba(20,33,61,.055);border:1px solid #e7ebf2;position:relative;overflow:hidden;}
.hero:after {content:"";position:absolute;right:-55px;top:-100px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(79,70,229,.10),rgba(15,159,143,.025) 65%,transparent 70%);pointer-events:none;}
.hero h1 {color:#14213d;margin:0;font-size:1.85rem;line-height:1.35;letter-spacing:-.035em;}
.hero p {color:#667085;margin:9px 0 0;font-size:1rem;line-height:1.6;}
.eyebrow {color:#667085;text-transform:uppercase;letter-spacing:.11em;font-size:.72rem;font-weight:800;}
.stButton>button,.stDownloadButton>button {border-radius:11px;min-height:2.55rem;font-weight:650;border:1px solid #dce3ed;background:#fff;color:#24324b;transition:all .15s ease;}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:#8b85f6;color:#3730a3;background:#f8f8ff;box-shadow:0 4px 12px rgba(79,70,229,.08);}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {background:#4f46e5;color:white;border-color:#4f46e5;}
div[data-testid="stRadio"] > label {font-weight:750;color:#273653;}
div[data-testid="stRadio"] div[role="radiogroup"] {gap:5px;}
div[data-testid="stRadio"] div[role="radiogroup"] label {padding:9px 11px;border-radius:10px;border:1px solid transparent;}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover {background:#f0f2ff;}
div[data-testid="stProgress"] > div {border-radius:999px;}
div[data-testid="stAlert"] {border-radius:13px;border:1px solid #e6eaf0;}
div[data-testid="stExpander"] {border:1px solid #e5eaf1;border-radius:14px;background:#fff;}
div[data-testid="stPlotlyChart"] {border:1px solid #e7ebf2;border-radius:16px;background:#fff;padding:8px 8px 0;}
div[data-testid="stDataFrame"] {border:1px solid #e7ebf2;border-radius:13px;overflow:hidden;background:#fff;}
div[data-testid="stForm"] {background:#fff;border:1px solid #e7ebf2;border-radius:15px;padding:12px;}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stSelectbox"] div[data-baseweb="select"] {border-radius:10px;}
h1,h2,h3,h4 {letter-spacing:-.025em;color:#14213d;}
h2 {margin-top:.25rem;}
.pranjal-intel {padding:18px 20px;border-radius:17px;background:linear-gradient(120deg,#f0f2ff 0%,#effcf9 100%);border:1px solid #dfe5f6;margin:4px 0 12px;}
.pranjal-intel-title {font-weight:800;color:#14213d;font-size:1.12rem;}
.pranjal-intel-sub {color:#667085;font-size:.9rem;margin-top:4px;}
@media (max-width: 768px) {.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:22px}.hero h1{font-size:1.45rem}}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.markdown("<div style=\"font-size:2rem;font-weight:850;letter-spacing:-.05em;color:#172554;line-height:1.15;padding:4px 0 2px 0;\">✦ FinPilot</div>", unsafe_allow_html=True)
    st.caption("Your intelligent money companion")
    st.markdown(f"<div style=\"color:#52627a;font-size:.9rem;font-style:italic;line-height:1.5;padding:3px 0 8px 0;\">“{S.sidebar_quote}”</div>", unsafe_allow_html=True)
    if st.button("✦ New inspiration", width="stretch", key="new_inspiration"):
        choices = [q for q in HEADER_QUOTES if q != S.header_quote]
        S.header_quote = random.choice(choices or HEADER_QUOTES)
        st.rerun()
    st.markdown('<div style="background:#e0e7ff;color:#3730a3;padding:9px 11px;border-radius:10px;font-size:.82rem;font-weight:700;">● DEMO MODE  ·  Sample transactions</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")
    NAV_ITEMS = ["🏠 Overview", "➕ Add expense", "📊 Spending", "🔔 Smart alerts", "🎯 Goal planner", "🤖 FinPilot AI", "📄 Report"]
    if "active_page" not in S:
        S.active_page = NAV_ITEMS[0]
    active_page = st.radio("Go to", NAV_ITEMS, key="active_page", label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### Demo settings")
    carry_forward = st.number_input("Balance carried forward from previous months (₹)", min_value=0, value=67000, step=1000)
    savings = st.number_input("Monthly savings target (₹)", min_value=0, value=10000, step=1000)
    st.caption(f"🎯 Active savings goals: {len(S.goals)}")
    st.caption("Add and manage multiple goals in Goal planner.")
    if st.button("↻ Reset demo data", width="stretch"):
        S.raw = sample.demo()
        S.manual_entries = []
        S.corrections = {}
        S.goals = [
            {"name": "Laptop", "target": 120000.0, "saved": 30000.0, "monthly": 5000.0},
            {"name": "Emergency fund", "target": 50000.0, "saved": 10000.0, "monthly": 2000.0},
        ]
        st.rerun()
    with st.expander("Optional: import a statement"):
        uploads = st.file_uploader("CSV or PDF (not required)", type=["csv", "pdf"], accept_multiple_files=True)
        if uploads and st.button("Import selected files"):
            try:
                imported = pd.concat([core.load_file(f) for f in uploads], ignore_index=True)
                S.raw = pd.concat([S.raw, imported], ignore_index=True)
                st.success("Statement imported.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not import file: {e}")

# Combine demo transactions and quick entries
if not S.goals:
    S.goals.append({"name": "Emergency fund", "target": 50000.0, "saved": 0.0, "monthly": 2000.0})
primary_goal = S.goals[0]
goal_name = primary_goal["name"]
goal_target = float(primary_goal["target"])
goal_saved = float(primary_goal["saved"])

raw = S.raw.copy()
if S.manual_entries:
    raw = pd.concat([raw, pd.DataFrame(S.manual_entries)], ignore_index=True)
df = core.prep(raw, S.corrections)
if df.empty:
    st.warning("No transactions yet. Add an expense to begin.")
    st.stop()

today = pd.Timestamp.today().normalize()
# Demo data may be dated around Oct 2026; use the latest transaction date for coherent demo calculations.
today = max(today, df.date.max().normalize())
cur = today.to_period("M")
prev = cur - 1
monthly_summary = core.month_summary(df, cur)
income_this = monthly_summary["income"]
income_prev = core.month_summary(df, prev)["income"]
income = income_this or income_prev or 85000

# Carry-forward is money already held from earlier months.
# Estimate current balance as carry-forward + this month's net cash flow.
current_balance = max(0, float(carry_forward) + float(monthly_summary["net"]))

rec = core.recurring(df)
anoms = core.anomalies(df)
fc = core.forecast(df, rec, today, current_balance, income)
pressure = fc[fc.pressure].date.min() if fc.pressure.any() else None
safe = core.safe_to_spend(df, rec, today, income, savings)
health = core.health(df, rec, core.BUDGETS, cur, current_balance, today)
feed = core.radar(df, rec, today, core.BUDGETS, anoms, None if pressure is None or pd.isna(pressure) else pressure)
goal = {"name": goal_name, "target": goal_target, "saved": goal_saved}
net = core.monthly_net(df)

# ---------- Header ----------
st.markdown(f"""
<div class="hero">
  <div style="font-size:.76rem;text-transform:uppercase;letter-spacing:.16em;font-weight:750;color:#c7d2fe;margin-bottom:8px;">A little money wisdom</div>
  <h1>“{S.header_quote}”</h1>
  <p>Your money, made clearer. Understand spending, plan confidently, and reach your goals.</p>
</div>
""", unsafe_allow_html=True)
st.caption("Interactive prototype for demonstration · Uses fictional sample data unless you add an expense.")

# ---------- Main dashboard ----------
monthly_summary = core.month_summary(df, cur)
monthly_expenses = monthly_summary["expense"]
monthly_income = monthly_summary["income"]

# Remaining budget is based only on categories with an explicit budget.
budget_status_df = core.budget_status(df, core.BUDGETS, cur)
total_planned_budget = float(sum(core.BUDGETS.values()))
budgeted_spend = float(budget_status_df["spent"].sum()) if len(budget_status_df) else 0.0
budget_remaining = total_planned_budget - budgeted_spend

st.markdown(
    '<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin:4px 0 10px 0;">'
    '<div class="eyebrow">Your money at a glance</div>'
    '<div style="font-size:.72rem;font-weight:750;letter-spacing:.06em;color:#3730a3;background:#e0e7ff;padding:6px 10px;border-radius:999px;">PRANJAL · SMART MONEY DASHBOARD</div>'
    '</div>',
    unsafe_allow_html=True
)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Available balance", inr(current_balance), help="Estimated carry-forward balance plus this month net cash flow; not live bank data.")
m2.metric("Income this month", inr(monthly_income), help="Income transactions in the selected demo month.")
m3.metric("Spent this month", inr(monthly_expenses), help="Total outgoing transactions in the selected demo month.")
if budget_remaining >= 0:
    m4.metric("Budget remaining", inr(budget_remaining), help=f"Across categories with set budgets, out of {inr(total_planned_budget)} planned.")
else:
    m4.metric("Over budget", inr(abs(budget_remaining)), delta="Needs attention", delta_color="inverse",
              help=f"Spending in budgeted categories exceeds the combined {inr(total_planned_budget)} plan.")

if active_page == '🏠 Overview':
    st.markdown("## Your savings goals")
    st.caption("Your plans, progress, and next milestones — all in one place.")
    if S.goals:
        goal_cols = st.columns(min(3, len(S.goals)))
        for i, item in enumerate(S.goals[:3]):
            with goal_cols[i]:
                target = max(1.0, float(item["target"]))
                saved_amt = float(item["saved"])
                pct = min(100, int(saved_amt / target * 100))
                with st.container(border=True):
                    st.markdown(f"**🎯 {item['name']}**")
                    st.markdown(f"<div style='font-size:1.45rem;font-weight:700;color:#172554'>{inr(saved_amt)}</div>", unsafe_allow_html=True)
                    st.caption(f"of {inr(target)}")
                    st.progress(pct / 100)
                    st.caption(f"{pct}% complete · {inr(max(0, target-saved_amt))} to go")
        if len(S.goals) > 3:
            st.caption(f"+ {len(S.goals)-3} additional goals available in Goal planner.")
    else:
        st.info("Create your first goal in Goal planner to see it here.")

    # ---------- FinPilot Intelligence: grounded, explainable demo insights ----------
    st.markdown("## ✨ FinPilot Intelligence")
    st.caption("Your money co-pilot: explainable insights based on available transactions, budgets, and goals. Demo data is fictional; no live bank connection is active.")
    cats_now = monthly_summary.get("cats", pd.Series(dtype=float))
    if len(cats_now):
        top_category = str(cats_now.idxmax())
        top_category_spend = float(cats_now.max())
    else:
        top_category, top_category_spend = "No spending yet", 0.0
    intelligence_cols = st.columns(3)
    with intelligence_cols[0]:
        with st.container(border=True):
            st.caption("TOP SPENDING CATEGORY")
            st.markdown(f"**{top_category}**")
            st.markdown(f"<div style='font-size:1.5rem;font-weight:800;color:#312e81'>{inr(top_category_spend)}</div>", unsafe_allow_html=True)
            st.caption("Based on recorded expenses this month.")
    with intelligence_cols[1]:
        with st.container(border=True):
            st.caption("SAFE-TO-SPEND GUIDE")
            st.markdown(f"<div style='font-size:1.5rem;font-weight:800;color:#0f766e'>{inr(safe['per_day'])}/day</div>", unsafe_allow_html=True)
            st.caption("An estimate from your current cash flow and planned savings.")
    with intelligence_cols[2]:
        with st.container(border=True):
            st.caption("SAVINGS PROGRESS")
            total_targets = sum(float(g.get("target", 0)) for g in S.goals)
            total_saved = sum(float(g.get("saved", 0)) for g in S.goals)
            all_goal_pct = min(100, int(total_saved / max(1, total_targets) * 100))
            st.markdown(f"<div style='font-size:1.5rem;font-weight:800;color:#312e81'>{all_goal_pct}%</div>", unsafe_allow_html=True)
            st.progress(all_goal_pct / 100)
            st.caption(f"{inr(total_saved)} saved across {len(S.goals)} goal(s).")

    with st.container(border=True):
        st.markdown("**Ask FinPilot AI about your money**")
        st.caption("Try a question. The answer uses your current demo transactions and settings; it is not connected to your bank.")
        with st.form("overview_intelligence_form", clear_on_submit=False):
            intelligence_question = st.text_input(
                "Your question",
                placeholder="e.g. Where am I spending the most? Can I save more?",
                label_visibility="collapsed",
            )
            ask_cols = st.columns([1, 1, 2])
            with ask_cols[0]:
                ask_submit = st.form_submit_button("✨ Ask FinPilot AI", width="stretch")
            with ask_cols[1]:
                spending_prompt = st.form_submit_button("Spending insights", width="stretch")
            with ask_cols[2]:
                savings_prompt = st.form_submit_button("Help me save more", width="stretch")
            if ask_submit or spending_prompt or savings_prompt:
                if spending_prompt:
                    chosen_question = "Where am I spending the most, and what can I improve?"
                elif savings_prompt:
                    chosen_question = "How can I save more money based on my spending and goals?"
                else:
                    chosen_question = intelligence_question.strip()
                if not chosen_question:
                    st.warning("Type a question or choose one of the example prompts.")
                else:
                    try:
                        intelligence_answer, intelligence_evidence = agent.answer(
                            chosen_question, df, {
                                "today": today, "income": income, "savings": savings,
                                "goal": goal, "budgets": core.BUDGETS
                            }
                        )
                        st.markdown("**FinPilot AI says**")
                        st.write(intelligence_answer)
                        if intelligence_evidence is not None and len(intelligence_evidence):
                            with st.expander("See supporting transactions"):
                                st.dataframe(intelligence_evidence, width="stretch")
                    except Exception as exc:
                        st.error(f"I couldn't answer that yet: {exc}")
                        st.caption("You can still use the spending charts, alerts, and Goal planner while we improve this demo feature.")

    st.markdown("## Quick expense tracking")
    st.caption("Add a purchase in seconds. No bank statement upload is needed for each expense.")
    with st.expander("＋ Quick add an expense", expanded=False):
        with st.form("quick_expense_form", clear_on_submit=True):
            q1, q2, q3 = st.columns([1.4, 1, 1.2])
            with q1:
                quick_name = st.text_input("What did you spend on?", placeholder="Coffee, cab, books")
            with q2:
                quick_amount = st.number_input("Amount (₹)", min_value=1, value=150, step=10)
            with q3:
                quick_category = st.selectbox("Category", ["Food Delivery", "Groceries", "Shopping", "Dining", "Transport", "Subscriptions", "Utilities", "Education", "Entertainment", "Other"], key="quick_category")
            quick_date = st.date_input("Date", value=pd.Timestamp.today().date(), key="quick_date")
            if st.form_submit_button("＋ Save expense", width="stretch"):
                if not quick_name.strip():
                    st.error("Enter an expense name first.")
                else:
                    S.corrections[core.merchant_of(quick_name.strip())] = quick_category
                    S.manual_entries.append({"date": pd.Timestamp(quick_date), "description": quick_name.strip(), "amount": -float(quick_amount)})
                    st.success(f"Saved {quick_name.strip()} · {inr(quick_amount)}")
                    st.rerun()

    st.caption(f"Demo data is fictional. Available balance = money carried forward ({inr(carry_forward)}) + this month net cash flow ({inr(monthly_summary['net'])}). This is an estimate, not a live bank balance.")

    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Where your money goes")
        summary = core.month_summary(df, cur)
        if len(summary["cats"]):
            chart = px.pie(values=summary["cats"].values, names=summary["cats"].index, hole=0.55)
            chart.update_layout(
                margin=dict(t=12, b=12, l=8, r=8),
                legend_title_text="",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
                font=dict(color="#334155", size=12),
            )
            st.plotly_chart(chart, width="stretch")
        else:
            st.info("Add an expense to see your spending breakdown.")
    with right:
        st.subheader("Your money snapshot")
        with st.container(border=True):
            st.markdown(f"**Monthly net cash flow**")
            st.markdown(f"<div style='font-size:1.75rem;font-weight:800;color:{'#0f766e' if monthly_summary['net'] >= 0 else '#b91c1c'}'>{inr(monthly_summary['net'])}</div>", unsafe_allow_html=True)
            st.divider()
            snap1, snap2 = st.columns(2)
            snap1.metric("Carried forward", inr(carry_forward))
            snap2.metric("Savings target", inr(savings))
            snap1.metric("Wellness score", f"{health['total']}/100")
            snap2.metric("Estimated balance", inr(current_balance))
            st.caption("Demo estimate only — this is not a live bank balance.")

    st.markdown("## Recent transactions")
    st.caption("Your latest recorded activity at a glance.")
    recent = df.sort_values("date", ascending=False).head(6).copy()
    recent["date"] = recent["date"].dt.strftime("%d %b")
    recent["amount"] = recent["amount"].map(lambda x: ("+" if x > 0 else "−") + inr(abs(x)))
    st.dataframe(recent[["date", "merchant", "category", "amount"]], hide_index=True, width="stretch")

if active_page == '➕ Add expense':
    st.subheader("Add an expense")
    st.write("Record a purchase in a few seconds. Your demo dashboard updates immediately.")
    with st.form("add_expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            expense_name = st.text_input("What did you spend on?", placeholder="e.g. Lunch, Uber, stationery")
            expense_amount = st.number_input("Amount (₹)", min_value=1, value=180, step=10)
        with c2:
            expense_category = st.selectbox("Category", ["Food Delivery", "Groceries", "Shopping", "Dining", "Transport", "Subscriptions", "Utilities", "Education", "Entertainment", "Other"])
            expense_date = st.date_input("Date", value=pd.Timestamp.today().date())
        expense_note = st.text_input("Optional note", placeholder="e.g. Lunch with friends")
        submitted = st.form_submit_button("＋ Save expense", width="stretch")
        if submitted:
            if not expense_name.strip():
                st.error("Enter a name for this expense.")
            else:
                description = f"{expense_name.strip()} {expense_note.strip()}".strip()
                # Keep the chosen category for this merchant in the demo session.
                merchant = core.merchant_of(description)
                S.corrections[merchant] = expense_category
                S.manual_entries.append({
                    "date": pd.Timestamp(expense_date),
                    "description": description,
                    "amount": -float(expense_amount),
                })
                st.success(f"Added {expense_name.strip()} · {inr(expense_amount)}")
                st.rerun()
    st.info("For this judging demo, expenses are saved in the current app session. Reset demo data from the sidebar to start over.")

if active_page == '📊 Spending':
    st.subheader("Spending history")
    st.caption("Review past months or years using the transactions available in FinPilot. Sample data is fictional.")

    dated_transactions = df.dropna(subset=["date"]).copy()
    dated_transactions["date"] = pd.to_datetime(dated_transactions["date"])
    available_periods = sorted(dated_transactions["date"].dt.to_period("M").unique())
    available_years = sorted(dated_transactions["date"].dt.year.unique())

    view_mode = st.radio(
        "History view",
        ["Monthly", "Yearly"],
        horizontal=True,
        key="history_view_mode"
    )

    if view_mode == "Monthly":
        period_labels = [str(period) for period in available_periods]
        default_period = str(cur) if str(cur) in period_labels else (period_labels[-1] if period_labels else str(cur))
        selected_period_label = st.selectbox(
            "Choose month",
            period_labels or [str(cur)],
            index=period_labels.index(default_period) if default_period in period_labels else 0,
            format_func=lambda value: pd.Period(value, freq="M").strftime("%B %Y"),
            key="history_selected_month"
        )
        selected_period = pd.Period(selected_period_label, freq="M")
        selected_transactions = dated_transactions[
            dated_transactions["date"].dt.to_period("M") == selected_period
        ].copy()
        summary = core.month_summary(df, selected_period)
        period_title = selected_period.strftime("%B %Y")
        income_total = float(summary["income"])
        expense_total = float(summary["expense"])
        net_total = float(summary["net"])
        category_totals = summary["cats"]
    else:
        year_labels = [str(int(year)) for year in available_years]
        default_year = str(today.year) if str(today.year) in year_labels else (year_labels[-1] if year_labels else str(today.year))
        selected_year_label = st.selectbox(
            "Choose year",
            year_labels or [str(today.year)],
            index=year_labels.index(default_year) if default_year in year_labels else 0,
            key="history_selected_year"
        )
        selected_year = int(selected_year_label)
        selected_transactions = dated_transactions[
            dated_transactions["date"].dt.year == selected_year
        ].copy()
        income_total = float(selected_transactions.loc[selected_transactions["amount"] > 0, "amount"].sum())
        expense_total = float(-selected_transactions.loc[selected_transactions["amount"] < 0, "amount"].sum())
        net_total = income_total - expense_total
        category_totals = (
            -selected_transactions.loc[selected_transactions["amount"] < 0]
            .groupby("category")["amount"].sum()
        ).sort_values(ascending=False)
        period_title = str(selected_year)

    k1, k2, k3 = st.columns(3)
    k1.metric("Income", inr(income_total))
    k2.metric("Total expenses", inr(expense_total))
    k3.metric("Net cash flow", inr(net_total), help="Income minus expenses for the selected period.")

    st.markdown("---")
    st.subheader(f"Expenses in {period_title}")
    expense_rows = selected_transactions[selected_transactions["amount"] < 0].sort_values("date", ascending=False).copy()
    if not expense_rows.empty:
        for _, transaction in expense_rows.iterrows():
            transaction_date = pd.Timestamp(transaction["date"]).strftime("%d %b %Y")
            merchant = str(transaction.get("merchant", "Purchase"))
            category_name = str(transaction.get("category", "Other"))
            amount_text = inr(abs(float(transaction["amount"])))
            with st.container(border=True):
                c_date, c_detail, c_amount = st.columns([1, 3, 1.2])
                c_date.caption(transaction_date)
                c_detail.markdown(f"**You spent {amount_text}**")
                c_detail.caption(f"{merchant} · {category_name}")
                c_amount.markdown(f"**−{amount_text}**")
    else:
        st.info("No expenses recorded for this period. Add an expense to start tracking.")

    st.markdown("---")
    st.subheader(f"Where your money went in {period_title}")
    if len(category_totals):
        bars = px.bar(
            x=category_totals.index,
            y=category_totals.values,
            labels={"x": "Spending category", "y": "Amount spent (₹)"},
            text_auto=".2s"
        )
        bars.update_layout(
            margin=dict(t=20, b=15, l=10, r=10),
            xaxis_tickangle=-25,
            yaxis=dict(rangemode="tozero"),
            showlegend=False
        )
        st.plotly_chart(bars, width="stretch")
    else:
        st.info("No category totals to chart for this period yet.")

    if view_mode == "Yearly":
        st.markdown("---")
        st.subheader(f"Month-by-month spending in {period_title}")
        year_transactions = selected_transactions.copy()
        year_expenses = year_transactions[year_transactions["amount"] < 0].copy()
        if not year_expenses.empty:
            year_expenses["Month"] = year_expenses["date"].dt.strftime("%b")
            year_expenses["Month number"] = year_expenses["date"].dt.month
            monthly_chart_data = (
                year_expenses.groupby("Month number")
                .agg(spent=("amount", lambda values: -values.sum()))
                .reset_index()
            )
            monthly_chart_data["Month"] = monthly_chart_data["Month number"].map(
                lambda month_number: pd.Timestamp(year=selected_year, month=int(month_number), day=1).strftime("%b")
            )
            monthly_chart_data = monthly_chart_data.rename(columns={"spent": "Amount spent (₹)"})
            monthly_chart = px.line(
                monthly_chart_data,
                x="Month",
                y="Amount spent (₹)",
                markers=True,
                title="Spending trend across the year"
            )
            st.plotly_chart(monthly_chart, width="stretch")
        else:
            st.info("No monthly spending trend is available for this year.")

    st.markdown("---")
    st.subheader("Monthly budget check")
    if view_mode == "Monthly":
        budgets = core.budget_status(df, core.BUDGETS, selected_period)
        for row in budgets.itertuples():
            st.write(f"**{row.category}** · {inr(row.spent)} of {inr(row.budget)}")
            st.progress(min(1.0, max(0.0, row.pct / 100)))
    else:
        st.caption("Category budgets are monthly targets, so this section is shown only in Monthly view.")

if active_page == '🔔 Smart alerts':
    st.subheader("Smart alerts")
    if feed:
        for observation, action in feed:
            st.info(f"**{observation}**  \n{action}")
    else:
        st.success("No alerts right now. You're all caught up.")
    st.subheader("Potentially unusual transactions")
    if len(anoms):
        show = anoms[["date", "merchant", "category", "amount", "reason"]].copy()
        show["date"] = show["date"].dt.strftime("%d %b %Y")
        show["amount"] = show["amount"].map(lambda x: inr(abs(x)))
        st.dataframe(show, hide_index=True, width="stretch")
    else:
        st.write("No unusual transactions detected in the current sample.")

if active_page == '🎯 Goal planner':
    st.subheader("Multiple savings goals")
    st.write("Create separate goals, track progress, and record money you set aside for each one.")

    with st.container(border=True):
        st.markdown("**＋ Create a new goal**")
        with st.form("create_goal_form", clear_on_submit=True):
            g1, g2, g3 = st.columns(3)
            with g1:
                new_goal_name = st.text_input("Goal name", placeholder="e.g. Trip to Goa")
            with g2:
                new_goal_target = st.number_input("Target amount (₹)", min_value=1, value=20000, step=1000)
            with g3:
                new_goal_saved = st.number_input("Already saved (₹)", min_value=0, value=0, step=500)
            new_goal_monthly = st.number_input("Planned monthly saving (₹)", min_value=0, value=2000, step=500)
            if st.form_submit_button("＋ Add savings goal", width="stretch"):
                if not new_goal_name.strip():
                    st.error("Please enter a name for your goal.")
                elif any(g["name"].strip().lower() == new_goal_name.strip().lower() for g in S.goals):
                    st.error("A goal with this name already exists.")
                else:
                    S.goals.append({"name": new_goal_name.strip(), "target": float(new_goal_target), "saved": float(new_goal_saved), "monthly": float(new_goal_monthly)})
                    st.success(f"Created goal: {new_goal_name.strip()}")
                    st.rerun()

    st.markdown("### Your goals")
    if not S.goals:
        st.info("Create your first savings goal above.")
    for idx, item in enumerate(S.goals):
        target = max(1.0, float(item["target"]))
        saved_amount = float(item["saved"])
        remaining = max(0.0, target - saved_amount)
        pct = min(100, int(saved_amount / target * 100))
        with st.container(border=True):
            title_col, metric_col = st.columns([2, 1])
            with title_col:
                st.markdown(f"### 🎯 {item['name']}")
                st.progress(pct / 100)
                st.caption(f"{inr(saved_amount)} saved of {inr(target)} · {pct}% complete")
                st.caption(f"Still needed: {inr(remaining)}")
            with metric_col:
                monthly_plan = max(0.0, float(item.get("monthly", 0)))
                st.metric("Monthly saving plan", inr(monthly_plan))
                months_needed = int((remaining + monthly_plan - 1) // monthly_plan) if monthly_plan > 0 and remaining > 0 else (0 if remaining <= 0 else None)
                if months_needed is not None:
                    st.caption("Already reached!" if months_needed == 0 else f"About {months_needed} month(s) at this pace")
                else:
                    st.caption("Set a monthly plan to estimate a timeline.")
            with st.expander(f"Update {item['name']}"):
                with st.form(f"update_goal_{idx}"):
                    updated_saved = st.number_input("Amount saved so far (₹)", min_value=0, value=int(saved_amount), step=500, key=f"saved_{idx}")
                    added_saving = st.number_input("Add money saved today (₹)", min_value=0, value=0, step=500, key=f"add_saved_{idx}")
                    updated_monthly = st.number_input("Monthly saving plan (₹)", min_value=0, value=int(item.get("monthly", 0)), step=500, key=f"monthly_{idx}")
                    if st.form_submit_button("Save goal progress"):
                        item["saved"] = float(updated_saved + added_saving)
                        item["monthly"] = float(updated_monthly)
                        st.success("Goal progress updated.")
                        st.rerun()
            if st.button(f"🗑 Delete {item['name']}", key=f"delete_goal_{idx}"):
                S.goals.pop(idx)
                st.rerun()

    st.markdown("---")
    st.subheader("Small changes can grow your savings")
    category = st.selectbox("Choose a spending category to reduce", list(core.BUDGETS.keys()), key="goal_category")
    cut = st.slider("Reduce that category by (%)", 0, 50, 15, key="goal_cut")
    prev_spend = core.month_summary(df, prev)["cats"].get(category, 0)
    extra = prev_spend * cut / 100
    st.metric("Potential extra savings per month", inr(extra))
    st.caption("Illustration based on previous month's recorded spending, not a guaranteed saving.")

@st.dialog("💡 What can I ask FinPilot AI?", width="large")
def question_guide():
    st.caption("Choose a question to see an answer based on the demo transactions.")
    groups = [
        ("💸 Spending", [
            "Where did I spend the most?",
            "What increased vs last month?",
        ]),
        ("🧾 Bills & subscriptions", [
            "Which subscriptions do I have?",
            "What bills are coming up?",
        ]),
        ("🔔 Alerts", [
            "Are there unusual transactions?",
            "How much of my budget is committed?",
        ]),
        ("🎯 Budget & goals", [
            "How much can I safely spend today?",
            "How long until I reach my savings goal?",
        ]),
    ]
    for title, questions in groups:
        st.markdown(f"**{title}**")
        cols = st.columns(2)
        for i, q in enumerate(questions):
            with cols[i % 2]:
                if st.button(f"↗ {q}", key=f"guide_{q}", width="stretch"):
                    st.session_state["pending_question"] = q
                    st.rerun()

if active_page == '🤖 FinPilot AI':
    st.subheader("FinPilot AI")
    st.write("Choose a suggested question or ask your own.")
    if st.button("✨ Browse example questions", width="content"):
        question_guide()

    question = st.chat_input("Ask about your spending, bills, budget or goals")
    suggested_question = S.pop("pending_question", None)
    active_question = suggested_question or question

    if active_question:
        st.chat_message("user").write(active_question)
        try:
            answer, evidence = agent.answer(active_question, df, {
                "today": today, "income": income, "savings": savings,
                "goal": goal, "budgets": core.BUDGETS
            })
            st.chat_message("assistant").write(answer)
            if evidence is not None and len(evidence):
                with st.expander("Show supporting transactions"):
                    st.dataframe(evidence, width="stretch")
        except Exception as exc:
            st.error(f"Couldn't answer that question: {exc}")

    st.caption("Examples: spending by category, changes since last month, subscriptions, upcoming bills, safe daily spending, unusual transactions, and savings-goal timing.")

if active_page == '📄 Report':
    st.subheader("Demo report")
    monthly = core.month_summary(df, cur)
    bullets = [
        f"Income {inr(monthly['income'])}, expenses {inr(monthly['expense'])}, savings rate {monthly['rate']:.0%}",
        f"Financial wellness score {health['total']}/100",
        f"Safe-to-spend estimate: {inr(safe['per_day'])} per day",
        f"Goal: {goal_name}, target {inr(goal_target)}, saved {inr(goal_saved)}",
    ]
    pdf = report.build_pdf(f"FinPilot demo report — {cur}", bullets, [o for o, _ in feed], [a for _, a in feed])
    st.download_button("⬇ Download demo report (PDF)", pdf, f"finpilot_demo_{cur}.pdf", "application/pdf")
    st.caption("This report is generated from fictional sample data and any expenses entered during this session.")
