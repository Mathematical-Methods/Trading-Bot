# Automated Trading Bot

## Overview
This project is an automated stock trading bot built with Python, leveraging the Schwab API for real-time market data and trading. It adheres to **Clean Architecture** principles to ensure modularity, testability, and maintainability. The bot processes minutely stock data, aggregates it into configurable time frames (e.g., minute, hour), and calculates technical indicators (e.g., RSI, SMA) to drive trading decisions. It supports both simulated and real trading modes.

## Features
- **Flexible Time Frame Aggregation**: Processes minutely data into multiple time frames (e.g., minutely RSI, hourly SMA) within the `Indicators` class.
- **Technical Indicators**: Includes RSI, moving average crossovers, and more, configurable per time frame.
- **Simulation & Real Trading**: Runs in simulation mode with a virtual portfolio or executes real trades via the Schwab API.
- **Real-Time Data**: Streams CHART_EQUITY and SCREENER_EQUITY data for dynamic trading decisions.
- **Test-Driven Development**: Includes unit tests for core functionalities.

## Project Structure
Automated_Trading/
├── application/         # Application layer (business logic)
├── domain/              # Domain layer (entities and business rules)
│   └── entities/        # Core entities (e.g., Portfolio, Indicators)
├── infrastructure/      # Infrastructure layer (external systems)
│   ├── adapters/        # API clients and adapters (e.g., Schwab client)
│   └── config/          # Configuration (e.g., environment setup)
├── interfaces/          # Interface definitions (e.g., for UI or external services)
├── tests/               # Unit tests for all layers
├── main.py              # Entry point for the application
└── README.md            # Project documentation

## Conceptual Functions
The bot is built around 20 core functions, organized by Clean Architecture layers:

### Infrastructure Layer
1. **`initialize_environment()`** - Loads `.env` configuration and sets up logging.
2. **`start_client(app_key, app_secret, callback_url)`** - Initializes the Schwab API client.
4. **`fetch_account_hash(client, simulate)`** - Retrieves the account hash for real trading.
5. **`request_account_details(client, account_hash)`** - Fetches account details from Schwab.
6. **`request_account_positions(client, account_hash)`** - Retrieves current positions from Schwab.
7. **`load_initial_historical_data(client, symbols, indicators)`** - Fetches and feeds historical minute data to `Indicators`.

### Application Layer
8. **`start_streamer(client, response_handler, start_time, stop_time, days, timezone)`** - Starts the Schwab data streamer.
9. **`subscribe_to_streams(streamer, initial_symbols)`** - Subscribes to real-time data streams.
10. **`process_stream_messages(shared_list, client, simulate, portfolio, indicators)`** - Dispatches streamer messages to handlers.
11. **`handle_chart_equity(service, client, simulate, portfolio, indicators)`** - Processes CHART_EQUITY data and executes trades.
12. **`handle_screener_equity(service, streamer, indicators, portfolio, client)`** - Manages SCREENER_EQUITY subscriptions.
17. **`execute_trade(action, symbol, price, quantity, client, simulate, portfolio, account_hash)`** - Executes buy/sell trades.
18. **`report_portfolio_status(portfolio, interval, last_report_time)`** - Logs simulated portfolio status.
19. **`report_account_status(client, account_hash, interval, last_report_time)`** - Logs real account status.
20. **`main_loop(shared_list, client, simulate, portfolio, indicators, report_interval)`** - Runs the main event loop.

### Domain Layer
3. **`initialize_portfolio(initial_cash)`** - Creates a simulated portfolio.
13. **`update_indicators(symbol, close, volume, timestamp, indicators)`** - Updates `Indicators` with minute data, aggregating per internal config.
14. **`calculate_rsi(market_inputs, period)`** - Computes RSI for a given period.
15. **`calculate_ma_crossover(market_inputs, short_period, long_period)`** - Detects MA crossovers.
16. **`calculate_trading_action(symbol, indicators, *indicator_values)`** - Determines trading actions based on indicators.

## Future Enhancements
- Add support for additional indicators (e.g., MACD, Bollinger Bands).
- Implement dynamic time frame reconfiguration.
- Integrate a UI or CLI for manual control.

## License
This project is made public for demonstration purposes. As it is incomplete, no license is granted at this time.