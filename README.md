# Polymarket Trading Bot - Python Edition

> Automated copy trading bot for Polymarket that mirrors trades from top performers with intelligent position sizing and real-time execution.


## Overview

This is the Python version of the Polymarket Copy Trading Bot. It automatically replicates trades from successful Polymarket traders to your wallet. It monitors trader activity 24/7, calculates proportional position sizes based on your capital, and executes matching orders in real-time.

### How It Works

1. **Select Traders** - Choose top performers from [Polymarket leaderboard](https://polymarket.com/leaderboard)
2. **Monitor Activity** - Bot continuously watches for new positions opened by selected traders using Polymarket Data API
3. **Calculate Size** - Automatically scales trades based on your balance vs. trader's balance
4. **Execute Orders** - Places matching orders on Polymarket using your wallet
5. **Track Performance** - Logs complete trade activity to console and daily log files

## Best Practice

https://github.com/user-attachments/assets/82f5404a-24b3-4e0e-8a8a-ef3264e4359f

<img width="1038" height="237" alt="image" src="https://github.com/user-attachments/assets/d2f8bd89-9f68-4299-af88-5e410b9b1652" />

<img width="894" height="668" alt="image" src="https://github.com/user-attachments/assets/c09b1691-835a-4419-8740-734d300074a5" />

I've decided to copy Vidarx's trades. Looking at his profit curve, it just keeps going up over the whole time period. He mostly trades on very short time frames like 15-minute or 5-minute charts — these markets are super volatile and move fast. His strategy is really unique, and at one point his trades completely beat (or outperformed) Gabagool's trading. But now Gabagool's style seems almost dead or not working anymore.

In short: by copying him in the BTC 5-minute market during one cycle (one trading period), we made $256 in profit.

## Quick Start

### Prerequisites

- Python 3.10+
- Polygon wallet with USDC and POL/MATIC for gas
- RPC endpoint ([Infura](https://infura.io) or [Alchemy](https://www.alchemy.com) free tier)

### Installation

```bash
# Clone repository
git clone https://github.com/gamma-trade-lab/polymarket-copy-trading-bot.git
cd polymarket-copy-trading-bot

# Install dependencies
pip install -r requirements.txt

# Run interactive setup wizard
python -m src.scripts.setup.setup

# Verify system status
python -m src.scripts.setup.system_status

# Start trading bot
python -m src.main
```


## Configuration

### Finding Traders

1. Visit [Polymarket Leaderboard](https://polymarket.com/leaderboard)
2. Look for traders with positive P&L, win rate >55%, and active trading history
3. Verify detailed stats on [Predictfolio](https://predictfolio.com)
4. Add wallet addresses to `USER_ADDRESSES` in `.env`

## Features

- **Multi-Trader Support** - Track and copy trades from multiple traders simultaneously
- **Smart Position Sizing** - Automatically adjusts trade sizes based on your capital
- **Tiered Multipliers** - Apply different multipliers based on trade size
- **Position Tracking** - Accurately tracks purchases and sells even after balance changes
- **Trade Aggregation** - Combines multiple small trades into larger executable orders
- **Real-time Execution** - Monitors trades every second and executes instantly
- **Log-Only Architecture** - No database required; trade flow is processed in-memory and logged
- **Price Protection** - Built-in slippage checks to avoid unfavorable fills
- **Colored Logging** - Beautiful colored console output for better monitoring

## Important Notes

### CLOB Client Implementation

The Polymarket CLOB (Central Limit Order Book) client is a critical component that requires full implementation. The current Python version includes a placeholder structure. For production use, you have two options:

**Implement full Python CLOB client**
   - This requires implementing Polymarket's order signing protocol
   - See the Polymarket documentation for API details
   - The structure is in `src/utils/create_clob_client.py`

## Safety & Risk Management

- **Use at your own risk** - This bot executes real trades with real money
- **Start small** - Test with minimal funds before scaling up
- **Diversify** - Don't copy just one trader; track multiple strategies
- **Monitor regularly** - Check bot logs daily to ensure proper execution
- **No guarantees** - Past performance doesn't guarantee future results

## Discover More Bots

To see more profitable bots for traders, visit https://github.com/gamma-trade-lab/



