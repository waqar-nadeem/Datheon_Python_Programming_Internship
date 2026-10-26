#!/usr/bin/env python3
"""
Stock Portfolio Performance Tracker
Python Programming Internship - Task 2

Features:
- Add stock positions (ticker, shares, buy price)
- Fetch real-time prices via yfinance
- Calculate per-holding and total portfolio gain/loss
- Log performance summary to portfolio_summary.csv
- Optional validation against S&P 500 constituents list
"""

import csv
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance is required. Install with: pip install yfinance")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONSTITUENTS_FILE = "constituents.csv"
SUMMARY_FILE = "portfolio_summary.csv"
POSITIONS_FILE = "portfolio_positions.csv"  # optional persistence of holdings


def load_valid_tickers(filename: str = CONSTITUENTS_FILE) -> set:
    """Load valid ticker symbols from the S&P 500 constituents CSV."""
    tickers = set()
    path = filename
    if not os.path.exists(path):
        # Try relative to this script or common locations
        candidates = [
            filename,
            os.path.join(os.path.dirname(__file__), filename),
            os.path.join("/home/workdir/attachments", filename),
            os.path.join("/home/workdir/artifacts", filename),
        ]
        for p in candidates:
            if os.path.exists(p):
                path = p
                break
        else:
            print(f"Warning: {filename} not found. Ticker validation disabled.")
            return set()

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get("Symbol", "").strip().upper()
                if symbol:
                    # Handle special cases like BRK.B -> BRK-B for yfinance
                    tickers.add(symbol)
    except Exception as e:
        print(f"Warning: Could not load constituents: {e}")
    return tickers


def normalize_ticker(ticker: str) -> str:
    """Convert common formats to yfinance-compatible tickers."""
    t = ticker.strip().upper()
    # BRK.B / BF.B style → BRK-B / BF-B
    if "." in t:
        t = t.replace(".", "-")
    return t


def get_current_price(ticker: str) -> Optional[float]:
    """Fetch the latest market price for a ticker using yfinance."""
    try:
        t = yf.Ticker(normalize_ticker(ticker))
        # Prefer regularMarketPrice / currentPrice, fall back to history
        info = t.info
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )
        if price is not None:
            return float(price)

        # Fallback: last close from history
        hist = t.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception as e:
        print(f"  Warning: Could not fetch price for {ticker}: {e}")
    return None


def load_positions(filename: str = POSITIONS_FILE) -> Dict[str, dict]:
    """Load previously saved positions from CSV (if exists)."""
    positions = {}
    if not os.path.exists(filename):
        return positions
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row["ticker"].upper()
                positions[ticker] = {
                    "shares": float(row["shares"]),
                    "buy_price": float(row["buy_price"]),
                }
    except Exception as e:
        print(f"Warning: Could not load positions: {e}")
    return positions


