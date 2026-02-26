"""
Post order to Polymarket
"""
from typing import Optional, Dict, Any
from ..config.env import ENV
from ..utils.logger import info, warning, order_result, error
from ..config.copy_strategy import calculate_order_size, get_trade_multiplier

RETRY_LIMIT = ENV.RETRY_LIMIT
COPY_STRATEGY_CONFIG = ENV.COPY_STRATEGY_CONFIG

# Polymarket minimum order sizes
MIN_ORDER_SIZE_USD = 1.0  # Minimum order size in USD for BUY orders
MIN_ORDER_SIZE_TOKENS = 1.0  # Minimum order size in tokens for SELL/MERGE orders


def extract_order_error(response: Any) -> Optional[str]:
    """Extract error message from order response"""
    if not response:
        return None
    
    if isinstance(response, str):
        return response
    
    if isinstance(response, dict):
        # Check direct error
        if 'error' in response:
            error_val = response['error']
            if isinstance(error_val, str):
                return error_val
            if isinstance(error_val, dict):
                if 'error' in error_val:
                    return error_val['error']
                if 'message' in error_val:
                    return error_val['message']
        
        # Check other error fields
        if 'errorMsg' in response:
            return response['errorMsg']
        if 'message' in response:
            return response['message']
    
    return None


def is_insufficient_balance_or_allowance_error(message: Optional[str]) -> bool:
    """Check if error is related to insufficient balance or allowance"""
    if not message:
        return False
    lower = message.lower()
    return 'not enough balance' in lower or 'allowance' in lower


def is_fok_fill_error(message: Optional[str]) -> bool:
    """Check if error is related to FOK order not being fully filled"""
    if not message:
        return False
    lower = message.lower()
    return 'fok orders are fully filled or killed' in lower or 'couldn\'t be fully filled' in lower


def calculate_available_liquidity(order_book_levels: list, target_amount: float, is_buy: bool) -> float:
    """
    Calculate available liquidity across order book levels.
    Returns conservative estimate (80% of available) to account for order book changes.
    
    Args:
        order_book_levels: List of order book entries (asks for buy, bids for sell)
        target_amount: Desired order size (in tokens for sell, USD for buy)
        is_buy: True for buy orders, False for sell orders
    
    Returns:
        Available liquidity that can be safely used for FOK orders
    """
    if not order_book_levels:
        return 0.0
    
    total_available = 0.0
    
    if is_buy:
        # For buy orders: calculate USD value available
        for ask in order_book_levels:
            size = float(ask.get('size', 0))
            price = float(ask.get('price', 0))
            usd_value = size * price
            total_available += usd_value
            if total_available >= target_amount:
                break
    else:
        # For sell orders: calculate token amount available
        for bid in order_book_levels:
            size = float(bid.get('size', 0))
            total_available += size
            if total_available >= target_amount:
                break
    
    # Use 80% of available liquidity to be conservative (account for order book changes)
    conservative_available = total_available * 0.8
    
    # Don't exceed target amount
    return min(conservative_available, target_amount)


