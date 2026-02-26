#!/usr/bin/env python3
"""
Quick Configuration Tool for Buy Amount Settings

This script helps you easily configure how much the bot spends on each trade.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def print_header():
    """Print header"""
    print('\n' + '=' * 70)
    print('BUY AMOUNT CONFIGURATION TOOL')
    print('=' * 70)
    print('\nThis tool helps you control how much the bot spends on each trade.\n')


def print_current_config():
    """Print current configuration"""
    env_path = Path.cwd() / '.env'
    
    if not env_path.exists():
        print('[INFO] No .env file found. You can create one with this tool.\n')
        return {}
    
    print('Current Configuration:')
    print('-' * 70)
    
    config = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    config[key] = value
    except UnicodeDecodeError:
        # Try with latin-1 as fallback (handles most Windows files)
        with open(env_path, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    config[key] = value
    
    strategy = config.get('COPY_STRATEGY', 'PERCENTAGE')
    copy_size = config.get('COPY_SIZE', '10.0')
    max_order = config.get('MAX_ORDER_SIZE_USD', '100.0')
    min_order = config.get('MIN_ORDER_SIZE_USD', '1.0')
    multiplier = config.get('TRADE_MULTIPLIER', '1.0')
    
    print(f'  Strategy:        {strategy}')
    print(f'  Copy Size:       {copy_size}')
    print(f'  Max Order Size:  ${max_order}')
    print(f'  Min Order Size:  ${min_order}')
    print(f'  Multiplier:      {multiplier}x')
    print()
    
    return config


def explain_strategies():
    """Explain different strategies"""
    print('\nBuy Amount Strategies:')
    print('-' * 70)
    print('1. FIXED - Always buy the same dollar amount per trade')
    print('   Example: Always buy $50 per trade, regardless of trader size')
    print('   Best for: Predictable spending, fixed budget per trade\n')
    
    print('2. PERCENTAGE - Buy a percentage of trader\'s order size')
    print('   Example: Buy 10% of trader\'s order (if trader buys $100, you buy $10)')
    print('   Best for: Proportional exposure, scaling with trader size\n')
    
    print('3. ADAPTIVE - Adjust percentage based on trade size')
    print('   Example: Higher % for small trades, lower % for large trades')
    print('   Best for: Advanced users who want dynamic scaling\n')


def configure_fixed_amount() -> dict:
    """Configure fixed buy amount"""
    print('\nFIXED Amount Configuration')
    print('-' * 70)
    
    while True:
        amount_str = input('Enter fixed buy amount per trade (USD, e.g., 50.0): ').strip()
        try:
            amount = float(amount_str)
            if amount < 1.0:
                print('[ERROR] Minimum order size is $1.00\n')
                continue
            if amount > 10000:
                print('[WARNING] Amount seems very high. Are you sure? (y/n): ')
                confirm = input().strip().lower()
                if confirm != 'y':
                    continue
            break
        except ValueError:
            print('[ERROR] Please enter a valid number\n')
    
    max_order = input(f'Maximum order size cap (USD, default {amount}): ').strip()
    max_order = float(max_order) if max_order else amount
    
    return {
        'COPY_STRATEGY': 'FIXED',
        'COPY_SIZE': str(amount),
        'MAX_ORDER_SIZE_USD': str(max(max_order, amount)),
    }


def configure_percentage() -> dict:
    """Configure percentage buy amount"""
    print('\nPERCENTAGE Configuration')
    print('-' * 70)
    
    while True:
        percent_str = input('Enter percentage of trader\'s order (e.g., 10.0 for 10%): ').strip()
        try:
            percent = float(percent_str)
            if percent <= 0 or percent > 100:
                print('[ERROR] Percentage must be between 0 and 100\n')
                continue
            break
        except ValueError:
            print('[ERROR] Please enter a valid number\n')
    
    max_order = input('Maximum order size cap (USD, default 100.0): ').strip()
    max_order = float(max_order) if max_order else 100.0
    
    return {
        'COPY_STRATEGY': 'PERCENTAGE',
        'COPY_SIZE': str(percent),
        'MAX_ORDER_SIZE_USD': str(max_order),
    }


def update_env_file(config: dict):
    """Update .env file with new configuration"""
    env_path = Path.cwd() / '.env'
    
    if not env_path.exists():
        print('[ERROR] .env file not found. Please run setup wizard first.')
        print('Run: python -m src.scripts.setup.setup')
        return False
    
    # Read existing .env file
    lines = []
    updated_keys = set(config.keys())
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                original_line = line
                stripped = line.strip()
                
                # Skip empty lines and comments
                if not stripped or stripped.startswith('#'):
                    lines.append(original_line)
                    continue
                
                # Check if this line contains a config we want to update
                if '=' in stripped:
                    key = stripped.split('=')[0].strip()
                    if key in updated_keys:
                        # Update this line
                        value = config[key]
                        lines.append(f"{key} = '{value}'\n")
                        updated_keys.remove(key)
                        continue
                
                lines.append(original_line)
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        with open(env_path, 'r', encoding='latin-1') as f:
            for line in f:
                original_line = line
                stripped = line.strip()
                
                # Skip empty lines and comments
                if not stripped or stripped.startswith('#'):
                    lines.append(original_line)
                    continue
                
                # Check if this line contains a config we want to update
                if '=' in stripped:
                    key = stripped.split('=')[0].strip()
                    if key in updated_keys:
                        # Update this line
                        value = config[key]
                        lines.append(f"{key} = '{value}'\n")
                        updated_keys.remove(key)
                        continue
                
                lines.append(original_line)
    
    # Add any remaining config that wasn't in the file
    for key in updated_keys:
        lines.append(f"{key} = '{config[key]}'\n")
    
    # Write back to file with UTF-8 encoding
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True


def show_examples(config: dict):
    """Show examples of how buy amounts will be calculated"""
    print('\n' + '=' * 70)
    print('EXAMPLES: How Your Buy Amounts Will Work')
    print('=' * 70)
    
    strategy = config.get('COPY_STRATEGY', 'PERCENTAGE')
    copy_size = float(config.get('COPY_SIZE', '10.0'))
    max_order = float(config.get('MAX_ORDER_SIZE_USD', '100.0'))
    multiplier = float(config.get('TRADE_MULTIPLIER', '1.0'))
    
    trader_sizes = [10, 50, 100, 500, 1000]
    
    print(f'\nStrategy: {strategy}')
    print(f'Copy Size: {copy_size}')
    print(f'Max Order Cap: ${max_order}')
    if multiplier != 1.0:
        print(f'Multiplier: {multiplier}x')
    print()
    print('Trader Order | Your Buy Amount')
    print('-' * 40)
    
    for trader_size in trader_sizes:
        if strategy == 'FIXED':
            base = copy_size
        elif strategy == 'PERCENTAGE':
            base = trader_size * (copy_size / 100)
        else:
            base = trader_size * (copy_size / 100)  # Simplified for examples
        
        final = min(base * multiplier, max_order)
        final = max(final, 1.0)  # Min order size
        
        print(f'${trader_size:>10.0f} | ${final:>12.2f}')
    
    print()


def main():
    """Main function"""
    print_header()
    
    # Show current config
    current_config = print_current_config()
    
    # Explain strategies
    explain_strategies()
    
    # Choose strategy
    print('Choose how you want to control buy amounts:')
    print('  1. FIXED - Set a fixed dollar amount per trade')
    print('  2. PERCENTAGE - Set a percentage of trader\'s order')
    print('  3. Exit without changes')
    
    choice = input('\nEnter choice (1-3): ').strip()
    
    if choice == '1':
        new_config = configure_fixed_amount()
    elif choice == '2':
        new_config = configure_percentage()
    else:
        print('\nExiting without changes.')
        return
    
    # Keep existing min order size
    new_config['MIN_ORDER_SIZE_USD'] = current_config.get('MIN_ORDER_SIZE_USD', '1.0')
    
    # Ask about multiplier
    use_multiplier = input('\nUse a multiplier? (y/n, default n): ').strip().lower()
    if use_multiplier == 'y':
        multiplier_str = input('Enter multiplier (e.g., 1.5 for 1.5x, 0.5 for 0.5x): ').strip()
        try:
            multiplier = float(multiplier_str)
            if multiplier > 0:
                new_config['TRADE_MULTIPLIER'] = str(multiplier)
        except ValueError:
            print('[WARNING] Invalid multiplier, skipping')
    
    # Show examples
    show_examples(new_config)
    
    # Confirm
    confirm = input('Apply these settings? (y/n): ').strip().lower()
    if confirm != 'y':
        print('\nCancelled. No changes made.')
        return
    
    # Update .env file
    if update_env_file(new_config):
        print('\n[SUCCESS] Configuration updated!')
        print('\nTo apply changes, restart your bot.')
    else:
        print('\n[ERROR] Failed to update configuration')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nCancelled by user.')
        sys.exit(0)
    except Exception as e:
        print(f'\n[ERROR] {e}')
        sys.exit(1)

