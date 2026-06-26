from typing import List, Dict, Optional
from datetime import datetime
import io
import logging

logger = logging.getLogger(__name__)

REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass


def _format_currency(value: float) -> str:
    return f"\u20b9{value:,.2f}"


def _format_percent(value: float) -> str:
    return f"{value:+.2f}%" if value else "0.00%"


def _get_chart_json(holdings: List[Dict]) -> str:
    import json
    chart_data = []
    for h in holdings:
        weight = h.get("weight_pct", h.get("weight", 0))
        chart_data.append({
            "symbol": h.get("symbol", "N/A"),
            "value": h.get("current_value", h.get("value", 0)),
            "weight": weight,
            "pnl": h.get("pnl", h.get("unrealized_pnl", 0)),
        })
    return json.dumps(chart_data, indent=2)


def generate_pdf_report(
    portfolio_data: Dict,
    holdings: List[Dict],
    transactions: List[Dict],
) -> bytes:
    if REPORTLAB_AVAILABLE:
        return _generate_reportlab_pdf(portfolio_data, holdings, transactions)
    html = generate_html_report(portfolio_data, holdings, transactions)
    note = (
        "<!-- PDF generation note: reportlab is not installed. "
        "This HTML can be converted to PDF using weasyprint or wkhtmltopdf. "
        "Install reportlab with: pip install reportlab -->\n"
    )
    return (note + html).encode("utf-8")


