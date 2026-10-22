"""All numbers are computed here in pandas. The LLM never does math."""
import re
import numpy as np
import pandas as pd

RULES = [
    ("Income", r"salary|payroll|interest credit"), ("Rent", r"\brent\b"), ("EMI", r"\bemi\b|loan"),
    ("Food Delivery", r"swiggy|zomato"), ("Groceries", r"bigbasket|blinkit|zepto|dmart|grocer"),
    ("Subscriptions", r"netflix|spotify|hotstar|prime video|youtube premium|gym|cult"),
    ("Shopping", r"amazon|amzn|flipkart|myntra|croma"), ("Transport", r"uber|\bola\b|metro|irctc|fuel|petrol"),
    ("Utilities", r"electricity|bses|airtel|jio|broadband"), ("Dining", r"cafe|restaurant|starbucks|dominos"),
]
MERCHANTS = [(r"amzn|amazon", "Amazon"), (r"swiggy", "Swiggy"), (r"zomato", "Zomato"), (r"netflix", "Netflix"),
             (r"spotify", "Spotify"), (r"hotstar", "Hotstar"), (r"cult|gym", "Gym"), (r"uber", "Uber"),
             (r"blinkit", "Blinkit"), (r"starbucks", "Starbucks"), (r"croma", "Croma"), (r"airtel", "Airtel"),
             (r"bses|electricity", "Electricity"), (r"\bemi\b", "Loan EMI"), (r"\brent\b", "Rent"), (r"salary", "Salary")]
BUDGETS = {"Food Delivery": 6000, "Groceries": 5000, "Shopping": 8000, "Dining": 2000,
           "Transport": 2500, "Subscriptions": 3000, "Utilities": 4000}
CATEGORIES = [c for c, _ in RULES] + ["Other"]
FREQ_MONTHLY = {"Weekly": 4.33, "Monthly": 1, "Annual": 1 / 12}


def inr(x):
    return f"₹{x:,.0f}"


# ---------- ingest & clean ----------
def mask_pii(t):
    t = re.sub(r"\b\d{9,18}\b", "XXXX", str(t))
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", t)
    return re.sub(r"\b[\w.-]+@[a-zA-Z]{2,}\b", "[upi-id]", t)


def _num(c):
    try:
        return float(str(c).replace(",", "").replace("₹", "").strip())
    except ValueError:
        return None


def read_pdf(f):
    import pdfplumber
    out = []
    with pdfplumber.open(f) as pdf:
        for p in pdf.pages:
            for t in p.extract_tables():
                for r in t:
                    c = [str(x or "").strip() for x in r]
                    d = pd.to_datetime(c[0], errors="coerce", dayfirst=True)
                    nums = [n for n in (_num(x) for x in c[2:]) if n is not None]
                    if pd.notna(d) and nums:
                        out.append((d, c[1], nums[0]))
    return pd.DataFrame(out, columns=["date", "description", "amount"])


def load_file(f):
    if f.name.lower().endswith(".pdf"):
        return read_pdf(f)
    d = pd.read_csv(f)
    d.columns = [c.strip().lower() for c in d.columns]
    ren = {}
    for c in d.columns:
        if c in ("narration", "particulars", "details", "remarks"): ren[c] = "description"
        if c in ("txn date", "transaction date", "value date"): ren[c] = "date"
        if c in ("withdrawal", "withdrawals", "debit amount"): ren[c] = "debit"
        if c in ("deposit", "deposits", "credit amount"): ren[c] = "credit"
    d = d.rename(columns=ren)
    if "amount" not in d.columns:
        d["amount"] = d.get("credit", 0).fillna(0) - d.get("debit", 0).fillna(0)
    d["date"] = pd.to_datetime(d["date"], dayfirst=True, errors="coerce")
    return d[["date", "description", "amount"]].dropna(subset=["date"])


def merchant_of(desc):
    s = desc.lower()
    for pat, name in MERCHANTS:
        if re.search(pat, s):
            return name
    w = re.sub(r"upi[-/ ]|pos |\*.*|\d+|[^a-z ]", " ", s).split()
    return " ".join(w[:2]).title() or "Unknown"


def categorize(m, desc):
    t = f"{m} {desc}".lower()
    for cat, pat in RULES:
        if re.search(pat, t):
            return cat
    return "Other"


def prep(df, corrections=None):
    corrections = corrections or {}
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["amount"] = pd.to_numeric(d["amount"])
    d["description"] = d["description"].astype(str).map(mask_pii)
    d["merchant"] = d["description"].map(merchant_of)
    d["category"] = [("Income" if a > 0 else corrections.get(m) or categorize(m, ds))
                     for a, m, ds in zip(d.amount, d.merchant, d.description)]
    return d.sort_values("date").reset_index(drop=True)


