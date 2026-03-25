"""
Stockbit Data Collector CLI

Usage:
    python3 cli.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()


# ─── Display ─────────────────────────────────────────────────────────────────

def _v(val, fmt=None):
    """Format nilai atau '-' jika None."""
    if val is None:
        return "[dim]-[/dim]"
    if fmt:
        try:
            return fmt.format(float(val))
        except (TypeError, ValueError):
            pass
    return str(val)


def show_price_panel(ticker: str, price_data: dict):
    company = price_data.get("company_name", ticker)
    price   = price_data.get("last_price")
    chg_pct = price_data.get("change_pct")
    high52  = price_data.get("week52_high")
    low52   = price_data.get("week52_low")

    chg_str = ""
    if chg_pct is not None:
        c = float(chg_pct)
        color = "green" if c >= 0 else "red"
        chg_str = f" [{color}]({c:+.2f}%)[/{color}]"

    price_str = f"[bold cyan]Rp {float(price):,.0f}[/bold cyan]{chg_str}" if price else "[dim]-[/dim]"
    range_str = f"52wk: Rp {float(low52):,.0f} – Rp {float(high52):,.0f}" if high52 and low52 else ""

    console.print(Panel(
        f"[bold white]{company}[/bold white]  [dim]({ticker})[/dim]\n"
        f"{price_str}    [dim]{range_str}[/dim]",
        title="[bold blue]◆ DATA SAHAM[/bold blue]",
        border_style="blue",
    ))


def show_fundamental_panel(fund: dict):
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    t.add_column("Metrik",   style="dim", width=24)
    t.add_column("Nilai",    justify="right", width=14)
    t.add_column("Metrik",   style="dim", width=24)
    t.add_column("Nilai",    justify="right", width=14)

    rows = [
        ("P/E (TTM)",       _v(fund.get("pe_ratio"),    "{:.2f}"),  "Net Margin",      _v(fund.get("net_margin"),    "{:.2f}%")),
        ("P/B",             _v(fund.get("pb_ratio"),    "{:.2f}"),  "Gross Margin",    _v(fund.get("gross_margin"),  "{:.2f}%")),
        ("P/S (TTM)",       _v(fund.get("ps_ratio"),    "{:.2f}"),  "Op Margin",       _v(fund.get("op_margin"),     "{:.2f}%")),
        ("EV/EBITDA",       _v(fund.get("ev_ebitda"),   "{:.2f}"),  "ROE",             _v(fund.get("roe"),           "{:.2f}%")),
        ("Earnings Yield",  _v(fund.get("earnings_yield"),"{:.2f}%"), "ROA",           _v(fund.get("roa"),           "{:.2f}%")),
        ("DER",             _v(fund.get("der"),         "{:.2f}"),  "ROIC",            _v(fund.get("roic"),          "{:.2f}%")),
        ("Current Ratio",   _v(fund.get("current_ratio"),"{:.2f}"), "Piotroski Score", _v(fund.get("piotroski_score"),"{:.0f}")),
        ("EPS (TTM)",       _v(fund.get("eps_ttm"),     "{:,.0f}"), "BVPS",            _v(fund.get("bvps"),          "{:,.0f}")),
    ]

    for r in rows:
        t.add_row(*r)

    console.print(Panel(t, title="[bold]Rasio & Fundamental[/bold]", border_style="cyan", padding=(0,1)))


def show_financial_panel(fund: dict):
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    t.add_column("Income Statement (TTM)",  style="dim", width=24)
    t.add_column("Miliar IDR",              justify="right", width=16)
    t.add_column("Balance Sheet",           style="dim", width=24)
    t.add_column("Miliar IDR",              justify="right", width=16)

    def _b(v):
        if v is None:
            return "[dim]-[/dim]"
        f = float(v)
        color = "green" if f > 0 else "red" if f < 0 else "dim"
        return f"[{color}]{f:>12,.0f}[/{color}]"

    rows = [
        ("Revenue",       _b(fund.get("revenue_ttm")),      "Total Assets",    _b(fund.get("total_assets"))),
        ("Gross Profit",  _b(fund.get("gross_profit_ttm")), "Total Equity",    _b(fund.get("total_equity"))),
        ("EBITDA",        _b(fund.get("ebitda_ttm")),       "Total Debt",      _b(fund.get("total_debt"))),
        ("Net Income",    _b(fund.get("net_income_ttm")),   "Net Debt",        _b(fund.get("net_debt"))),
        ("CFO",           _b(fund.get("cfo_ttm")),          "Cash",            _b(fund.get("cash_bs"))),
        ("FCF",           _b(fund.get("fcf_ttm")),          "Working Capital", _b(fund.get("working_capital"))),
        ("CapEx",         _b(fund.get("capex_ttm")),        "Total Liabilities",_b(fund.get("total_liabilities"))),
    ]

    for r in rows:
        t.add_row(*r)

    console.print(Panel(t, title="[bold]Laporan Keuangan[/bold]", border_style="cyan", padding=(0,1)))


def show_historical_summary(hist_rows: list):
    """Tampilkan ringkasan 8 kuartal terakhir."""
    if not hist_rows:
        return

    recent = sorted(hist_rows, key=lambda r: (r.get("year", 0), r.get("quarter", 0)), reverse=True)[:8]
    recent.reverse()

    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    t.add_column("Periode",    style="dim", width=10)
    t.add_column("Revenue (B)",  justify="right", width=14)
    t.add_column("Net Inc (B)",  justify="right", width=14)
    t.add_column("EPS",          justify="right", width=10)

    for r in recent:
        period = f"{r.get('year')}-Q{r.get('quarter')}"

        def _hv(v):
            if v is None:
                return "[dim]-[/dim]"
            f = float(v)
            color = "green" if f > 0 else "red" if f < 0 else "dim"
            return f"[{color}]{f:,.0f}[/{color}]"

        t.add_row(period, _hv(r.get("revenue")), _hv(r.get("net_income")), _hv(r.get("eps")))

    console.print(Panel(t, title="[bold]Historical Quarterly (8 terakhir)[/bold]", border_style="cyan", padding=(0,1)))


# ─── Collect ─────────────────────────────────────────────────────────────────

def collect(ticker: str):
    from src.database.repository import (
        upsert_ticker, save_fundamental, save_price,
        get_latest_fundamental, get_historical_rows,
    )
    from src.collector.historical import save_historical

    console.print(f"\n[dim]Mengambil data [bold]{ticker}[/bold]...[/dim]")

    fund       = None
    price_data = None
    hist_rows  = []

    with console.status(f"[cyan]Fetching fundamental + historical {ticker}...[/cyan]", spinner="dots"):
        try:
            from src.collector.fundamental import fetch_fundamental
            from src.collector.historical  import fetch_historical
            fund = fetch_fundamental(ticker)
            save_fundamental(ticker, fund)
            hist_rows = fetch_historical(ticker)
            save_historical(ticker, hist_rows)
            console.print(f"  [green]✓[/green] Fundamental & historical tersimpan ({len(hist_rows)} baris)")
        except Exception as e:
            console.print(f"  [yellow]⚠ Fundamental fetch gagal: {e}[/yellow]")
            fund      = get_latest_fundamental(ticker)
            hist_rows = get_historical_rows(ticker)
            if fund:
                console.print(f"  [dim]↳ Menggunakan cache DB[/dim]")

    with console.status(f"[cyan]Fetching price {ticker}...[/cyan]", spinner="dots"):
        try:
            from src.collector.price import fetch_price
            price_data = fetch_price(ticker)
            save_price(ticker, price_data)
            if price_data.get("company_name"):
                upsert_ticker(ticker, company_name=price_data["company_name"])
            console.print(f"  [green]✓[/green] Price tersimpan: Rp {float(price_data['last_price']):,.0f}")
        except Exception as e:
            console.print(f"  [yellow]⚠ Price fetch gagal: {e}[/yellow]")

    if not fund and not price_data:
        console.print(f"[red]✗ Tidak ada data untuk {ticker}. Pastikan kode emiten benar.[/red]")
        return

    console.print()
    if price_data:
        show_price_panel(ticker, price_data)
    if fund:
        show_fundamental_panel(fund)
        show_financial_panel(fund)
    if hist_rows:
        show_historical_summary(hist_rows)
    elif fund:
        hist_rows = get_historical_rows(ticker)
        if hist_rows:
            show_historical_summary(hist_rows)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    console.print(Panel(
        "[bold cyan]Stockbit Data Collector[/bold cyan]\n"
        "[dim]Ambil & simpan data fundamental, harga, dan historical per emiten IDX[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))

    while True:
        console.print()
        ticker = Prompt.ask(
            "[bold]Masukkan kode emiten[/bold] [dim](contoh: BBCA, TLKM, BUMI) atau [red]exit[/red] untuk keluar[/dim]"
        ).strip().upper()

        if ticker in ("EXIT", "Q", "QUIT", ""):
            console.print("\n[dim]Sampai jumpa![/dim]")
            break

        collect(ticker)


if __name__ == "__main__":
    main()
