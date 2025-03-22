import logging

def load_initial_historical_data(client, symbols, indicators):
    """
    Fetches initial historical minute-level data for a list of symbols and updates the indicators object.

    Args:
        client (schwabdev.Client): Schwab API client object for fetching historical data.
        symbols (list): List of stock symbols (e.g., ["TSLA", "AAPL"]) to fetch data for.
        indicators (Indicators): Instance of Indicators class to update with historical data.

    Returns:
        bool: True if data was successfully loaded for all symbols, False if any symbol failed.
    """
    if not symbols:
        logging.info("No symbols provided for historical data loading")
        return True  # Nothing to do, but not an error

    success = True
    for symbol in symbols:
        try:
            # Fetch 5 days of 1-minute historical data using the Schwab API
            response = client.price_history(
                symbol=symbol,
                periodType="day",
                period=5,  # Number of days of historical data
                frequencyType="minute",
                frequency=1,  # 1-minute intervals
                needExtendedHoursData=False
            )
            if not response.ok:
                logging.error(f"Failed to fetch history for {symbol}: {response.status_code} - {response.text}")
                success = False
                continue

            history_data = response.json()
            candles = history_data.get('candles', [])
            if not candles:
                logging.info(f"No historical data found for {symbol}")
                continue

            # Pass each candle's data to the indicators object
            for candle in candles:
                close = candle['close']
                volume = candle['volume']
                timestamp = candle['datetime']  # Timestamp in milliseconds
                indicators.update_minute_data(symbol, close, volume, timestamp)

            logging.info(f"Loaded historical data for {symbol}")
        except Exception as e:
            logging.error(f"Exception while loading historical data for {symbol}: {str(e)}")
            success = False

    return success