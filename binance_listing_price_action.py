"""
Binance Futures New Listings - 1-Minute Analysis (English Version)
================================================================
- Direct connection to Binance API
- 1-minute candlestick data for 100 hours after listing
- Individual coin overlay + average lines + detailed statistics

Usage: python binance_listing_analysis_en.py
Output: listing_analysis_en.png, listing_data_en.csv, listing_report_en.txt
"""

import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import time
import os
import gc
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib to use English fonts
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# Configuration
# ============================================================
HOURS_TO_TRACK = 100          # Tracking period (hours)
MINUTES_TO_TRACK = HOURS_TO_TRACK * 60  # 6000 minutes
START_DATE = datetime(2023, 1, 1)
API_DELAY = 0.5               # API call interval (seconds)
BATCH_SIZE = 10               # Batch processing size
SAVE_INTERVAL = 50            # Intermediate save interval

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CHART = os.path.join(SCRIPT_DIR, "listing_analysis_en.png")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "listing_data_en.csv")
OUTPUT_REPORT = os.path.join(SCRIPT_DIR, "listing_report_en.txt")


# ============================================================
# Binance API Integration
# ============================================================
def get_exchange():
    """Create Binance Futures exchange object"""
    return ccxt.binanceusdm({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'recvWindow': 10000,
        },
        'timeout': 30000,
        'rateLimit': 100,
    })


def get_all_listings(exchange):
    """Get all coin listings since 2023"""
    print("📊 Collecting all Binance Futures listings...")
    
    try:
        exchange.load_markets()
        print(f"✅ Market info loaded: {len(exchange.markets)} markets")
    except Exception as e:
        print(f"❌ Failed to load market info: {e}")
        return []
    
    listings = []
    total_markets = len(exchange.markets)
    processed = 0
    
    for symbol, market in exchange.markets.items():
        processed += 1
        
        # Filter USDT futures only
        if market['quote'] != 'USDT' or not market['active'] or market['type'] != 'swap':
            continue
        
        # Check listing date
        onboard_date = market.get('info', {}).get('onboardDate')
        if not onboard_date:
            continue
        
        try:
            listing_ts = int(onboard_date)
            listing_dt = datetime.fromtimestamp(listing_ts / 1000)
            
            # Only coins listed after START_DATE
            if listing_dt >= START_DATE:
                listings.append({
                    'symbol': symbol,
                    'base': market['base'],
                    'listing_timestamp': listing_ts,
                    'listing_datetime': listing_dt
                })
        except (ValueError, TypeError):
            continue
        
        # Progress indicator
        if processed % 100 == 0:
            print(f"    Processing... {processed}/{total_markets} ({processed/total_markets*100:.1f}%)")
    
    # Sort by listing date (oldest first)
    listings.sort(key=lambda x: x['listing_timestamp'])
    
    print(f"✅ Coins listed since {START_DATE.strftime('%Y-%m-%d')}: {len(listings)}")
    
    # Yearly statistics
    year_stats = {}
    for listing in listings:
        year = listing['listing_datetime'].year
        year_stats[year] = year_stats.get(year, 0) + 1
    
    print(f"📅 Listings by year:")
    for year in sorted(year_stats.keys()):
        print(f"    {year}: {year_stats[year]} coins")
    
    return listings