def save_positions(positions: Dict[str, dict], filename: str = POSITIONS_FILE):
    """Persist current positions to CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticker", "shares", "buy_price"])
        writer.writeheader()
        for ticker, data in positions.items():
            writer.writerow({
                "ticker": ticker,
                "shares": data["shares"],
                "buy_price": data["buy_price"],
            })


def calculate_portfolio(positions: Dict[str, dict]) -> List[dict]:
    """
    Fetch prices and compute performance metrics for every holding.
    Returns a list of result dictionaries.
    """
    results = []
    for ticker, data in positions.items():
        shares = data["shares"]
        buy_price = data["buy_price"]
        invested = shares * buy_price

        current_price = get_current_price(ticker)
        if current_price is None:
            results.append({
                "ticker": ticker,
                "shares": shares,
                "buy_price": buy_price,
                "current_price": None,
                "invested": invested,
                "current_value": None,
                "gain_loss": None,
                "gain_loss_pct": None,
                "status": "PRICE_UNAVAILABLE",
            })
            continue

        current_value = shares * current_price
        gain_loss = current_value - invested
        gain_loss_pct = (gain_loss / invested * 100) if invested else 0.0

        results.append({
            "ticker": ticker,
            "shares": shares,
            "buy_price": buy_price,
            "current_price": current_price,
            "invested": invested,
            "current_value": current_value,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
            "status": "OK",
        })
    return results


def print_portfolio_report(results: List[dict]):
    """Pretty-print the portfolio performance table."""
    print("\n" + "=" * 90)
    print(f"{'TICKER':<8} {'SHARES':>10} {'BUY $':>10} {'CURR $':>10} "
          f"{'INVESTED':>12} {'VALUE':>12} {'G/L $':>12} {'G/L %':>9}")
    print("-" * 90)

    total_invested = 0.0
    total_value = 0.0

    for r in results:
        if r["status"] != "OK":
            print(f"{r['ticker']:<8} {'N/A':>10} {'N/A':>10} {'N/A':>10} "
                  f"{r['invested']:>12.2f} {'N/A':>12} {'N/A':>12} {'N/A':>9}")
            total_invested += r["invested"]
            continue

        total_invested += r["invested"]
        total_value += r["current_value"]

        gl_sign = "+" if r["gain_loss"] >= 0 else ""
        print(
            f"{r['ticker']:<8} "
            f"{r['shares']:>10.2f} "
            f"{r['buy_price']:>10.2f} "
            f"{r['current_price']:>10.2f} "
            f"{r['invested']:>12.2f} "
            f"{r['current_value']:>12.2f} "
            f"{gl_sign}{r['gain_loss']:>11.2f} "
            f"{gl_sign}{r['gain_loss_pct']:>7.2f}%"
        )

    print("-" * 90)
    total_gl = total_value - total_invested
    total_gl_pct = (total_gl / total_invested * 100) if total_invested else 0.0
    gl_sign = "+" if total_gl >= 0 else ""

    print(f"{'TOTAL':<8} {'':<10} {'':<10} {'':<10} "
          f"{total_invested:>12.2f} {total_value:>12.2f} "
          f"{gl_sign}{total_gl:>11.2f} {gl_sign}{total_gl_pct:>7.2f}%")
    print("=" * 90)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def log_summary_to_csv(results: List[dict], filename: str = SUMMARY_FILE):
    """Append a performance snapshot to the summary CSV."""
    fieldnames = [
        "timestamp", "ticker", "shares", "buy_price", "current_price",
        "invested", "current_value", "gain_loss", "gain_loss_pct", "status"
    ]
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        ts = datetime.now().isoformat(timespec="seconds")
        for r in results:
            writer.writerow({
                "timestamp": ts,
                "ticker": r["ticker"],
                "shares": r["shares"],
                "buy_price": r["buy_price"],
                "current_price": r["current_price"] if r["current_price"] is not None else "",
                "invested": round(r["invested"], 2),
                "current_value": round(r["current_value"], 2) if r["current_value"] is not None else "",
                "gain_loss": round(r["gain_loss"], 2) if r["gain_loss"] is not None else "",
                "gain_loss_pct": round(r["gain_loss_pct"], 2) if r["gain_loss_pct"] is not None else "",
                "status": r["status"],
            })
    print(f"\n✓ Performance log saved to {filename}")


def add_position(positions: Dict[str, dict], valid_tickers: set):
    """Interactive prompt to add or update a position."""
    ticker = input("Enter ticker symbol (e.g. AAPL): ").strip().upper()
    if not ticker:
        print("Cancelled.")
        return

    norm = normalize_ticker(ticker)
    if valid_tickers and ticker not in valid_tickers and norm not in valid_tickers:
        confirm = input(f"  '{ticker}' not found in S&P 500 list. Add anyway? (y/n): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Cancelled.")
            return

    try:
        shares = float(input("Number of shares: ").strip())
        if shares <= 0:
            print("Shares must be positive.")
            return
        buy_price = float(input("Buy price per share ($): ").strip())
        if buy_price <= 0:
            print("Buy price must be positive.")
            return
    except ValueError:
        print("Invalid number. Please try again.")
        return

    # If already exists, ask whether to replace or add to shares
    if ticker in positions:
        print(f"  Existing position: {positions[ticker]['shares']} shares @ ${positions[ticker]['buy_price']:.2f}")
        action = input("  (r)eplace / (a)dd shares / (c)ancel? ").strip().lower()
        if action == "a":
            old = positions[ticker]
            total_shares = old["shares"] + shares
            # Weighted average buy price
            avg_price = (old["shares"] * old["buy_price"] + shares * buy_price) / total_shares
            positions[ticker] = {"shares": total_shares, "buy_price": avg_price}
            print(f"  Updated: {total_shares:.2f} shares @ avg ${avg_price:.2f}")
        elif action == "r":
            positions[ticker] = {"shares": shares, "buy_price": buy_price}
            print(f"  Replaced with {shares:.2f} shares @ ${buy_price:.2f}")
        else:
            print("Cancelled.")
            return
    else:
        positions[ticker] = {"shares": shares, "buy_price": buy_price}
        print(f"  Added {shares:.2f} shares of {ticker} @ ${buy_price:.2f}")


def remove_position(positions: Dict[str, dict]):
    """Remove a ticker from the portfolio."""
    if not positions:
        print("Portfolio is empty.")
        return
    print("Current holdings:", ", ".join(sorted(positions.keys())))
    ticker = input("Ticker to remove: ").strip().upper()
    if ticker in positions:
        del positions[ticker]
        print(f"Removed {ticker}.")
    else:
        print(f"{ticker} not found.")


def main():
    print("=" * 60)
    print("   STOCK PORTFOLIO PERFORMANCE TRACKER")
    print("=" * 60)

    valid_tickers = load_valid_tickers()
    if valid_tickers:
        print(f"Loaded {len(valid_tickers)} valid S&P 500 tickers for validation.")

    positions = load_positions()
    if positions:
        print(f"Loaded {len(positions)} existing position(s) from {POSITIONS_FILE}.")

    while True:
        print("\n--- Menu ---")
        print("1. Add / Update position")
        print("2. Remove position")
        print("3. View portfolio & calculate performance")
        print("4. Save positions")
        print("5. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            add_position(positions, valid_tickers)
        elif choice == "2":
            remove_position(positions)
        elif choice == "3":
            if not positions:
                print("Portfolio is empty. Add some positions first.")
                continue
            print("\nFetching live prices...")
            results = calculate_portfolio(positions)
            print_portfolio_report(results)
            log_summary_to_csv(results)
        elif choice == "4":
            save_positions(positions)
            print(f"Positions saved to {POSITIONS_FILE}")
        elif choice == "5":
            if positions:
                save = input("Save positions before exit? (y/n): ").strip().lower()
                if save in ("y", "yes"):
                    save_positions(positions)
                    print(f"Positions saved to {POSITIONS_FILE}")
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
