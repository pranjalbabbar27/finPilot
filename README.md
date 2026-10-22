# Pranjal (FinPilot engine) — a student money companion: what can I safely spend today, and how does every rupee move my goal?

Python + Streamlit. No Java. File upload only (no bank linking). No investment features.

## Run in VS Code
    python -m venv .venv
    .venv\Scripts\activate        (Mac/Linux: source .venv/bin/activate)
    pip install -r requirements.txt
    streamlit run app.py

Click **Load demo persona** in the sidebar for planted patterns (price hike, duplicate charge, forgotten subscription, big new merchant).

Optional: set `ANTHROPIC_API_KEY` so Claude phrases answers. Numbers are ALWAYS computed in pandas; the LLM only explains,
and PII (account numbers, emails, UPI ids) is masked before anything is sent.

Upload format: CSV with `date, description, amount` (negative = spent) or `date, description, debit, credit`.
PDF statements: table-based PDFs with a signed amount column.

## Files
- app.py — Pranjal website (Overview, Add expense, Spending, Smart alerts, Goal planner, Ask Pranjal, Report)
- finpilot/core.py — all calculations
- finpilot/agent.py — Q&A, guardrail, optional Claude phrasing
- finpilot/report.py — monthly PDF
- finpilot/sample.py — synthetic persona
