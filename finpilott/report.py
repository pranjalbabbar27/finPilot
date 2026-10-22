import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _t(x):
    return str(x).replace("₹", "Rs ")


def build_pdf(title, summary, observations, actions):
    buf = io.BytesIO()
    st = getSampleStyleSheet()
    el = [Paragraph(_t(title), st["Title"])]
    for head, items in (("Summary", summary), ("Observations", observations), ("Action items", actions)):
        el += [Spacer(1, 10), Paragraph(head, st["Heading2"])]
        el += [Paragraph("• " + _t(i), st["BodyText"]) for i in items] or [Paragraph("Nothing to report.", st["BodyText"])]
    el += [Spacer(1, 14), Paragraph("FinPilot explains your data. It does not give investment or financial advice.", st["Italic"])]
    SimpleDocTemplate(buf, pagesize=A4).build(el)
    return buf.getvalue()
