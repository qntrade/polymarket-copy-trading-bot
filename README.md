# Polymarket Copy Trading Bot - Python Edition

> Automated copy trading bot for Polymarket that mirrors trades from top performers with intelligent position sizing and real-time execution.


## Overview

This is the Python version of the Polymarket Copy Trading Bot. It automatically replicates trades from successful Polymarket traders to your wallet. It monitors trader activity 24/7, calculates proportional position sizes based on your capital, and executes matching orders in real-time.

### How It Works

1. **Select Traders** - Choose top performers from [Polymarket leaderboard](https://polymarket.com/leaderboard)
2. **Monitor Activity** - Bot continuously watches for new positions opened by selected traders using Polymarket Data API
3. **Calculate Size** - Automatically scales trades based on your balance vs. trader's balance
4. **Execute Orders** - Places matching orders on Polymarket using your wallet
5. **Track Performance** - Logs complete trade activity to console and daily log files

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

📖 **For detailed setup instructions, see [Getting Started Guide](docs/GETTING_STARTED.md)**

## Available Commands

### Setup & Configuration
```bash
python -m src.scripts.setup.setup              # Interactive setup wizard
python -m src.scripts.setup.system_status       # Verify system status and configuration
python -m src.scripts.setup.help              # Display all available commands
```

### Main Bot
```bash
python -m src.main                       # Start the copy trading bot
```

### Wallet Management
```bash
python -m src.scripts.wallet.check_proxy_wallet        # Check proxy and main wallet activity
python -m src.scripts.wallet.check_both_wallets        # Compare two wallet addresses
python -m src.scripts.wallet.check_my_stats            # View wallet statistics
python -m src.scripts.wallet.check_recent_activity     # Check recent trading activity
python -m src.scripts.wallet.check_positions_detailed  # View detailed position information
python -m src.scripts.wallet.check_pnl_discrepancy     # Check P&L discrepancy analysis
python -m src.scripts.wallet.verify_allowance         # Verify USDC token allowance
python -m src.scripts.wallet.check_allowance          # Check and set USDC allowance
python -m src.scripts.wallet.set_token_allowance      # Set ERC1155 token allowance
python -m src.scripts.wallet.find_my_eoa              # Find and analyze EOA wallet
python -m src.scripts.wallet.find_gnosis_safe_proxy   # Find Gnosis Safe proxy wallet
```

### Position Management (⚠️ Requires CLOB Client Implementation)
```bash
# Note: These scripts exist but require full CLOB client implementation
python -m src.scripts.position.manual_sell            # Manually sell a specific position
python -m src.scripts.position.sell_large_positions   # Sell large positions
python -m src.scripts.position.close_stale_positions # Close stale/old positions
python -m src.scripts.position.close_resolved_positions # Close resolved positions
python -m src.scripts.position.redeem_resolved_positions # Redeem resolved positions
```

### Trader Research & Analysis
```bash
python -m src.scripts.research.find_best_traders      # Find best performing traders
python -m src.scripts.research.find_low_risk_traders  # Find low-risk traders with good metrics
python -m src.scripts.research.scan_best_traders      # Scan and analyze top traders
python -m src.scripts.research.scan_traders_from_markets # Scan traders from active markets
```

### Simulation & Backtesting
```bash
python -m src.scripts.simulation.simulate_profitability # Simulate profitability for a trader
python -m src.scripts.simulation.simulate_profitability_old # Old simulation logic
python -m src.scripts.simulation.run_simulations        # Run comprehensive batch simulations
python -m src.scripts.simulation.compare_results        # Compare simulation results
python -m src.scripts.simulation.aggregate_results      # Aggregate trading results across strategies
python -m src.scripts.simulation.audit_copy_trading     # Audit copy trading algorithm
python -m src.scripts.simulation.fetch_historical_trades # Fetch and cache historical trade data
```

## Configuration

### Essential Variables

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `USER_ADDRESSES` | Traders to copy (comma-separated) | `'0xABC..., 0xDEF...'` |
| `PROXY_WALLET` | Your Polygon wallet address | `'0x123...'` |
| `PRIVATE_KEY` | Wallet private key (no 0x prefix) | `'abc123...'` |
| `RPC_URL` | Polygon RPC endpoint | `'https://polygon...'` |
| `USDC_CONTRACT_ADDRESS` | USDC contract on Polygon | `'0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'` |
| `CLOB_HTTP_URL` | Polymarket CLOB API URL | `'https://clob.polymarket.com'` |
| `TRADE_MULTIPLIER` | Position size multiplier (default: 1.0) | `2.0` |
| `FETCH_INTERVAL` | Check interval in seconds (default: 1) | `1` |
| `TRADE_AGGREGATION_ENABLED` | Enable trade aggregation (default: false) | `true` |
| `TRADE_AGGREGATION_WINDOW_SECONDS` | Aggregation window (default: 30) | `30` |

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

## Key Differences from TypeScript Version

- **Async/Await**: Python uses `asyncio` for async operations
- **Type System**: Python uses type hints instead of TypeScript types
- **Web3**: Uses `web3.py` instead of `ethers.js`
- **HTTP Client**: Uses `httpx` instead of `axios`
- **Logging**: Uses `colorama` for colored output
- **Package Management**: Uses `pip` and `requirements.txt` instead of `npm` and `package.json`

## Important Notes

### CLOB Client Implementation

The Polymarket CLOB (Central Limit Order Book) client is a critical component that requires full implementation. The current Python version includes a placeholder structure. For production use, you have two options:

**Implement full Python CLOB client**
   - This requires implementing Polymarket's order signing protocol
   - See the Polymarket documentation for API details
   - The structure is in `src/utils/create_clob_client.py`

## Safety & Risk Management

⚠️ **Important Disclaimers:**

- **Use at your own risk** - This bot executes real trades with real money
- **Start small** - Test with minimal funds before scaling up
- **Diversify** - Don't copy just one trader; track multiple strategies
- **Monitor regularly** - Check bot logs daily to ensure proper execution
- **No guarantees** - Past performance doesn't guarantee future results

### Best Practices

1. Use a dedicated wallet separate from your main funds
2. Only allocate capital you can afford to lose
3. Research traders thoroughly before copying
4. Set up monitoring and alerts
5. Know how to stop the bot quickly (Ctrl+C)
6. Run system status check before starting: `python -m src.scripts.setup.system_status`

## Troubleshooting

### Common Issues

**Missing environment variables** → Run `python -m src.scripts.setup.setup` to create `.env` file

**Bot not detecting trades** → Verify trader addresses and check recent activity

**Insufficient balance** → Add USDC to wallet and ensure POL/MATIC for gas fees

**CLOB client errors** → The CLOB client needs full implementation (see Important Notes above)

**Import errors** → Make sure you're running from the project root directory

**Run system status check:** `python -m src.scripts.setup.system_status`


## License

ISC License - See [LICENSE](LICENSE) file for details.

