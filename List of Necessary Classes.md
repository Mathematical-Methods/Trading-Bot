# List of Necessary Classes

This list outlines the core classes required for the Automated Trading Bot, organized according to Clean Architecture layers.

---

## 1. Domain Layer
Contains the core business entities and logic, independent of external systems.

- **`Portfolio`**
  - **Description**: Manages the simulated portfolio, tracking cash balance, positions (e.g., stocks owned), and realized gains/losses from trades.
  - **Key Methods**:
    - `buy(symbol, quantity, price)`: Adds a position to the portfolio.
    - `sell(symbol, quantity, price)`: Removes a position and updates gains/losses.
    - `get_position(symbol)`: Returns the current position for a given stock.
    - `report_gains_losses()`: Calculates and returns total realized profits or losses.

- **`Indicators`**
  - **Description**: Manages and calculates technical indicators (e.g., Relative Strength Index, Simple Moving Average) across multiple time frames (e.g., minute, hour) using market data.
  - **Key Methods**:
    - `__init__(timeframe_configs)`: Initializes the class with configurations for different time frames.
    - `update_minute_data(data)`: Updates the indicator calculations with new minute-level data.
    - `get_indicator_value(indicator_name)`: Retrieves the current value of a specific indicator (e.g., "RSI").

---

## 2. Infrastructure Layer
Handles interactions with external systems, such as APIs and real-time data streams.

- **`SchwabClientAdapter`**
  - **Description**: Acts as an adapter for the Schwab API, providing a clean interface for account management, data retrieval, and trade execution.
  - **Key Methods**:
    - `price_history(symbol, period)`: Fetches historical price data for a stock.
    - `account_details()`: Retrieves account information (e.g., balance).
    - `account_positions()`: Gets current positions held in the account.
    - `order_place(order)`: Submits a buy or sell order to the Schwab API.

- **`Streamer`**
  - **Description**: Manages the Schwab data streamer for real-time market updates, handling subscriptions and incoming messages.
  - **Key Methods**:
    - `start_auto()`: Starts the streaming process automatically.
    - `send(message)`: Sends subscription or control messages to the streamer.
    - `chart_equity()`: Processes real-time chart equity data.
    - `screener_equity()`: Handles real-time screener equity updates.

---

## 3. Application Layer
Coordinates the business logic and interactions between the domain and infrastructure layers.

- **`TradingBot`**
  - **Description**: The main application class that orchestrates the trading bot’s operations, including starting the streamer, processing real-time data, and executing trades based on indicator signals.
  - **Key Methods**:
    - `run()`: Starts the bot and initiates the main loop.
    - `process_stream_messages()`: Interprets incoming streamer messages and triggers actions.
    - `handle_chart_equity(data)`: Processes real-time chart data and updates indicators.
    - `handle_screener_equity(data)`: Responds to screener updates if applicable.

---

## 4. Shared Utilities
Helper classes or utilities used across layers.

- **`SharedList`**
  - **Description**: A thread-safe list or queue for storing and retrieving streamer messages, enabling safe communication between threads (e.g., streamer and bot logic).
  - **Key Methods**:
    - `append(item)`: Adds a message to the list.
    - `pop()`: Retrieves and removes the oldest message.
    - `clear()`: Empties the list.

---

### Why This List Makes Sense
- **Domain Layer**: `Portfolio` and `Indicators` encapsulate the core trading logic, keeping it independent of external dependencies.
- **Infrastructure Layer**: `SchwabClientAdapter` and `Streamer` handle all interactions with the Schwab API and real-time data, isolating external complexities.
- **Application Layer**: `TradingBot` ties everything together, ensuring the system operates cohesively.
- **Shared Utilities**: `SharedList` supports thread-safe communication, which is crucial for real-time systems.

This list provides a clear structure for building the trading bot, ensuring each class has a defined role and responsibility.