def safe_fetch_ohlcv(exchange, symbol, since_ts, limit=MINUTES_TO_TRACK):
    """Safe 1-minute OHLCV data collection"""
    all_data = []
    current_ts = since_ts
    max_retries = 5
    
    # Limit API calls
    max_requests = min(limit // 800 + 2, 10)  # Max 10 requests
    request_count = 0
    
    while len(all_data) < limit and request_count < max_requests:
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Batch size adjustment (800 per request - safer)
                batch_limit = min(800, limit - len(all_data))
                
                ohlcv = exchange.fetch_ohlcv(
                    symbol, 
                    timeframe='1m', 
                    since=current_ts, 
                    limit=batch_limit
                )
                
                if not ohlcv:
                    return all_data
                
                all_data.extend(ohlcv)
                request_count += 1
                success = True
                
                # Update timestamp for next request
                if len(ohlcv) > 0:
                    current_ts = ohlcv[-1][0] + 60000
                
                # API rate limiting - sufficient wait
                time.sleep(API_DELAY)
                
                # Last batch if less data than requested
                if len(ohlcv) < batch_limit:
                    break
                
            except ccxt.NetworkError as e:
                retry_count += 1
                wait_time = min(retry_count * 3, 15)  # Max 15 seconds
                print(f"      Network error - waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except ccxt.RateLimitExceeded as e:
                retry_count += 1
                wait_time = min(retry_count * 10, 60)  # Max 60 seconds
                print(f"      Rate limit - waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except ccxt.BaseError as e:
                retry_count += 1
                wait_time = min(retry_count * 2, 10)
                print(f"      API error - waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"      Unexpected error: {str(e)[:50]}...")
                break
        
        if not success:
            print(f"      Max retries exceeded - returning partial data ({len(all_data)})")
            break
    
    return all_data[:limit]


def collect_all_data(exchange, listings):
    """Collect all coin data - optimized for large datasets"""
    all_data = []
    failed_coins = []
    
    total_coins = len(listings)
    print(f"\n🔄 Starting data collection for all coins...")
    print(f"   Target coins: {total_coins}")
    print(f"   Tracking period: {HOURS_TO_TRACK} hours")
    print(f"   Estimated time: {total_coins * 1.5} minutes")
    print("=" * 70)
    
    start_time = time.time()
    
    for i, listing in enumerate(listings):
        symbol = listing['symbol']
        listing_date = listing['listing_datetime'].strftime('%Y-%m-%d')
        progress = (i + 1) / total_coins * 100
        
        print(f"[{i+1:4d}/{total_coins}] {progress:5.1f}% | {symbol:20s} ({listing_date})", end="")
        
        try:
            # Data collection
            ohlcv = safe_fetch_ohlcv(exchange, symbol, listing['listing_timestamp'])
            
            if len(ohlcv) < 200:  # Minimum 200 minutes required
                print(f" ❌ Insufficient ({len(ohlcv)})")
                failed_coins.append({'symbol': symbol, 'reason': f'insufficient_data_{len(ohlcv)}'})
                continue
            
            # Efficient data processing
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Essential calculations only
            first_price = df.iloc[0]['open']
            final_price = df.iloc[-1]['close'] / first_price * 100
            max_price = (df['high'].max() / first_price * 100)
            min_price = (df['low'].min() / first_price * 100)
            
            # Save important time points in 15-minute intervals (memory efficiency)
            time_points = {}
            # Add Time=0 (100% by definition)
            time_points['0min'] = 100.0
            
            # 15-minute intervals up to 6 hours, then hourly
            time_intervals = [
                (15, 'min'), (30, 'min'), (45, 'min'),
                (1, 'h'), (1.25, 'h'), (1.5, 'h'), (1.75, 'h'), (2, 'h'),
                (3, 'h'), (4, 'h'), (6, 'h'), (12, 'h'), (24, 'h'), (48, 'h'), (72, 'h'), (100, 'h')
            ]
            
            for interval, unit in time_intervals:
                if unit == 'min':
                    idx = min(int(interval), len(df) - 1)
                    key = f'{int(interval)}min'
                else:
                    idx = min(int(interval * 60), len(df) - 1)
                    key = f'{interval}h' if interval != int(interval) else f'{int(interval)}h'
                
                if idx < len(df):
                    time_points[key] = df.iloc[idx]['close'] / first_price * 100
            
            coin_data = {
                'symbol': symbol,
                'base': listing['base'],
                'listing_date': listing['listing_datetime'],
                'first_price': first_price,
                'final_price': final_price,
                'max_price': max_price,
                'min_price': min_price,
                'volatility': df['close'].pct_change().std() * 100,
                'candles': len(df),
                'time_points': time_points
            }
            
            all_data.append(coin_data)
            print(f" ✅ {len(df):4d} | Final: {final_price:5.1f}%")
            
        except Exception as e:
            print(f" ❌ Error: {str(e)[:30]}...")
            failed_coins.append({'symbol': symbol, 'reason': str(e)[:50]})
            continue
        
        # Progress and time estimation
        if (i + 1) % BATCH_SIZE == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / (i + 1)
            remaining = avg_time * (total_coins - i - 1)
            success_rate = len(all_data) / (i + 1) * 100
            
            print(f"    📊 Success rate: {success_rate:.1f}% | Remaining: {remaining/60:.1f}min | Completed: {len(all_data)}")
        
        # Intermediate save
        if (i + 1) % SAVE_INTERVAL == 0 and all_data:
            temp_path = os.path.join(SCRIPT_DIR, f"temp_progress_{i+1}.csv")
            save_temp_csv(all_data, temp_path)
            print(f"    💾 Temp save: {len(all_data)} coins")
        
        # Memory cleanup
        if (i + 1) % 100 == 0:
            gc.collect()
    
    elapsed_total = time.time() - start_time
    success_rate = len(all_data) / total_coins * 100
    
    print(f"\n🎉 Data collection completed!")
    print(f"   Success: {len(all_data)} ({success_rate:.1f}%)")
    print(f"   Failed: {len(failed_coins)}")
    print(f"   Time taken: {elapsed_total/60:.1f} minutes")
    
    return all_data, failed_coins


# ============================================================
# Data Analysis and Visualization
# ============================================================
def save_temp_csv(all_data, output_path):
    """Save temporary progress"""
    if not all_data:
        return
    
    rows = []
    for coin in all_data:
        row = {
            'symbol': coin['symbol'],
            'listing_date': coin['listing_date'].strftime('%Y-%m-%d'),
            'final_price': coin['final_price'],
            'max_price': coin['max_price'],
            'min_price': coin['min_price'],
        }
        # Add key time points
        key_times = ['15min', '30min', '1h', '6h', '24h', '100h']
        for time_point in key_times:
            if time_point in coin.get('time_points', {}):
                row[f'price_{time_point}'] = coin['time_points'][time_point]
        
        rows.append(row)
    
    pd.DataFrame(rows).to_csv(output_path, index=False)


def create_comprehensive_analysis(all_data, output_chart):
    """Create comprehensive analysis charts"""
    if not all_data or len(all_data) < 10:
        print("❌ Insufficient data for analysis.")
        return None
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle(f'Binance Futures New Listings Analysis Since 2023 (n={len(all_data)})', 
                 fontsize=16, fontweight='bold')
    
    # 1. Final performance distribution
    ax1 = axes[0, 0]
    final_prices = [coin['final_price'] for coin in all_data]
    
    bins = np.arange(0, min(300, max(final_prices) + 10), 5)
    n, bins_hist, patches = ax1.hist(final_prices, bins=bins, alpha=0.7, edgecolor='black')
    
    for patch, bin_edge in zip(patches, bins_hist[:-1]):
        color = 'green' if bin_edge >= 100 else 'red'
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.axvline(x=100, color='black', linestyle='--', linewidth=2, label='Break-even (100%)')
    ax1.axvline(x=np.median(final_prices), color='blue', linestyle='-', linewidth=2,
               label=f'Median: {np.median(final_prices):.1f}%')
    
    ax1.set_title(f'Final Performance Distribution (after {HOURS_TO_TRACK}h)')
    ax1.set_xlabel('Price (Listing Price = 100%)')
    ax1.set_ylabel('Number of Coins')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Average performance over time (15-minute intervals)
    ax2 = axes[0, 1]
    
    # 15-minute interval time labels
    time_labels = ['0min', '15min', '30min', '45min', '1h', '1.25h', '1.5h', '1.75h', 
                   '2h', '3h', '4h', '6h', '12h', '24h', '48h', '72h', '100h']
    
    # Calculate overall average
    avg_prices = []
    for time_label in time_labels:
        prices = [coin['time_points'].get(time_label, 100) for coin in all_data 
                 if time_label in coin['time_points']]
        if prices:
            avg_prices.append(np.mean(prices))
        else:
            avg_prices.append(100)  # Default to 100% if no data
    
    # Calculate yearly averages
    year_data = {}
    for coin in all_data:
        year = coin['listing_date'].year
        if year not in year_data:
            year_data[year] = []
        year_data[year].append(coin)
    
    # Plot overall average
    x_positions = range(len(time_labels))
    ax2.plot(x_positions, avg_prices, 'bo-', linewidth=3, markersize=8, label=f'Overall Average (n={len(all_data)})')
    
    # Plot yearly averages
    colors = {'2023': 'green', '2024': 'orange', '2025': 'purple'}
    for year in sorted(year_data.keys()):
        year_coins = year_data[year]
        year_avg_prices = []
        
        for time_label in time_labels:
            year_prices = [coin['time_points'].get(time_label, 100) for coin in year_coins 
                          if time_label in coin['time_points']]
            if year_prices:
                year_avg_prices.append(np.mean(year_prices))
            else:
                year_avg_prices.append(100)
        
        color = colors.get(str(year), 'gray')
        ax2.plot(x_positions, year_avg_prices, '--', color=color, linewidth=2, 
                alpha=0.8, label=f'{year} Average (n={len(year_coins)})')
    
    ax2.axhline(y=100, color='black', linestyle='-', alpha=0.3, label='Break-even (100%)')
    ax2.set_title('Average Performance Over Time (15-min intervals)')
    ax2.set_xlabel('Time Since Listing')
    ax2.set_ylabel('Average Price (%)')
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(time_labels, rotation=45, ha='right')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(95, 110)  # Focus on the relevant range
    
    # 3. Performance by year
    ax3 = axes[0, 2]
    year_data = {}
    for coin in all_data:
        year = coin['listing_date'].year
        if year not in year_data:
            year_data[year] = []
        year_data[year].append(coin['final_price'])
    
    years = sorted(year_data.keys())
    year_avgs = [np.mean(year_data[year]) for year in years]
    year_counts = [len(year_data[year]) for year in years]
    
    bars = ax3.bar(years, year_avgs, alpha=0.7, 
                   color=['green' if avg >= 100 else 'red' for avg in year_avgs])
    
    # Show coin counts
    for i, (year, avg, count) in enumerate(zip(years, year_avgs, year_counts)):
        ax3.text(year, avg + 2, f'{count} coins', ha='center', va='bottom', fontsize=9)
    
    ax3.axhline(y=100, color='black', linestyle='--', alpha=0.5)
    ax3.set_title('Average Performance by Listing Year')
    ax3.set_xlabel('Listing Year')
    ax3.set_ylabel('Average Final Price (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Win rate analysis (15-minute intervals)
    ax4 = axes[1, 0]
    time_win_rates = []
    for time_label in time_labels:
        prices = [coin['time_points'].get(time_label, 100) for coin in all_data 
                 if time_label in coin['time_points']]
        if prices:
            win_rate = sum(1 for p in prices if p >= 100) / len(prices) * 100
        else:
            win_rate = 50  # Default if no data
        time_win_rates.append(win_rate)
    
    bars = ax4.bar(x_positions, time_win_rates, 
                   color=['green' if wr >= 50 else 'red' for wr in time_win_rates],
                   alpha=0.7)
    
    ax4.axhline(y=50, color='black', linestyle='--', alpha=0.5, label='50% line')
    ax4.set_title('Win Rate by Time Point (15-min intervals)')
    ax4.set_xlabel('Time Since Listing')
    ax4.set_ylabel('Win Rate (%)')
    ax4.set_xticks(x_positions)
    ax4.set_xticklabels(time_labels, rotation=45, ha='right')
    ax4.set_ylim(0, 100)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Show win rate values for key time points
    key_indices = [0, 4, 8, 12, 16]  # 0min, 1h, 2h, 12h, 100h
    for i in key_indices:
        if i < len(bars):
            bar = bars[i]
            wr = time_win_rates[i]
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{wr:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 5. Volatility distribution
    ax5 = axes[1, 1]
    volatilities = [coin.get('volatility', 0) for coin in all_data]
    
    ax5.hist(volatilities, bins=30, alpha=0.7, color='orange', edgecolor='black')
    ax5.axvline(x=np.median(volatilities), color='red', linestyle='--', 
               label=f'Median: {np.median(volatilities):.1f}%')
    ax5.set_title('Daily Volatility Distribution')
    ax5.set_xlabel('Daily Volatility (%)')
    ax5.set_ylabel('Number of Coins')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Summary statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    winners = sum(1 for coin in all_data if coin['final_price'] >= 100)
    win_rate = winners / len(all_data) * 100
    
    stats_text = f"📊 Analysis Summary\n"
    stats_text += "=" * 30 + "\n\n"
    stats_text += f"Analysis Period: 2023.01 ~\n"
    stats_text += f"Total Coins: {len(all_data)}\n\n"
    stats_text += f"🎯 Final Performance:\n"
    stats_text += f"  Win Rate: {win_rate:.1f}% ({winners}/{len(all_data)})\n"
    stats_text += f"  Average: {np.mean(final_prices):.1f}%\n"
    stats_text += f"  Median: {np.median(final_prices):.1f}%\n"
    stats_text += f"  Best: {max(final_prices):.1f}%\n"
    stats_text += f"  Worst: {min(final_prices):.1f}%\n\n"
    
    best_time_idx = np.argmax(time_win_rates)
    best_time = time_labels[best_time_idx]
    stats_text += f"💡 Optimal Sell Point:\n"
    stats_text += f"  {best_time} (Win Rate: {time_win_rates[best_time_idx]:.1f}%)\n\n"
    
    stats_text += f"📈 Yearly Breakdown:\n"
    for year in years:
        year_win_rate = sum(1 for p in year_data[year] if p >= 100) / len(year_data[year]) * 100
        stats_text += f"  {year}: {len(year_data[year])} coins (WR: {year_win_rate:.0f}%)\n"
    
    ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_chart, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Comprehensive chart saved: {output_chart}")
    
    return {
        'final_prices': final_prices,
        'time_win_rates': dict(zip(time_labels, time_win_rates)),
        'year_data': year_data,
        'best_time': best_time
    }


def save_complete_csv(all_data, output_path):
    """Save complete CSV data"""
    rows = []
    for coin in all_data:
        row = {
            'symbol': coin['symbol'],
            'base': coin['base'],
            'listing_date': coin['listing_date'].strftime('%Y-%m-%d %H:%M:%S'),
            'listing_year': coin['listing_date'].year,
            'listing_month': coin['listing_date'].month,
            'first_price': coin['first_price'],
            'final_price': coin['final_price'],
            'max_price': coin['max_price'],
            'min_price': coin['min_price'],
            'volatility': coin.get('volatility', 0),
            'candles_count': coin['candles'],
        }
        
        # Add time point prices (15-minute intervals)
        for time_point, price in coin['time_points'].items():
            row[f'price_{time_point}'] = price
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df = df.sort_values(['listing_date'], ascending=True)
    df.to_csv(output_path, index=False)
    
    print(f"📊 Complete CSV saved: {output_path}")
    print(f"   Total {len(df)} coin records")


def generate_final_report(all_data, analysis_stats, failed_coins, output_path):
    """Generate final analysis report"""
    report = []
    
    report.append("=" * 70)
    report.append("📊 BINANCE FUTURES - ALL LISTINGS ANALYSIS SINCE 2023")
    report.append("=" * 70)
    report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Analysis Target: All coins listed since 2023-01-01")
    report.append(f"Successfully analyzed: {len(all_data)} coins")
    report.append(f"Failed: {len(failed_coins)} coins")
    
    # Overall statistics
    final_prices = analysis_stats['final_prices']
    winners = sum(1 for p in final_prices if p >= 100)
    
    report.append(f"\n🎯 Overall Performance Summary:")
    report.append(f"  Total Win Rate: {winners/len(final_prices)*100:.1f}% ({winners}/{len(final_prices)})")
    report.append(f"  Average Return: {np.mean(final_prices):.1f}%")
    report.append(f"  Median Return: {np.median(final_prices):.1f}%")
    report.append(f"  Standard Deviation: {np.std(final_prices):.1f}%")
    report.append(f"  Best Performance: {max(final_prices):.1f}%")
    report.append(f"  Worst Performance: {min(final_prices):.1f}%")
    
    # Time-based win rates (key intervals only)
    report.append(f"\n⏰ Win Rate by Key Time Points:")
    key_times = ['0min', '15min', '30min', '1h', '2h', '3h', '6h', '12h', '24h', '48h', '72h', '100h']
    for time_point in key_times:
        if time_point in analysis_stats['time_win_rates']:
            win_rate = analysis_stats['time_win_rates'][time_point]
            report.append(f"  {time_point:>6s}: {win_rate:>5.1f}%")
    
    # Yearly analysis
    report.append(f"\n📅 Performance by Year:")
    year_data = analysis_stats['year_data']
    for year in sorted(year_data.keys()):
        year_prices = year_data[year]
        year_winners = sum(1 for p in year_prices if p >= 100)
        year_win_rate = year_winners / len(year_prices) * 100
        report.append(f"  {year}: {len(year_prices):3d} coins | Win Rate: {year_win_rate:5.1f}% | Avg: {np.mean(year_prices):5.1f}%")
    
    # Top/Bottom performers
    sorted_data = sorted(all_data, key=lambda x: x['final_price'], reverse=True)
    
    report.append(f"\n🏆 Top 20 Performers:")
    for i, coin in enumerate(sorted_data[:20], 1):
        listing_date = coin['listing_date'].strftime('%Y-%m')
        report.append(f"  {i:2d}. {coin['symbol']:15s}: {coin['final_price']:6.1f}% ({listing_date})")
    
    report.append(f"\n💥 Bottom 20 Performers:")
    for i, coin in enumerate(sorted_data[-20:], 1):
        listing_date = coin['listing_date'].strftime('%Y-%m')
        report.append(f"  {i:2d}. {coin['symbol']:15s}: {coin['final_price']:6.1f}% ({listing_date})")
    
    # Strategy recommendations
    best_time = analysis_stats['best_time']
    best_win_rate = analysis_stats['time_win_rates'][best_time]
    
    report.append(f"\n💡 Investment Strategy Recommendations:")
    report.append(f"  Optimal Sell Point: {best_time} after listing (Win Rate: {best_win_rate:.1f}%)")
    
    if np.mean(final_prices) > 110:
        report.append(f"  Strategy Grade: 🟢 AGGRESSIVE (Excellent average returns)")
    elif np.mean(final_prices) > 95:
        report.append(f"  Strategy Grade: 🟡 CONSERVATIVE (Moderate average returns)")
    else:
        report.append(f"  Strategy Grade: 🔴 CAUTIOUS (High risk of losses)")
    
    # Risk management
    below_90 = sum(1 for p in final_prices if p < 90) / len(final_prices) * 100
    report.append(f"\n⚠️  Risk Management:")
    report.append(f"  Probability of >10% loss: {below_90:.1f}%")
    report.append(f"  Recommended stop-loss: 90% (-10% loss)")
    
    if np.std(final_prices) > 100:
        report.append(f"  Warning: High volatility (Std Dev: {np.std(final_prices):.1f}%)")
    
    report.append("\n" + "=" * 70)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"📋 Final report saved: {output_path}")
    
    # Console summary
    print("\n" + "="*70)
    print("🎉 Complete analysis finished!")
    print("="*70)
    print(f"Analyzed coins: {len(all_data)}")
    print(f"Overall win rate: {winners/len(final_prices)*100:.1f}%")
    print(f"Average return: {np.mean(final_prices):.1f}%")
    print(f"Optimal sell point: {best_time}")
    print("="*70)


# ============================================================
# Main Execution
# ============================================================
def main():
    print("=" * 70)
    print("📊 Binance Futures Complete Listings Analysis (Since 2023)")
    print("=" * 70)
    print(f"Analysis period: All coins since {START_DATE.strftime('%Y-%m-%d')}")
    print(f"Tracking time: {HOURS_TO_TRACK} hours after listing")
    print(f"Data: 1-minute candlesticks")
    print("=" * 70)
    
    # Connect to Binance
    try:
        exchange = get_exchange()
        print("✅ Binance API connection successful")
    except Exception as e:
        print(f"❌ Binance API connection failed: {e}")
        return
    
    # Get all listings
    all_listings = get_all_listings(exchange)
    if not all_listings:
        print("❌ Could not retrieve listings.")
        return
    
    # Collect all data
    all_data, failed_coins = collect_all_data(exchange, all_listings)
    
    if len(all_data) < 10:
        print("❌ Insufficient data for analysis.")
        return
    
    # Comprehensive analysis
    print(f"\n📊 Analyzing {len(all_data)} coins...")
    analysis_stats = create_comprehensive_analysis(all_data, OUTPUT_CHART)
    
    # Save data
    save_complete_csv(all_data, OUTPUT_CSV)
    generate_final_report(all_data, analysis_stats, failed_coins, OUTPUT_REPORT)
    
    # Clean up temp files
    temp_files = [f for f in os.listdir(SCRIPT_DIR) if f.startswith('temp_')]
    for temp_file in temp_files:
        try:
            os.remove(os.path.join(SCRIPT_DIR, temp_file))
        except:
            pass
    
    print(f"\n🎉 All analysis completed!")
    print(f"📊 Chart: {OUTPUT_CHART}")
    print(f"📄 Data: {OUTPUT_CSV}")
    print(f"📋 Report: {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()