def _generate_reportlab_pdf(
    portfolio_data: Dict,
    holdings: List[Dict],
    transactions: List[Dict],
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"], fontSize=22, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle", parent=styles["Normal"],
        fontSize=10, textColor=colors.grey, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"],
        fontSize=14, spaceAfter=8, spaceBefore=16
    )
    normal_style = ParagraphStyle(
        "CustomNormal", parent=styles["Normal"], fontSize=9, spaceAfter=4
    )
    small_style = ParagraphStyle(
        "SmallText", parent=styles["Normal"],
        fontSize=7, textColor=colors.grey, alignment=1
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=styles["Normal"],
        fontSize=7, textColor=colors.grey, alignment=1,
        spaceBefore=20
    )

    elements = []

    elements.append(Paragraph(f"{portfolio_data.get('name', 'Portfolio Report')}", title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | "
        f"User: {portfolio_data.get('user_name', portfolio_data.get('user_email', 'N/A'))}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E0E0E0")))
    elements.append(Spacer(1, 6))

    total_value = portfolio_data.get("total_value", sum(h.get("current_value", h.get("value", 0)) for h in holdings))
    total_investment = portfolio_data.get("total_investment", sum(h.get("invested_amount", 0) for h in holdings))
    total_pnl = total_value - total_investment
    returns_pct = (total_pnl / total_investment * 100) if total_investment else 0

    elements.append(Paragraph("Portfolio Summary", heading_style))
    summary_data = [
        ["Metric", "Value"],
        ["Total Value", _format_currency(total_value)],
        ["Total Investment", _format_currency(total_investment)],
        ["Total P&L", _format_currency(total_pnl)],
        ["Returns", _format_percent(returns_pct)],
        ["Holdings Count", str(len(holdings))],
        ["Report Date", datetime.now().strftime("%d-%m-%Y")],
    ]
    summary_table = Table(summary_data, colWidths=[120, 160])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F5F5")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#333333")),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    if portfolio_data.get("returns_data"):
        elements.append(Paragraph("Performance Chart Data", heading_style))
        elements.append(Paragraph(
            f"<pre>{json.dumps(portfolio_data['returns_data'], indent=2)}</pre>" if isinstance(portfolio_data.get("returns_data"), dict)
            else str(portfolio_data.get("returns_data", "")),
            ParagraphStyle("Code", parent=normal_style, fontSize=7, fontName="Courier")
        ))
        elements.append(Spacer(1, 8))

    if holdings:
        elements.append(Paragraph("Holdings Details", heading_style))
        header = ["Symbol", "Qty", "Avg Price", "Curr Price", "Value", "P&L", "Weight"]
        data_rows = [header]
        for h in holdings:
            qty = h.get("quantity", h.get("qty", 0))
            avg_price = h.get("avg_price", h.get("average_price", 0))
            curr_price = h.get("current_price", h.get("ltp", 0))
            value = h.get("current_value", h.get("value", 0))
            pnl = h.get("pnl", h.get("unrealized_pnl", 0))
            weight = h.get("weight_pct", h.get("weight", 0))
            data_rows.append([
                h.get("symbol", "N/A"),
                str(qty),
                _format_currency(avg_price),
                _format_currency(curr_price),
                _format_currency(value),
                _format_currency(pnl),
                f"{weight:.1f}%",
            ])
        holdings_table = Table(data_rows, colWidths=[55, 40, 55, 55, 60, 60, 40])
        pnl_col_idx = 5
        holdings_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FAFAFA")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FAFAFA"), colors.white]),
        ]))
        for i in range(1, len(data_rows)):
            try:
                pnl_val = float(data_rows[i][pnl_col_idx].replace("\u20b9", "").replace(",", ""))
                if pnl_val > 0:
                    holdings_table.setStyle(TableStyle([
                        ("TEXTCOLOR", (pnl_col_idx, i), (pnl_col_idx, i), colors.HexColor("#2E7D32"))
                    ]))
                elif pnl_val < 0:
                    holdings_table.setStyle(TableStyle([
                        ("TEXTCOLOR", (pnl_col_idx, i), (pnl_col_idx, i), colors.HexColor("#C62828"))
                    ]))
            except (ValueError, IndexError):
                pass
        elements.append(holdings_table)
        elements.append(Spacer(1, 12))

    if portfolio_data.get("sector_allocation"):
        elements.append(Paragraph("Sector Allocation", heading_style))
        sectors = portfolio_data["sector_allocation"]
        if isinstance(sectors, dict):
            sec_header = ["Sector", "Allocation %"]
            sec_rows = [sec_header]
            for sector, pct in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
                sec_rows.append([sector, f"{pct:.1f}%"])
            sec_table = Table(sec_rows, colWidths=[180, 100])
            sec_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F5F5F5"), colors.white]),
            ]))
            elements.append(sec_table)
            elements.append(Spacer(1, 12))

    if transactions:
        elements.append(Paragraph("Recent Transactions", heading_style))
        tx_header = ["Date", "Symbol", "Type", "Qty", "Price", "Total"]
        tx_rows = [tx_header]
        for tx in transactions[:20]:
            tx_rows.append([
                tx.get("date", tx.get("timestamp", "N/A"))[:10],
                tx.get("symbol", "N/A"),
                tx.get("type", tx.get("transaction_type", "N/A")).upper(),
                str(tx.get("quantity", tx.get("qty", 0))),
                _format_currency(tx.get("price", 0)),
                _format_currency(tx.get("total", tx.get("amount", 0))),
            ])
        tx_table = Table(tx_rows, colWidths=[65, 50, 55, 40, 55, 55])
        tx_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#37474F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FAFAFA"), colors.white]),
        ]))
        for i in range(1, len(tx_rows)):
            try:
                tx_type = tx_rows[i][2].lower()
                if "buy" in tx_type:
                    tx_table.setStyle(TableStyle([
                        ("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#2E7D32"))
                    ]))
                elif "sell" in tx_type:
                    tx_table.setStyle(TableStyle([
                        ("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#C62828"))
                    ]))
            except IndexError:
                pass
        elements.append(tx_table)
        elements.append(Spacer(1, 12))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E0E0E0")))
    elements.append(Spacer(1, 8))

    disclaimer_text = (
        "Disclaimer: This report is for informational purposes only and does not constitute "
        "investment advice. Past performance is not indicative of future results. "
        "Please consult a SEBI-registered financial advisor before making investment decisions. "
        f"Generated by Stoxly.ai on {datetime.now().strftime('%d %B %Y')}."
    )
    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    watermark = ParagraphStyle(
        "Watermark", parent=normal_style,
        fontSize=6, textColor=colors.HexColor("#CCCCCC"), alignment=1
    )
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Stoxly.ai - AI-Powered Indian Stock Market Platform", watermark))

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def generate_html_report(
    portfolio_data: Dict,
    holdings: List[Dict],
    transactions: List[Dict],
) -> str:
    total_value = portfolio_data.get("total_value", sum(h.get("current_value", h.get("value", 0)) for h in holdings))
    total_investment = portfolio_data.get("total_investment", sum(h.get("invested_amount", 0) for h in holdings))
    total_pnl = total_value - total_investment
    returns_pct = (total_pnl / total_investment * 100) if total_investment else 0

    holdings_rows = ""
    for h in holdings:
        qty = h.get("quantity", h.get("qty", 0))
        avg_price = h.get("avg_price", h.get("average_price", 0))
        curr_price = h.get("current_price", h.get("ltp", 0))
        value = h.get("current_value", h.get("value", 0))
        pnl = h.get("pnl", h.get("unrealized_pnl", 0))
        weight = h.get("weight_pct", h.get("weight", 0))
        pnl_class = "positive" if pnl >= 0 else "negative"
        holdings_rows += f"""
        <tr>
            <td>{h.get("symbol", "N/A")}</td>
            <td>{qty}</td>
            <td>{_format_currency(avg_price)}</td>
            <td>{_format_currency(curr_price)}</td>
            <td>{_format_currency(value)}</td>
            <td class="{pnl_class}">{_format_currency(pnl)}</td>
            <td>{weight:.1f}%</td>
        </tr>"""

    sector_rows = ""
    sectors = portfolio_data.get("sector_allocation", {})
    if isinstance(sectors, dict):
        for sector, pct in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            bar_width = min(pct * 5, 100)
            sector_rows += f"""
            <tr>
                <td>{sector}</td>
                <td>
                    <div class="sector-bar-container">
                        <div class="sector-bar" style="width: {bar_width}%"></div>
                    </div>
                </td>
                <td style="text-align: right">{pct:.1f}%</td>
            </tr>"""

    tx_rows = ""
    for tx in transactions[:20]:
        tx_type = tx.get("type", tx.get("transaction_type", "")).lower()
        tx_class = "tx-buy" if "buy" in tx_type else "tx-sell"
        tx_rows += f"""
        <tr class="{tx_class}">
            <td>{str(tx.get("date", tx.get("timestamp", "N/A")))[:10]}</td>
            <td>{tx.get("symbol", "N/A")}</td>
            <td>{tx_type.upper()}</td>
            <td>{tx.get("quantity", tx.get("qty", 0))}</td>
            <td>{_format_currency(tx.get("price", 0))}</td>
            <td>{_format_currency(tx.get("total", tx.get("amount", 0)))}</td>
        </tr>"""

    chart_json = _get_chart_json(holdings)

    pnl_class = "positive" if total_pnl >= 0 else "negative"
    pnl_sign = "+" if total_pnl >= 0 else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{portfolio_data.get("name", "Portfolio Report")} - Stoxly.ai</title>
