import os
import re
from . import core
from .core import inr

BLOCK = re.compile(r"\b(stocks?|shares?|mutual funds?|sip|etf|crypto|bitcoin|invest\w*|nifty|sensex|trading|ipo|fd rates?)\b", re.I)
REFUSAL = ("I can't recommend stocks, funds, crypto or any investment, because that is personalised financial advice and "
           "I'm not a licensed advisor. I can explain your spending, savings rate and goal timeline, and show how redirecting "
           "money from one category changes your goal date. Try the What-If tab.")
SYSTEM = ("You explain verified personal-finance facts in 3-4 plain sentences. Never change or add numbers. "
          "Never recommend investments or financial products.")


def polish(q, text):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return text
    try:
        import anthropic
        r = anthropic.Anthropic().messages.create(
            model="claude-sonnet-5-5", max_tokens=400, system=SYSTEM,
            messages=[{"role": "user", "content": f"Question: {q}\nVerified facts:\n{core.mask_pii(text)}"}])
        return r.content[0].text
    except Exception:
        return text


def answer(q, df, cfg):
    """Returns (text, evidence_df_or_None). Intent routing -> code computes -> text explains."""
    ql = q.lower()
    if BLOCK.search(ql):
        return REFUSAL, None
    today, cur = cfg["today"], cfg["today"].to_period("M")
    prev = cur - 1
    rec = core.recurring(df)
    ev = None
    if re.search(r"committed", ql):
        s = core.safe_to_spend(df, rec, today, cfg["income"], cfg["savings"])
        t = (f"{s['committed_pct']:.0f}% of this month's income is already committed: bills paid plus {inr(s['upcoming'])} "
             f"still due plus {inr(cfg['savings'])} set aside for savings."); ev = s["upcoming_df"]
    elif re.search(r"safe|today|can i spend", ql):
        s = core.safe_to_spend(df, rec, today, cfg["income"], cfg["savings"])
        t = f"You can safely spend about {inr(s['per_day'])} per day for the remaining {s['days_left']} days."
    elif re.search(r"increase|vs last|last month|why|badh|compared", ql):
        a, b = core.month_summary(df, prev)["cats"], core.month_summary(df, cur)["cats"]
        d = (b - a.reindex(b.index).fillna(0)).sort_values(ascending=False)
        cat = d.index[0]
        w = core.why(df, cat, cur, prev)
        t = (f"{cat} rose by {inr(w['delta'])}. More orders ({w['n0']} to {w['n1']}) account for {inr(w['freq'])}; "
             f"a bigger average size ({inr(w['a0'])} to {inr(w['a1'])}) accounts for {inr(w['size'])}."
             + (f" New merchants: {', '.join(w['new'])}." if w["new"] else "")); ev = w["evidence"]
    elif re.search(r"subscri|recurring", ql):
        s = rec[rec.category == "Subscriptions"] if len(rec) else rec
        t = (f"You have {len(s)} subscriptions costing {inr(s.monthly_cost.sum())} a month: "
             + ", ".join(f"{r.merchant} {inr(r.amount)}" for r in s.itertuples()) + "."); ev = s
    elif re.search(r"upcoming|due|bill|next|coming", ql):
        u = core.schedule(rec, today + __import__("pandas").Timedelta(days=1), today + __import__("pandas").Timedelta(days=30))
        t = f"{len(u)} known payments totalling {inr(u.amount.sum())} are due in the next 30 days."; ev = u
    elif re.search(r"unusual|anomal|duplicate|strange|suspicious", ql):
        a = core.anomalies(df)
        t = f"{len(a)} transactions look unusual." if len(a) else "Nothing unusual found."; ev = a
    elif re.search(r"goal|laptop|emergency", ql):
        n = core.monthly_net(df)
        m = core.months_to_goal(cfg["goal"]["target"], cfg["goal"]["saved"], n)
        t = f"At your average saving of {inr(n)}/month, '{cfg['goal']['name']}' arrives in about {m:.1f} months."
    elif re.search(r"most|zyada|sabse|kharch|top|highest|spend", ql):
        c = core.month_summary(df, cur)["cats"]
        t = "Top categories this month: " + ", ".join(f"{k} {inr(v)}" for k, v in c.head(3).items()) + "."
        ev = core.month_of(df, cur)[lambda x: x.amount < 0].nsmallest(8, "amount")
    else:
        return ("I can answer: where I spent most, what increased vs last month, which subscriptions I have, upcoming bills, "
                "how much of my budget is committed, what's safe to spend today, unusual transactions, and goal timing."), None
    return polish(q, t), ev
