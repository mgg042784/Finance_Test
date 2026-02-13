import financedatabase as fd
import pandas as pd
import numpy as np

# Initialize the database
equities = fd.Equities()

# Get energy sector equities
filtered_equities = equities.select(sector='Energy')
print(f"Total Energy Sector Equities: {len(filtered_equities)}")

# Convert to DataFrame (NO TRANSPOSE - keep ticker symbols as index)
df = pd.DataFrame(filtered_equities)
print(f"DataFrame shape: {df.shape}")
print(f"Column names: {df.columns.tolist()}\n")

# ============================================
# Data Transformation Logic - WORKING VERSION
# ============================================

def get_top_energy_stocks(df, top_n=15, 
                         preferred_currencies=['USD', 'EUR', 'GBP']):
    """
    Filter and rank energy sector stocks by market cap and liquidity.
    
    Note: financedatabase provides company metrics (market_cap, currency, location)
    but not real-time trading data (price, volume). For complete analysis,
    combine with yfinance or other price data sources.
    
    Parameters:
    -----------
    df : DataFrame
        Energy sector equities data from financedatabase
    top_n : int
        Number of top stocks to return
    preferred_currencies : list
        Preferred currencies for trading liquidity
        
    Returns:
    --------
    DataFrame with top ranked energy stocks
    """
    
    results = df.copy()
    
    # STEP 1: Ensure we have energy sector data
    print(f"Step 1: Starting with {len(results)} energy stocks")
    
    # STEP 2: Filter by market cap category (when available)
    if 'market_cap' in results.columns:
        mask = results['market_cap'].notna()
        results = results.loc[mask].copy()
        print(f"Step 2: {len(results)} stocks have market cap category data")
        # Create numeric score from market cap categories
        cap_scores = {'Micro Cap': 1, 'Small Cap': 2, 'Mid Cap': 3, 'Large Cap': 4, 'Mega Cap': 5}
        results['market_cap_score'] = results['market_cap'].map(cap_scores).fillna(0)
    
    # STEP 3: Filter by preferred currencies (liquidity indicator)
    if 'currency' in results.columns:
        mask = results['currency'].isin(preferred_currencies)
        results = results.loc[mask].copy()
        print(f"Step 3: {len(results)} stocks in preferred currencies ({', '.join(preferred_currencies)})")
    
    # STEP 4: Create ranking scores
    results = results.copy()
    results['rank_score'] = 0.0
    
    # Market cap score (larger cap = more stable)
    if 'market_cap_score' in results.columns:
        results.loc[:, 'rank_score'] = results['rank_score'] + results['market_cap_score'].rank(pct=True) * 50
    
    # Currency bonus (USD preferred for liquidity)
    if 'currency' in results.columns:
        currency_bonus = results['currency'].apply(
            lambda x: 30 if x == 'USD' else (20 if x in ['EUR', 'GBP'] else 0)
        )
        results.loc[:, 'rank_score'] = results['rank_score'] + currency_bonus
    
    # Exchange bonus (major exchanges = better liquidity)
    major_exchanges = ['NASDAQ', 'NYSE', 'XETRA', 'NYQ', 'XETR', 'LON', 'Euronext']
    if 'exchange' in results.columns:
        exchange_bonus = results['exchange'].apply(
            lambda x: 20 if any(ex in str(x).upper() for ex in major_exchanges) else 0
        )
        results.loc[:, 'rank_score'] = results['rank_score'] + exchange_bonus
    
    # STEP 5: Sort by ranking score descending
    results = results.sort_values('rank_score', ascending=False)
    
    # STEP 6: Return top N with key fields
    select_cols = ['name', 'currency', 'exchange', 'market_cap', 'country', 'rank_score']
    available_select_cols = [col for col in select_cols if col in results.columns]
    top_results = results.head(top_n)[available_select_cols].copy()
    
    print(f"Step 5-6: Returning top {len(top_results)} energy stocks\n")
    
    return top_results


# ============================================
# EXECUTION - Get Results
# ============================================

print("="*80)
print("ENERGY SECTOR STOCK RANKING ANALYSIS")
print("="*80 + "\n")

top_energy_stocks = get_top_energy_stocks(df, top_n=15)

print("\n" + "="*80)
print("TOP 15 ENERGY STOCKS BY RANKING SCORE")
print("="*80 + "\n")

# Format the output nicely
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

print(top_energy_stocks.to_string())

print("\n" + "="*80)
print("RANKING FACTORS EXPLANATION")
print("="*80)
print("""
SCORING BREAKDOWN:
  1. Market Cap Score (0-50 pts): Larger market cap = more stable & liquid
     - Percentile-ranked against all energy stocks
     
  2. Currency Bonus (0-30 pts):
     - USD: 30 points (most liquid globally)
     - EUR/GBP: 20 points (strong secondary currencies)
     - Others: 0 points
     
  3. Exchange Bonus (20 pts):
     - Major global exchanges (NYSE, NASDAQ, XETRA, LON, Euronext)
     - Better liquidity and trading volume

TOTAL SCORE: Sum of all factors (max ~100 points)

DATA LIMITATIONS:
  - Company fundamentals: market cap, currency, location, exchange
  - Trading data NOT available: real-time price, volume, momentum indicators
  
HOW TO ENHANCE THIS ANALYSIS:
  1. Integrate yfinance for current prices:
     > import yfinance as yf
     > ticker_data = yf.download(ticker_symbol)
     
  2. Add technical indicators:
     > Calculate 20-day/200-day moving averages
     > RSI, MACD for momentum
     
  3. Calculate returns:
     > % price change over time periods
     > Volume trend analysis
     
  4. Create comprehensive ranking:
     > Combine fundamental scores with technical metrics
     > Weight by sector trends
""")

print("\n" + "="*80)
print("NEXT STEPS FOR USERS")
print("="*80)
print("""
Example: Fetch current price data for top stocks

import yfinance as yf
for ticker in top_energy_stocks.index[:5]:
    data = yf.download(ticker, progress=False)
    print(f"{ticker}: Current Price: {data['Close'][-1]}")
""")

