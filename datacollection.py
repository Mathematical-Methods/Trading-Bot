import schwabdev
import json
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Initialize the Schwab client
load_dotenv()
app_key = os.getenv('app_key')         # Replace with your app key
app_secret = os.getenv('app_secret')  # Replace with your app secret
callback_url = os.getenv('callback_url')  # Replace with your callback URL
client = schwabdev.Client(app_key, app_secret, callback_url)

# Placeholder list of 100 stock symbols (replace with actual symbols)
symbols = ['AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'AIG', 'AMD', 'AMGN',
            'AMT', 'AMZN', 'AVGO', 'AXP', 'BA', 'BAC', 'BK', 'BKNG', 'BLK',
            'BMY', 'BRK.B', 'C', 'CAT', 'CHTR', 'CL', 'CMCSA', 'COF', 'COP', 
            'COST', 'CRM', 'CSCO', 'CVS', 'CVX', 'DE', 'DHR', 'DIS', 'DOW', 
            'DUK', 'EMR', 'F', 'FDX', 'GD', 'GE', 'GILD', 'GM', 'GOOG', 
            'GOOGL', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'INTU', 'JNJ', 'JPM', 
            'KHC', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'MA', 'MCD', 'MDLZ', 
            'MDT', 'MET', 'META', 'MMM', 'MO', 'MRK', 'MS', 'MSFT', 'NEE', 
            'NFLX', 'NKE', 'NVDA', 'ORCL', 'PEP', 'PFE', 'PG', 'PM', 
            'PYPL', 'QCOM', 'RTX', 'SBUX', 'SCHW', 'SO', 'SPG', 'T', 'TGT', 
            'TMO', 'TMUS', 'TSLA', 'TXN', 'UNH', 'UNP', 'UPS', 'USB', 'V', 
            'VZ', 'WFC', 'WMT', 'XOM']

# Function to fetch minute-level data for a symbol over a specified number of days
def fetch_minute_data(symbol, days=60):
    """
    Fetch up to 'days' worth of minute-level candlestick data for a stock.
    Makes multiple requests in 10-day chunks due to API limits.
    Returns a sorted list of candlestick data.
    """
    all_candles = []
    end_date = datetime.now()

    # Loop to fetch data in 10-day chunks
    for _ in range((days // 10) + 1):
        start_date = end_date - timedelta(days=10)
        
        # Fetch price history for the 10-day period
        response = client.price_history(
            symbol=symbol,
            periodType="day",
            frequencyType="minute",
            frequency=1,
            startDate=int(start_date.timestamp() * 1000),  # Milliseconds
            endDate=int(end_date.timestamp() * 1000),      # Milliseconds
            needExtendedHoursData=False
        )
        
        # Check if the request was successful
        if response.ok:
            candles = response.json().get("candles", [])
            if not candles:
                print(f"No more data available for {symbol} before {start_date}")
                break
            all_candles.extend(candles)
        else:
            print(f"Error fetching data for {symbol} from {start_date} to {end_date}: {response.status_code}")
            break
        
        # Move the window back
        end_date = start_date
        time.sleep(0.5)  # Delay to avoid hitting rate limits

    # Sort candles by timestamp to ensure chronological order
    all_candles.sort(key=lambda x: x["datetime"])
    return all_candles

# Main loop to process each stock
for symbol in symbols:
    print(f"Fetching data for {symbol}...")
    try:
        # Fetch up to 60 days of minute data
        data = fetch_minute_data(symbol, days=60)
        
        if data:
            # Save to a JSON file named after the symbol
            filename = f"./stock_data/{symbol}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Saved {len(data)} candles to {filename}")
        else:
            print(f"No data retrieved for {symbol}")
            
    except Exception as e:
        print(f"Failed to process {symbol}: {str(e)}")

print("Data collection complete.")