# Step-by-Step Guide: How to Run the Polymarket Copy Trading Bot

## Prerequisites Checklist

Before starting, make sure you have:

- ✅ **Python 3.10 or higher** installed
- ✅ **Polygon wallet** with USDC and MATIC/POL for gas
- ✅ **RPC endpoint** (free tier from Alchemy or Infura works)
- ✅ **Trader addresses** to copy (from Polymarket leaderboard)

---

## Step 1: Install Python Dependencies

Open PowerShell or Command Prompt in the project directory and run:

```powershell
# Install all required packages
pip install -r requirements.txt
```

**Expected output:** All packages should install successfully without errors.

**Troubleshooting:**
- If you get "pip is not recognized", install Python from [python.org](https://www.python.org/downloads/)
- If you get permission errors, try: `pip install --user -r requirements.txt`

---

## Step 2: Get Polygon RPC Endpoint

### Option A: Alchemy (Recommended)

1. Go to [Alchemy](https://www.alchemy.com)
2. Create a free account
3. Create a new app:
   - Click "Create App"
   - Name: "Polymarket Bot"
   - Chain: **Polygon**
   - Network: **Polygon Mainnet**
4. Copy your HTTP URL:
   - Example: `https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY`

### Option B: Infura (Free)

1. Go to [Infura](https://infura.io)
2. Create a free account
3. Create a new project
4. Select "Polygon" network
5. Copy your endpoint:
   - Example: `https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID`

---

## Step 3: Prepare Your Wallet

1. **Create or use existing Polygon wallet** (MetaMask, Trust Wallet, etc.)
2. **Export your private key:**
   - In MetaMask: Account → Account Details → Export Private Key
   - ⚠️ **NEVER share your private key!**
3. **Fund your wallet:**
   - Add **USDC** (start with $10-50 for testing)
   - Add **MATIC/POL** for gas fees (1-2 MATIC recommended)
4. **Get your wallet address:**
   - Copy your wallet address (starts with `0x...`)

---

## Step 4: Find Traders to Copy

### Method 1: Polymarket Leaderboard

1. Visit [Polymarket Leaderboard](https://polymarket.com/leaderboard)
2. Look for traders with:
   - Positive P&L
   - Win rate > 55%
   - Active trading history
3. Click on a trader → Copy their wallet address (`0x...`)

### Method 2: Use Bot's Research Tools

```powershell
# Find best performing traders
python -m src.scripts.research.find_best_traders

# Find low-risk traders
python -m src.scripts.research.find_low_risk_traders
```

---

## Step 5: Run the Setup Wizard

The interactive setup wizard will guide you through creating your `.env` file:

```powershell
python -m src.scripts.setup.setup
```

**The wizard will ask for:**

1. **RPC URL** - Paste your Polygon RPC endpoint
2. **Wallet Address** - Your Polygon wallet address (`0x...`)
3. **Private Key** - Your wallet's private key (without `0x` prefix)
4. **USDC Contract Address** - Press Enter for default: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
5. **CLOB HTTP URL** - Press Enter for default: `https://clob.polymarket.com`
6. **CLOB WS URL** - Press Enter for default: `wss://ws-subscriptions-clob.polymarket.com/ws`
7. **Trader Addresses** - Paste trader addresses (comma-separated)
   - Example: `0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b,0x6bab41a0dc40d6dd4c1a915b8c01969479fd1292`
8. **Trade Multiplier** - Press Enter for default `1.0` (same size as trader)
9. **Fetch Interval** - Press Enter for default `1` second
10. **Trade Aggregation** - Press Enter for default `false`

**After completion:** A `.env` file will be created in the project root.

---

## Step 6: Verify System Status

Before running the bot, verify everything is configured correctly:

```powershell
python -m src.scripts.setup.system_status
```

**This checks:**
- ✅ RPC endpoint connectivity
- ✅ Wallet balance (USDC and MATIC)
- ✅ CLOB API accessibility
- ✅ Trader addresses validity

**Fix any errors before proceeding!**

---

## Step 7: Check Wallet Balance & Allowance

### Check Your Wallet Balance

```powershell
# View wallet statistics
python -m src.scripts.wallet.check_my_stats

# Check USDC balance specifically
python -m src.scripts.wallet.check_proxy_wallet
```

**Ensure you have:**
- At least 10-50 USDC for testing
- 1-2 MATIC for gas fees

### Set USDC Allowance

The bot needs permission to spend your USDC:

```powershell
# Check and set allowance
python -m src.scripts.wallet.check_allowance
```

Follow the prompts to approve USDC spending.

---

## Step 8: Start the Bot

Once everything is configured, start the bot:

```powershell
python -m src.main
```

**Expected output:**
```
[INFO] First time running the bot?
  Read the guide: GETTING_STARTED.md
  Run system status check: python -m src.scripts.setup.system_status

[INFO] Performing initial system status check...
[SUCCESS] RPC endpoint accessible
[SUCCESS] Wallet balance: 50.0 USDC, 1.5 MATIC
[INFO] Initializing CLOB client...
[SUCCESS] CLOB client ready
[INFO] Starting trade monitor...
[INFO] Starting trade executor...
[INFO] Monitoring traders: 0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b...
[SUCCESS] Bot is running and ready to copy trades!
```

**The bot will:**
- Monitor trader activity every second
- Detect new positions opened by tracked traders
- Calculate position size based on your balance
- Execute matching orders automatically
- Log all activity to console and `logs/` directory

---

## Step 9: Monitor the Bot

### View Recent Activity

```powershell
# Check recent trades
python -m src.scripts.wallet.check_recent_activity

# View detailed positions
python -m src.scripts.wallet.check_positions_detailed

# Check P&L
python -m src.scripts.wallet.check_pnl_discrepancy
```

### View Logs

Logs are saved in the `logs/` directory:

```powershell
# View today's log (PowerShell)
Get-Content logs\bot-$(Get-Date -Format "yyyy-MM-dd").log

# Or open the log file directly
notepad logs\bot-2026-01-21.log
```

---

## Stopping the Bot

To stop the bot gracefully:

1. Press **Ctrl+C** in the terminal
2. The bot will:
   - Finish current operations
   - Stop services cleanly
   - Save state
   - Exit cleanly

**⚠️ Don't force close** - let it shut down gracefully!

---

## Common Issues & Solutions

### Issue 1: "Missing required environment variables"

**Solution:**
```powershell
# Run setup wizard again
python -m src.scripts.setup.setup
```

### Issue 3: "RPC endpoint not responding"
`
**Solution:**
- Verify `RPC_URL` in `.env` file
- Check API key is valid
- Try a different RPC endpoint

### Issue 4: "Insufficient USDC balance"

**Solution:**
- Add USDC to your wallet
- Check balance: `python -m src.scripts.wallet.check_my_stats`
- Ensure you have MATIC for gas fees

### Issue 5: "Bot not detecting trades"

**Solution:**
- Verify trader addresses are correct in `.env`
- Check traders are actively trading
- Verify `USER_ADDRESSES` format (comma-separated)
- Check recent activity: `python -m src.scripts.wallet.check_recent_activity`

### Issue 6: "ModuleNotFoundError: No module named 'src'"

**Solution:**
- Make sure you're in the project root directory
- Run commands from: `D:\05working\polymarket-bot\update(1.22)`
- Activate virtual environment if using one

---

## Quick Reference Commands

### Setup & Configuration
```powershell
python -m src.scripts.setup.setup              # Interactive setup wizard
python -m src.scripts.setup.system_status       # Verify system status
python -m src.scripts.setup.help              # Display all commands
```

### Main Bot
```powershell
python -m src.main                             # Start the copy trading bot
```

### Wallet Management
```powershell
python -m src.scripts.wallet.check_my_stats            # View wallet statistics
python -m src.scripts.wallet.check_proxy_wallet         # Check wallet balance
python -m src.scripts.wallet.check_allowance            # Check/set USDC allowance
python -m src.scripts.wallet.check_recent_activity      # Check recent trades
```

### Trader Research
```powershell
python -m src.scripts.research.find_best_traders        # Find best traders
python -m src.scripts.research.find_low_risk_traders    # Find low-risk traders
```

---

## Important Reminders

⚠️ **Safety First:**
- Start with small amounts ($10-50) for testing
- Only trade what you can afford to lose
- Monitor the bot regularly
- Keep your private key secure (never share it!)
- Research traders before copying them

📊 **Best Practices:**
- Use a dedicated wallet separate from your main funds
- Diversify by copying multiple traders
- Check bot logs daily
- Run system status check before starting: `python -m src.scripts.setup.system_status`
- Know how to stop the bot quickly (Ctrl+C)

---

## Next Steps

- Read the [Getting Started Guide](docs/GETTING_STARTED.md) for detailed information
- Check [Strategy Guide](docs/STRATEGY.md) to understand copy trading strategy
- See [Command Reference](docs/COMMAND_REFERENCE.md) for all available commands
- Review [Examples](docs/EXAMPLES.md) for practical usage examples

---

## Need Help?

If you encounter issues:

1. Run system status check: `python -m src.scripts.setup.system_status`
2. Check logs in `logs/` directory
3. Review the [Troubleshooting](#common-issues--solutions) section above
4. View all commands: `python -m src.scripts.setup.help`

---

**Good luck with your trading! 🚀**




