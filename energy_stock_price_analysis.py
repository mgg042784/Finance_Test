import financedatabase as fd
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("ENERGY SECTOR STOCKS - DETAILED PRICE AND PERFORMANCE ANALYSIS")
print("="*100 + "\n")

# ============================================
# STEP 1: Get Top 15 Energy Stocks
# ============================================

print("PHASE 1: Retrieving Top 15 Energy Stocks by Market Cap & Liquidity\n")

equities = fd.Equities()
filtered_equities = equities.select(sector='Energy')
df = pd.DataFrame(filtered_equities)

def get_top_energy_stocks(df, top_n=15, preferred_currencies=['USD', 'EUR', 'GBP']):
    """Filter and rank energy sector stocks"""
    results = df.copy()
    
    # Filter by market cap
    if 'market_cap' in results.columns:
        mask = results['market_cap'].notna()
        results = results.loc[mask].copy()
        cap_scores = {'Micro Cap': 1, 'Small Cap': 2, 'Mid Cap': 3, 'Large Cap': 4, 'Mega Cap': 5}
        results['market_cap_score'] = results['market_cap'].map(cap_scores).fillna(0)
    
    # Filter by currency
    if 'currency' in results.columns:
        mask = results['currency'].isin(preferred_currencies)
        results = results.loc[mask].copy()
    
    # Create ranking scores
    results = results.copy()
    results['rank_score'] = 0.0
    
    if 'market_cap_score' in results.columns:
        results.loc[:, 'rank_score'] = results['rank_score'] + results['market_cap_score'].rank(pct=True) * 50
    
    if 'currency' in results.columns:
        currency_bonus = results['currency'].apply(
            lambda x: 30 if x == 'USD' else (20 if x in ['EUR', 'GBP'] else 0)
        )
        results.loc[:, 'rank_score'] = results['rank_score'] + currency_bonus
    
    major_exchanges = ['NASDAQ', 'NYSE', 'XETRA', 'NYQ', 'XETR', 'LON', 'Euronext']
    if 'exchange' in results.columns:
        exchange_bonus = results['exchange'].apply(
            lambda x: 20 if any(ex in str(x).upper() for ex in major_exchanges) else 0
        )
        results.loc[:, 'rank_score'] = results['rank_score'] + exchange_bonus
    
    results = results.sort_values('rank_score', ascending=False)
    
    select_cols = ['name', 'currency', 'exchange', 'market_cap', 'country', 'rank_score']
    available_select_cols = [col for col in select_cols if col in results.columns]
    top_results = results.head(top_n)[available_select_cols].copy()
    
    return top_results

top_energy_stocks = get_top_energy_stocks(df, top_n=15)
print(f"Retrieved {len(top_energy_stocks)} top energy stocks\n")

# ============================================
# STEP 2: Fetch Current Price Data
# ============================================

print("="*100)
print("PHASE 2: Fetching Current Price Data from Yahoo Finance")
print("="*100 + "\n")

price_data_list = []
failed_tickers = []

for idx, ticker in enumerate(top_energy_stocks.index, 1):
    try:
        print(f"[{idx}/15] Downloading data for {ticker}...", end=" ")
        
        # Download historical data (1 year for better analysis)
        stock_data = yf.download(ticker, period='1y', progress=False)
        
        if stock_data.empty:
            print("FAILED - No data")
            failed_tickers.append(ticker)
            continue
        
        # Get current price (last closing price)
        current_price = stock_data['Close'].iloc[-1]
        
        # Get 52-week high and low
        high_52w = stock_data['Close'].max()
        low_52w = stock_data['Close'].min()
        
        # Calculate price change (from 1 year ago)
        price_1y_ago = stock_data['Close'].iloc[0]
        price_change_1y = ((current_price - price_1y_ago) / price_1y_ago) * 100
        
        # Get average volume
        avg_volume = stock_data['Volume'].mean()
        
        # Get latest volume
        latest_volume = stock_data['Volume'].iloc[-1]
        
        # Calculate distance from 52-week high (% below high)
        distance_from_high = ((high_52w - current_price) / high_52w) * 100
        
        # Calculate distance from 52-week low (% above low)
        distance_from_low = ((current_price - low_52w) / low_52w) * 100
        
        # Get company info
        stock_info = yf.Ticker(ticker)
        pe_ratio = stock_info.info.get('trailingPE', 'N/A')
        market_cap = stock_info.info.get('marketCap', 'N/A')
        div_yield = stock_info.info.get('dividendYield', 'N/A')
        
        price_data_list.append({
            'Ticker': ticker,
            'Company': top_energy_stocks.loc[ticker, 'name'],
            'Current Price': f"${current_price:.2f}",
            'Price 1Y Ago': f"${price_1y_ago:.2f}",
            '1Y Change %': f"{price_change_1y:.2f}%",
            '52W High': f"${high_52w:.2f}",
            '52W Low': f"${low_52w:.2f}",
            'Distance from High %': f"{distance_from_high:.2f}%",
            'Distance from Low %': f"{distance_from_low:.2f}%",
            'Avg Volume': f"{int(avg_volume):,}",
            'Latest Volume': f"{int(latest_volume):,}",
            'P/E Ratio': pe_ratio if isinstance(pe_ratio, str) else f"{pe_ratio:.2f}",
            'Div Yield %': div_yield if isinstance(div_yield, str) else f"{div_yield*100:.2f}%"
        })
        
        print("OK")
        
    except Exception as e:
        print(f"ERROR - {str(e)}")
        failed_tickers.append(ticker)
        continue