<style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; color: #333; background: #f4f6f9; padding: 20px; }}
    .report-container {{ max-width: 900px; margin: 0 auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 20px rgba(0,0,0,0.08); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #1A237E 0%, #283593 100%); color: #fff; padding: 32px 40px; }}
    .header h1 {{ font-size: 26px; font-weight: 700; margin-bottom: 4px; }}
    .header .meta {{ font-size: 13px; opacity: 0.85; line-height: 1.6; }}
    .body {{ padding: 32px 40px; }}
    .section {{ margin-bottom: 28px; }}
    .section-title {{ font-size: 16px; font-weight: 600; color: #1A237E; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #E8EAF6; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 8px; }}
    .summary-card {{ background: #f8f9fb; border-radius: 8px; padding: 14px; text-align: center; }}
    .summary-card .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; margin-bottom: 4px; }}
    .summary-card .value {{ font-size: 20px; font-weight: 700; }}
    .summary-card .value.positive {{ color: #2E7D32; }}
    .summary-card .value.negative {{ color: #C62828; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ background: #1A237E; color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.3px; }}
    td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f8f9fb; }}
    .positive {{ color: #2E7D32; }}
    .negative {{ color: #C62828; }}
    .sector-bar-container {{ background: #E8EAF6; border-radius: 4px; height: 18px; overflow: hidden; }}
    .sector-bar {{ height: 100%; background: linear-gradient(90deg, #3F51B5, #5C6BC0); border-radius: 4px; transition: width 0.3s; }}
    .tx-buy td:nth-child(3) {{ color: #2E7D32; font-weight: 600; }}
    .tx-sell td:nth-child(3) {{ color: #C62828; font-weight: 600; }}
    .chart-data {{ background: #f8f9fb; border: 1px solid #e0e0e0; border-radius: 6px; padding: 12px; font-family: 'Consolas', 'Courier New', monospace; font-size: 11px; line-height: 1.5; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; }}
    .footer {{ background: #f8f9fb; border-top: 1px solid #e0e0e0; padding: 20px 40px; text-align: center; font-size: 11px; color: #888; line-height: 1.6; }}
    .footer strong {{ color: #555; }}
    @media print {{
        body {{ background: #fff; padding: 0; }}
        .report-container {{ box-shadow: none; border-radius: 0; }}
        .header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        th {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .sector-bar {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .summary-card {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #f0f0f0; }}
    }}
</style>
</head>
<body>
<div class="report-container">
    <div class="header">
        <h1>{portfolio_data.get("name", "Portfolio Report")}</h1>
        <div class="meta">
            Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p")}<br>
            User: {portfolio_data.get("user_name", portfolio_data.get("user_email", "N/A"))}
        </div>
    </div>

    <div class="body">
        <div class="section">
            <div class="section-title">Portfolio Summary</div>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="label">Total Value</div>
                    <div class="value">{_format_currency(total_value)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Total Investment</div>
                    <div class="value">{_format_currency(total_investment)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Total P&amp;L</div>
                    <div class="value {pnl_class}">{pnl_sign}{_format_currency(abs(total_pnl))}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Returns</div>
                    <div class="value {pnl_class}">{_format_percent(returns_pct)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Holdings</div>
                    <div class="value">{len(holdings)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Report Date</div>
                    <div class="value" style="font-size:14px">{datetime.now().strftime("%d-%m-%Y")}</div>
                </div>
            </div>
        </div>"""

    if portfolio_data.get("returns_data"):
        import json
        returns_json = json.dumps(portfolio_data["returns_data"], indent=2) if isinstance(
            portfolio_data.get("returns_data"), dict
        ) else str(portfolio_data.get("returns_data", ""))
        html += f"""
        <div class="section">
            <div class="section-title">Performance Chart Data</div>
            <div class="chart-data">{returns_json}</div>
        </div>"""

    if holdings:
        html += f"""
        <div class="section">
            <div class="section-title">Holdings Details</div>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Qty</th>
                        <th>Avg Price</th>
                        <th>Curr Price</th>
                        <th>Value</th>
                        <th>P&amp;L</th>
                        <th>Weight</th>
                    </tr>
                </thead>
                <tbody>
                    {holdings_rows}
                </tbody>
            </table>
        </div>"""

    if sector_rows:
        html += f"""
        <div class="section">
            <div class="section-title">Sector Allocation</div>
            <table>
                <thead>
                    <tr><th>Sector</th><th></th><th style="text-align:right">Allocation</th></tr>
                </thead>
                <tbody>
                    {sector_rows}
                </tbody>
            </table>
        </div>"""

    if tx_rows:
        html += f"""
        <div class="section">
            <div class="section-title">Recent Transactions</div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Symbol</th>
                        <th>Type</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {tx_rows}
                </tbody>
            </table>
        </div>"""

    html += f"""
    </div>

    <div class="section" style="padding: 0 40px 8px;">
        <div class="section-title">Chart Data (JSON)</div>
        <div class="chart-data">{chart_json}</div>
    </div>
</div>

    <div class="footer">
        <strong>Disclaimer:</strong> This report is for informational purposes only and does not constitute investment advice.
        Past performance is not indicative of future results. Please consult a SEBI-registered financial advisor
        before making investment decisions.<br><br>
        Generated by <strong>Stoxly.ai</strong> on {datetime.now().strftime("%d %B %Y")} |
        AI-Powered Indian Stock Market Platform
    </div>
</div>
</body>
</html>"""

    return html