# ---------- recurring ----------
def _step(d, freq):
    return d + {"Weekly": pd.Timedelta(days=7), "Monthly": pd.DateOffset(months=1),
                "Annual": pd.DateOffset(years=1)}[freq]


REC_COLS = ["merchant", "category", "frequency", "amount", "prev_amount", "hike", "last", "monthly_cost", "count"]


def recurring(df):
    res = []
    for m, g in df[df.amount < 0].groupby("merchant"):
        g = g.sort_values("date")
        if len(g) < 3:
            continue
        gaps = g.date.diff().dt.days.dropna()
        gap = gaps.median()
        freq = "Weekly" if 6 <= gap <= 8 else "Monthly" if 26 <= gap <= 35 else "Annual" if 350 <= gap <= 380 else None
        if not freq or gaps.std() > max(3, 0.2 * gap):
            continue
        a = g.amount.abs().values
        base = np.median(a[:-1])
        if np.std(a[:-1]) / base > 0.15:
            continue
        res.append(dict(merchant=m, category=g.category.iloc[-1], frequency=freq, amount=a[-1], prev_amount=base,
                        hike=bool(a[-1] > base * 1.03), last=g.date.max(),
                        monthly_cost=a[-1] * FREQ_MONTHLY[freq], count=len(g)))
    return pd.DataFrame(res, columns=REC_COLS)


def schedule(rec, start, end):
    out = []
    for r in rec.itertuples():
        d = r.last
        while True:
            d = _step(d, r.frequency)
            if d > end:
                break
            if d >= start:
                out.append((d, r.merchant, r.amount))
    return pd.DataFrame(out, columns=["date", "merchant", "amount"]).sort_values("date").reset_index(drop=True)


# ---------- unusual spending ----------
def anomalies(df):
    ex = df[df.amount < 0].copy()
    ex["abs"] = ex.amount.abs()
    flags = {}
    for c, g in ex.groupby("category"):
        if len(g) < 5:
            continue
        med = g["abs"].median()
        mad = (g["abs"] - med).abs().median()
        if mad == 0:
            continue
        z = 0.6745 * (g["abs"] - med) / mad
        for i in g.index[z > 3.5]:
            flags[i] = f"Unusually large for {c}"
    for _, g in ex.sort_values("date").groupby(["merchant", "abs"]):
        if len(g) > 1:
            for i, gap in zip(g.index[1:], g.date.diff().dt.days.dropna()):
                if gap <= 2:
                    flags[i] = "Possible duplicate charge"
    if (ex.date.max() - ex.date.min()).days > 60:
        first = ex.groupby("merchant").date.min()
        new = first[first > ex.date.max() - pd.Timedelta(days=30)].index
        for i in ex[ex.merchant.isin(new) & (ex["abs"] > 2 * ex["abs"].median())].index:
            flags.setdefault(i, "New merchant, large amount")
    out = df.loc[list(flags)].copy()
    out["reason"] = [flags[i] for i in out.index]
    return out.sort_values("date")


# ---------- summaries, budgets ----------
def month_of(df, p):
    return df[df.date.dt.to_period("M") == p]


def month_summary(df, p):
    m = month_of(df, p)
    inc, exp = m[m.amount > 0].amount.sum(), -m[m.amount < 0].amount.sum()
    cats = (-m[m.amount < 0].groupby("category").amount.sum()).sort_values(ascending=False)
    return dict(income=inc, expense=exp, net=inc - exp, rate=(inc - exp) / inc if inc else 0, cats=cats)


def budget_status(df, budgets, p):
    s = month_summary(df, p)["cats"]
    rows = [(c, b, s.get(c, 0), 100 * s.get(c, 0) / b if b else 0) for c, b in budgets.items()]
    return pd.DataFrame(rows, columns=["category", "budget", "spent", "pct"])


def monthly_net(df):
    g = df.groupby(df.date.dt.to_period("M")).amount.sum()
    if len(g) > 1 and df.date.max().normalize() < (df.date.max() + pd.offsets.MonthEnd(0)).normalize():
        g = g[:-1]
    return float(g.mean())