async def post_order(
    clob_client: Any,
    condition: str,
    my_position: Optional[Dict[str, Any]],
    user_position: Optional[Dict[str, Any]],
    trade: Dict[str, Any],
    my_balance: float,
    user_balance: float,
    user_address: str
):
    """Post order to Polymarket (logging only, no database)"""
    if condition == 'merge':
        info('Executing MERGE strategy...')
        if not my_position:
            warning('No position to merge')
            return
        
        remaining = my_position.get('size', 0)
        
        # Check minimum order size
        if remaining < MIN_ORDER_SIZE_TOKENS:
            warning(f'Position size ({remaining:.2f} tokens) too small to merge - skipping')
            return
        
        retry = 0
        abort_due_to_funds = False
        consecutive_fok_failures = 0
        
        while remaining > 0 and retry < RETRY_LIMIT:
            try:
                order_book = await clob_client.get_order_book(trade['asset'])
                if not order_book.get('bids') or len(order_book['bids']) == 0:
                    warning('No bids available in order book')
                    break
                
                # Sort bids by price (highest first) for liquidity calculation
                sorted_bids = sorted(order_book['bids'], key=lambda x: float(x['price']), reverse=True)
                max_price_bid = sorted_bids[0]
                
                info(f'Best bid: {max_price_bid["size"]} @ ${max_price_bid["price"]}')
                
                # Calculate available liquidity conservatively
                available_liquidity = calculate_available_liquidity(sorted_bids, remaining, is_buy=False)
                
                # If we've had FOK failures, reduce size further
                if consecutive_fok_failures > 0:
                    reduction_factor = 0.5 ** consecutive_fok_failures  # 50%, 25%, 12.5%...
                    available_liquidity = min(available_liquidity, remaining * reduction_factor)
                    info(f'Reducing order size due to FOK failures (factor: {reduction_factor:.2%})')
                
                # Ensure we don't exceed remaining or available liquidity
                order_amount = min(remaining, available_liquidity, float(max_price_bid['size']))
                
                if order_amount < MIN_ORDER_SIZE_TOKENS:
                    warning(f'Available liquidity ({order_amount:.2f} tokens) below minimum ({MIN_ORDER_SIZE_TOKENS} tokens)')
                    break
                
                order_args = {
                    'side': 'SELL',
                    'tokenID': my_position['asset'],
                    'amount': order_amount,
                    'price': float(max_price_bid['price']),
                }
                
                info(f'Creating order: {order_amount:.2f} tokens @ ${order_args["price"]} (Available liquidity: {available_liquidity:.2f})')
                
                signed_order = await clob_client.create_market_order(order_args)
                resp = await clob_client.post_order(signed_order, 'FOK')
                
                if resp.get('success') is True:
                    retry = 0
                    consecutive_fok_failures = 0
                    order_result(True, f'Sold {order_args["amount"]} tokens at ${order_args["price"]}')
                    remaining -= order_args['amount']
                else:
                    error_message = extract_order_error(resp)
                    if is_insufficient_balance_or_allowance_error(error_message):
                        abort_due_to_funds = True
                        warning(f'Order rejected: {error_message or "Insufficient balance or allowance"}')
                        warning('Skipping remaining attempts. Top up funds or check allowance before retrying.')
                        break
                    elif is_fok_fill_error(error_message):
                        consecutive_fok_failures += 1
                        retry += 1
                        warning(f'FOK order failed - insufficient liquidity (attempt {retry}/{RETRY_LIMIT}). Reducing size and retrying...')
                        if consecutive_fok_failures >= 3:
                            warning('Multiple FOK failures - order book may have insufficient depth. Consider using IOC orders.')
                            break
                    else:
                        retry += 1
                        consecutive_fok_failures = 0
                        warning(f'Order failed (attempt {retry}/{RETRY_LIMIT}){f" - {error_message}" if error_message else ""}')
            except Exception as e:
                retry += 1
                consecutive_fok_failures = 0
                warning(f'Order error (attempt {retry}/{RETRY_LIMIT}): {e}')
        
        if abort_due_to_funds or retry >= RETRY_LIMIT:
            return
        
    elif condition == 'buy':
        info('Executing BUY strategy...')
        
        trader_order_size = trade.get('usdcSize', 0)
        info(f'Your balance: ${my_balance:.2f}')
        info(f'Trader bought: ${trader_order_size:.2f}')
        
        # Get current position size for position limit checks
        current_position_value = (my_position.get('size', 0) * my_position.get('avgPrice', 0)) if my_position else 0
        
        order_calc = calculate_order_size(
            COPY_STRATEGY_CONFIG,
            trader_order_size,
            my_balance,
            current_position_value
        )
        
        info(f'Buy amount calculation: {order_calc.reasoning}')
        info(f'→ Final buy amount: ${order_calc.final_amount:.2f}')
        
        if order_calc.final_amount == 0:
            warning(f'Cannot execute: {order_calc.reasoning}')
            if order_calc.below_minimum:
                warning('Increase COPY_SIZE or wait for larger trades')
            return
        
        remaining = order_calc.final_amount
        available_balance = my_balance
        
        retry = 0
        abort_due_to_funds = False
        total_bought_tokens = 0
        consecutive_fok_failures = 0
        
        while remaining > 0 and retry < RETRY_LIMIT:
            try:
                order_book = await clob_client.get_order_book(trade['asset'])
                if not order_book.get('asks') or len(order_book['asks']) == 0:
                    warning('No asks available in order book')
                    break
                
                # Sort asks by price (lowest first) for liquidity calculation
                sorted_asks = sorted(order_book['asks'], key=lambda x: float(x['price']))
                min_price_ask = sorted_asks[0]
                
                info(f'Best ask: {min_price_ask["size"]} @ ${min_price_ask["price"]}')
                
                if remaining < MIN_ORDER_SIZE_USD:
                    break
                
                # Calculate available liquidity conservatively (in USD)
                available_liquidity_usd = calculate_available_liquidity(sorted_asks, remaining, is_buy=True)
                
                # If we've had FOK failures, reduce size further
                if consecutive_fok_failures > 0:
                    reduction_factor = 0.5 ** consecutive_fok_failures  # 50%, 25%, 12.5%...
                    available_liquidity_usd = min(available_liquidity_usd, remaining * reduction_factor)
                    info(f'Reducing order size due to FOK failures (factor: {reduction_factor:.2%})')
                
                # Ensure we don't exceed remaining, available liquidity, or balance
                order_size = min(remaining, available_liquidity_usd, available_balance)
                
                if order_size < MIN_ORDER_SIZE_USD:
                    break
                
                if available_balance < order_size:
                    warning(f'Insufficient balance: Need ${order_size:.2f} but only have ${available_balance:.2f}')
                    abort_due_to_funds = True
                    break
                
                order_args = {
                    'side': 'BUY',
                    'tokenID': trade['asset'],
                    'amount': order_size,
                    'price': float(min_price_ask['price']),
                }
                
                info(f'Creating order: ${order_size:.2f} @ ${min_price_ask["price"]} (Balance: ${available_balance:.2f}, Available liquidity: ${available_liquidity_usd:.2f})')
                
                signed_order = await clob_client.create_market_order(order_args)
                resp = await clob_client.post_order(signed_order, 'FOK')
                
                if resp.get('success') is True:
                    retry = 0
                    consecutive_fok_failures = 0
                    tokens_bought = order_args['amount'] / order_args['price']
                    total_bought_tokens += tokens_bought
                    order_result(
                        True,
                        f'Bought ${order_args["amount"]:.2f} at ${order_args["price"]} ({tokens_bought:.2f} tokens)'
                    )
                    remaining -= order_args['amount']
                    available_balance -= order_args['amount']
                else:
                    error_message = extract_order_error(resp)
                    if is_insufficient_balance_or_allowance_error(error_message):
                        abort_due_to_funds = True
                        warning(f'Order rejected: {error_message or "Insufficient balance or allowance"}')
                        warning('Skipping remaining attempts. Top up funds or check allowance before retrying.')
                        break
                    elif is_fok_fill_error(error_message):
                        consecutive_fok_failures += 1
                        retry += 1
                        warning(f'FOK order failed - insufficient liquidity (attempt {retry}/{RETRY_LIMIT}). Reducing size and retrying...')
                        if consecutive_fok_failures >= 3:
                            warning('Multiple FOK failures - order book may have insufficient depth. Consider using IOC orders.')
                            break
                    else:
                        retry += 1
                        consecutive_fok_failures = 0
                        warning(f'Order failed (attempt {retry}/{RETRY_LIMIT}){f" - {error_message}" if error_message else ""}')
            except Exception as e:
                retry += 1
                consecutive_fok_failures = 0
                warning(f'Order error (attempt {retry}/{RETRY_LIMIT}): {e}')
        
        if abort_due_to_funds or retry >= RETRY_LIMIT:
            return

    elif condition == 'sell':
        info('Executing SELL strategy...')
        
        if not my_position:
            warning('No position to sell')
            return
        
        # No database: use current position size for proportional sell (no tracked previous buys)
        previous_buys = []
        total_bought_tokens = 0
        
        if total_bought_tokens > 0:
            info(f'Found {len(previous_buys)} previous purchases: {total_bought_tokens:.2f} tokens bought')
        
        remaining = 0
        if not user_position:
            remaining = my_position.get('size', 0)
            info(f'Trader closed entire position → Selling all your {remaining:.2f} tokens')
        else:
            trader_sell_size = trade.get('size', 0)
            user_position_size = user_position.get('size', 0)
            trader_position_before = user_position_size + trader_sell_size
            
            info(f'Trader selling: {trader_sell_size:.2f} tokens ({((trader_sell_size / trader_position_before) * 100) if trader_position_before > 0 else 0:.2f}% of their position)')
            
            trader_sell_percent = trader_sell_size / trader_position_before if trader_position_before > 0 else 0
            
            if total_bought_tokens > 0:
                base_sell_size = total_bought_tokens * trader_sell_percent
                info(f'Calculating from tracked purchases: {total_bought_tokens:.2f} × {(trader_sell_percent * 100):.2f}% = {base_sell_size:.2f} tokens')
            else:
                base_sell_size = my_position.get('size', 0) * trader_sell_percent
                warning(f'No tracked purchases found, using current position: {my_position.get("size", 0):.2f} × {(trader_sell_percent * 100):.2f}% = {base_sell_size:.2f} tokens')
            
            multiplier = get_trade_multiplier(COPY_STRATEGY_CONFIG, trade.get('usdcSize', 0))
            remaining = base_sell_size * multiplier
            
            if multiplier != 1.0:
                info(f'Applying {multiplier}x multiplier: {base_sell_size:.2f} → {remaining:.2f} tokens')
        
        if remaining < MIN_ORDER_SIZE_TOKENS:
            warning(f'Sell amount {remaining:.2f} tokens below minimum ({MIN_ORDER_SIZE_TOKENS} token)')
            return
        
        my_position_size = my_position.get('size', 0)
        if remaining > my_position_size:
            warning(f'Calculated sell {remaining:.2f} tokens > Your position {my_position_size:.2f} tokens')
            remaining = my_position_size
        
        retry = 0
        abort_due_to_funds = False
        total_sold_tokens = 0
        consecutive_fok_failures = 0
        
        while remaining > 0 and retry < RETRY_LIMIT:
            try:
                order_book = await clob_client.get_order_book(trade['asset'])
                if not order_book.get('bids') or len(order_book['bids']) == 0:
                    warning('No bids available in order book')
                    break
                
                # Sort bids by price (highest first) for liquidity calculation
                sorted_bids = sorted(order_book['bids'], key=lambda x: float(x['price']), reverse=True)
                max_price_bid = sorted_bids[0]
                
                info(f'Best bid: {max_price_bid["size"]} @ ${max_price_bid["price"]}')
                
                if remaining < MIN_ORDER_SIZE_TOKENS:
                    break
                
                # Calculate available liquidity conservatively
                available_liquidity = calculate_available_liquidity(sorted_bids, remaining, is_buy=False)
                
                # If we've had FOK failures, reduce size further
                if consecutive_fok_failures > 0:
                    reduction_factor = 0.5 ** consecutive_fok_failures  # 50%, 25%, 12.5%...
                    available_liquidity = min(available_liquidity, remaining * reduction_factor)
                    info(f'Reducing order size due to FOK failures (factor: {reduction_factor:.2%})')
                
                # Ensure we don't exceed remaining or available liquidity
                sell_amount = min(remaining, available_liquidity)
                
                if sell_amount < MIN_ORDER_SIZE_TOKENS:
                    break
                
                order_args = {
                    'side': 'SELL',
                    'tokenID': trade['asset'],
                    'amount': sell_amount,
                    'price': float(max_price_bid['price']),
                }
                
                info(f'Creating sell order: {sell_amount:.2f} tokens @ ${max_price_bid["price"]} (Available liquidity: {available_liquidity:.2f})')
                
                signed_order = await clob_client.create_market_order(order_args)
                resp = await clob_client.post_order(signed_order, 'FOK')
                
                if resp.get('success') is True:
                    retry = 0
                    consecutive_fok_failures = 0
                    total_sold_tokens += order_args['amount']
                    order_result(True, f'Sold {order_args["amount"]:.2f} tokens at ${order_args["price"]}')
                    remaining -= order_args['amount']
                else:
                    error_message = extract_order_error(resp)
                    if is_insufficient_balance_or_allowance_error(error_message):
                        abort_due_to_funds = True
                        warning(f'Order rejected: {error_message or "Insufficient balance or allowance"}')
                        warning('Skipping remaining attempts. Top up funds or check allowance before retrying.')
                        break
                    elif is_fok_fill_error(error_message):
                        consecutive_fok_failures += 1
                        retry += 1
                        warning(f'FOK order failed - insufficient liquidity (attempt {retry}/{RETRY_LIMIT}). Reducing size and retrying...')
                        if consecutive_fok_failures >= 3:
                            warning('Multiple FOK failures - order book may have insufficient depth. Consider using IOC orders.')
                            break
                    else:
                        retry += 1
                        consecutive_fok_failures = 0
                        warning(f'Order failed (attempt {retry}/{RETRY_LIMIT}){f" - {error_message}" if error_message else ""}')
            except Exception as e:
                retry += 1
                consecutive_fok_failures = 0
                warning(f'Order error (attempt {retry}/{RETRY_LIMIT}): {e}')
        
        if total_sold_tokens > 0 and total_bought_tokens > 0:
            sell_percentage = total_sold_tokens / total_bought_tokens
            info(f'Sold {(sell_percentage * 100):.1f}% of position (no DB tracking)')
        
        if abort_due_to_funds or retry >= RETRY_LIMIT:
            return

