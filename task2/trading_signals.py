import numpy as np
import pandas as pd
import numpy as np


def buy_signal1(prices, drop_threshold=-0.005, stabilization_threshold=0.001, drop_lookback=7, stabilization_lookback=1):
    """
    Detects significant price drops followed by quick stabilization for intraday trading on 1-minute intervals.
    
    Parameters:
    - prices (list or pd.Series): The price data on a 1-minute interval.
    - drop_threshold (float): The percentage decrease to qualify as a drop.
    - stabilization_threshold (float): The percentage increase to qualify as stabilization.
    - drop_lookback (int): Number of minutes to look back for a drop.
    - stabilization_lookback (int): Number of minutes to check for stabilization after a drop.
    
    Returns:
    - bool: True if a significant drop followed by quick stabilization is detected, False otherwise.
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)

    if len(prices) < drop_lookback + stabilization_lookback:
        return False

    # Calculate percentage changes
    price_changes = prices.pct_change().dropna()

    # Detect significant drop
    recent_drops = price_changes.iloc[-(drop_lookback + stabilization_lookback):-stabilization_lookback] < drop_threshold

    # Detect stabilization
    recent_stabilizations = price_changes.iloc[-stabilization_lookback:] > stabilization_threshold

    # Both conditions must be met
    return recent_drops.any() and recent_stabilizations.any()

def buy_signal2(prices, drop_threshold=-0.005, stabilization_period=1):
    """
    Detects a significant drop in the last 15 minutes, followed by stabilization in the next few minutes.

    :param prices: Pandas Series of recent prices, including the current price as the last entry.
    :param drop_threshold: The minimum relative decrease to consider it a significant drop. Negative value.
    :param stabilization_period: Number of minutes to check for stabilization after the drop.
    :return: Boolean indicating whether there has been a significant drop followed by stabilization.
    """
    if len(prices) < 15 + stabilization_period:  
        return False

    # Calculate the percentage change over the last 15 minutes to detect a significant drop
    significant_drop = prices.pct_change(periods=15).iloc[-stabilization_period - 1] <= drop_threshold

    # Check for stabilization after the drop
    stabilization_prices = prices.iloc[-stabilization_period:]
    stabilized = stabilization_prices.pct_change().dropna().abs().max() <= 0.002  # Max change of 0.2% for stabilization

    return significant_drop and stabilized


def sell_signal1(prices, purchase_price, threshold=0.005, stop_loss=0.02):
    """
    Determines if it's advisable to sell based on detecting a potential peak with specific conditions,
    or if a stop-loss condition is met.
    
    :param prices: Pandas Series of recent prices, including the current price as the last entry.
    :param purchase_price: The price at which the stock was bought, for comparison.
    :param threshold: The minimum relative increase from the purchase price to consider it a significant rise.
    :param stop_loss: The maximum allowable loss as a fraction of the purchase price.
    :return: Boolean indicating whether to sell.
    """
    lookback_period = 6  # Total number of comparisons
    required_rises = 4  # Required number of times the price should have been greater
    downward_comparisons = 2  # Number of recent downward trends required
    
    if len(prices) < lookback_period + 1:  # Ensure sufficient data for comparison
        return False
    
    current_price = prices.iloc[-1]  # Current price for the final selling condition

    # Calculate the relative increase from the purchase price to the peak in the lookback period
    peak_price = prices.iloc[-(lookback_period + 1):-downward_comparisons].max()
    relative_increase = (peak_price - prices[0]) / prices[0]
    
    # Stop-loss condition
    is_stop_loss_triggered = (purchase_price - current_price) / purchase_price >= stop_loss
    
    # Count the number of times the price was greater in the lookback period excluding the last two comparisons
    rises = (prices.diff().iloc[-(lookback_period + 1):-downward_comparisons] > 0).sum()
    
    # Check if the last two price movements have been downward
    recent_downward_trend = (prices.diff().iloc[-downward_comparisons:] < 0).all()
    
    # Sell if stop-loss condition is met, or:
    # - The price has risen significantly from the purchase price (above threshold).
    # - Risen the required number of times suggesting a trend.
    # - Recent price movements indicate a downturn.
    # - Current price is still above the purchase price.
    if is_stop_loss_triggered or (relative_increase >= threshold and rises >= required_rises and 
        recent_downward_trend and current_price > purchase_price):
        return True
    
    return False
def sell_signal2(prices, rise_threshold=0.008, stabilization_period=4):
    """
    Detects a significant rise in the last 15 minutes, followed by stabilization in the next few minutes.

    :param prices: Pandas Series of recent prices, including the current price as the last entry.
    :param rise_threshold: The minimum relative increase to consider it a significant rise. Positive value.
    :param stabilization_period: Number of minutes to check for stabilization after the rise.
    :return: Boolean indicating whether there has been a significant rise followed by stabilization.
    """
    if len(prices) < 10 + stabilization_period:  # Ensure there are enough data points
        return False

    # Calculate the percentage change over the last 15 minutes to detect a significant rise
    significant_rise = prices.pct_change(periods=10).iloc[-stabilization_period - 1] >= rise_threshold

    # Check for stabilization after the rise
    stabilization_prices = prices.iloc[-stabilization_period:]
    stabilized = stabilization_prices.pct_change().dropna().abs().max() <= 0.001  # Max change of 0.2% for stabilization

    return significant_rise and stabilized