# ---------- hero features ----------
def safe_to_spend(df, rec, today, income, savings):
    eom = today + pd.offsets.MonthEnd(0)
    p = today.to_period("M")
    m = month_of(df, p)
    spent = -m[m.amount < 0].amount.sum()
    paid_bills = -m[(m.amount < 0) & m.merchant.isin(rec.merchant)].amount.sum()
    up = schedule(rec, today + pd.Timedelta(days=1), eom)
    upcoming = up.amount.sum()
    days_left = (eom - today).days + 1
    avail = income - savings - spent - upcoming
    return dict(per_day=max(avail, 0) / days_left, available=avail, days_left=days_left, upcoming=upcoming,
                committed=paid_bills + upcoming + savings, committed_pct=100 * (paid_bills + upcoming + savings) / income,
                upcoming_df=up)


def goal_clock(amount, net):
    return amount / (net / 30) if net > 0 else float("inf")


def why(df, cat, cur, prev):
    def part(p):
        return month_of(df, p)[lambda x: (x.category == cat) & (x.amount < 0)]
    a, b = part(prev), part(cur)
    n0, n1 = len(a), len(b)
    a0 = a.amount.abs().mean() if n0 else 0
    a1 = b.amount.abs().mean() if n1 else 0
    new = sorted(set(b.merchant) - set(a.merchant))
    return dict(delta=b.amount.abs().sum() - a.amount.abs().sum(), freq=(n1 - n0) * a0, size=n1 * (a1 - a0),
                n0=n0, n1=n1, a0=a0, a1=a1, new=new, evidence=b)


def months_to_goal(target, saved, net):
    return (target - saved) / net if net > 0 else float("inf")


def whatif(df, rec, goal, cancel, cat, pct, cur):
    net = monthly_net(df)
    extra = rec[rec.merchant.isin(cancel)].monthly_cost.sum()
    extra += month_summary(df, cur - 1)["cats"].get(cat, 0) * pct / 100
    return dict(before=months_to_goal(goal["target"], goal["saved"], net),
                after=months_to_goal(goal["target"], goal["saved"], net + extra), extra=extra, net=net)


def forecast(df, rec, today, balance, income, days=30):
    nonrec = df[(df.amount < 0) & ~df.merchant.isin(rec.merchant) & (df.date > today - pd.Timedelta(days=30))]
    daily = -nonrec.amount.sum() / 30
    sal = df[df.amount > 0]
    sal_day = int(sal.date.dt.day.mode().iloc[0]) if len(sal) else 1
    sched = schedule(rec, today + pd.Timedelta(days=1), today + pd.Timedelta(days=days))
    rows, bal = [], balance
    for i in range(1, days + 1):
        d = today + pd.Timedelta(days=i)
        bal -= daily + sched[sched.date == d].amount.sum()
        if d.day == sal_day:
            bal += income
        rows.append((d, bal))
    f = pd.DataFrame(rows, columns=["date", "balance"])
    f["pressure"] = f.balance < 0.1 * income
    return f


def health(df, rec, budgets, cur, balance, today):
    s = month_summary(df, cur)
    sr = min(1, max(0, s["rate"] / 0.2)) * 40
    bs = budget_status(df, budgets, cur)
    ba = (bs.pct <= 100).mean() * 30
    bills = schedule(rec, today + pd.Timedelta(days=1), today + pd.Timedelta(days=30)).amount.sum()
    bc = (min(1, balance / bills) if bills else 1) * 30
    return dict(total=round(sr + ba + bc), savings=round(sr), budget=round(ba), bills=round(bc))


def radar(df, rec, today, budgets, anoms, pressure=None):
    out = []
    for r in rec.itertuples():
        d = (_step(r.last, r.frequency) - today).days
        if 0 <= d <= 5:
            out.append((f"{r.merchant} renews in {d} day(s) for {inr(r.amount)}", f"Confirm you still use {r.merchant}"))
        if r.hike:
            out.append((f"{r.merchant} rose from {inr(r.prev_amount)} to {inr(r.amount)}", f"Decide if {r.merchant} is still worth the new price"))
    left = (today + pd.offsets.MonthEnd(0) - today).days
    for r in budget_status(df, budgets, today.to_period("M")).itertuples():
        if r.pct >= 80:
            out.append((f"{r.category} budget {r.pct:.0f}% used with {left} days left", f"Pause {r.category} spending until month end"))
    for r in anoms[anoms.date >= today - pd.Timedelta(days=45)].itertuples():
        out.append((f"{r.reason}: {r.merchant} {inr(abs(r.amount))} on {r.date:%d %b}", "Verify this transaction, dispute if wrong"))
    if pressure is not None:
        out.append((f"Balance may get tight on {pressure:%d %b}", "Delay discretionary spending before that date"))
    return out