# ============================================
# STEP 3: Display Results
# ============================================

print("\n" + "="*100)
print("PHASE 3: CURRENT PRICE AND PERFORMANCE DATA")
print("="*100 + "\n")

if price_data_list:
    price_df = pd.DataFrame(price_data_list)
    
    # Display full table
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    print(price_df.to_string(index=False))
    
    print("\n" + "="*100)
    print("KEY METRICS EXPLANATION")
    print("="*100)
    print("""
PRICE METRICS:
  • Current Price: Most recent closing price from Yahoo Finance
  • 1Y Change %: Percentage price change over the past 12 months
  • 52W High/Low: Highest and lowest prices in the last 52 weeks
  • Distance from High %: How far below 52-week high (lower = rebounding potential)
  • Distance from Low %: How far above 52-week low (higher = out of bottom)

VOLUME METRICS:
  • Avg Volume: Average daily trading volume over 1 year (liquidity indicator)
  • Latest Volume: Most recent day's trading volume

VALUATION METRICS:
  • P/E Ratio: Price-to-Earnings (lower can mean undervalued)
  • Div Yield %: Annual dividend yield (higher for income investors)

MOMENTUM SIGNALS:
  ✓ Positive 1Y Change % = Strong uptrend
  ✓ Low "Distance from High %" = Stock near highs (momentum strength)
  ✓ High "Distance from Low %" = Recovery from lows
  ✓ High Average Volume = Good liquidity for trading
""")

    print("\n" + "="*100)
    print("TOP 5 PERFORMERS (By 1-Year Gain)")
    print("="*100 + "\n")
    
    # Extract numeric values for sorting
    price_df_sorted = price_df.copy()
    price_df_sorted['1Y_Change_Numeric'] = price_df_sorted['1Y Change %'].str.replace('%', '').astype(float)
    top_performers = price_df_sorted.nlargest(5, '1Y_Change_Numeric')[['Ticker', 'Company', 'Current Price', '1Y Change %']]
    print(top_performers.to_string(index=False))

if failed_tickers:
    print("\n" + "="*100)
    print(f"WARNING: Failed to retrieve data for {len(failed_tickers)} ticker(s)")
    print("="*100)
    print(f"Failed tickers: {', '.join(failed_tickers)}")
    print("(These may be delisted, suspended, or have ticker symbol differences)\n")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)
print("""
NEXT STEPS:

1. TECHNICAL ANALYSIS:
   - Plot price trends and moving averages
   - Identify support/resistance levels
   - Calculate RSI, MACD, Bollinger Bands

2. FUNDAMENTAL ANALYSIS:
   - Compare P/E ratios within energy sector
   - Analyze dividend yields
   - Review quarterly earnings

3. RISK ASSESSMENT:
   - Check volatility (standard deviation)
   - Analyze earnings surprises
   - Monitor geopolitical events

4. PORTFOLIO CONSTRUCTION:
   - Combine momentum and value stocks
   - Balance high/low volatility positions
   - Consider sector rotation timing
""")
