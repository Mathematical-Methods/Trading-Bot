# Scope
- Trader should be able to monitor the market to determine, based on a predefined strategy, when to issue buy and sell orders. 

# Stepwise refinement
## Trader: main()

### Monitor the market: 
    - Scan for securities which fit a certain criteria:
        - 1. All of the below need to be true: 
            - high market volume compared to relative:
                - See thinkscript: 
                    input volumeRange = 20;
                    input minRVol = 5;
                    input minAvgVol = 200000;

                    def avgVol = Average(volume, volumeRange);
                    def rvol = volume / avgVol[1];
                    plot signal = rvol >= minRVol and avgVol > minAvgVol;
            - Percent change of greater than 9%
            - number of shares ~20,000,000
            - price of stock between $1.00 and $20.00
            - Note: This scan may not be the best for a SMA cross strategy, but I am placing it here as a placeholder. 
    
        - 2. or simply a bullish, but volatile stock. It is unknown currently what this would look like.
        - 3. or have a dynamic config file, or criteria scanning module

    - The stock at the "top of the list" needs to be picked.
        - order of priority needs to be picked, unknown what this should be.

    - listen to that picked stock's prices, or derived indicators.

    - indicators would need to be internally derived (assuming only price action is available) 
        - Ensure that this is scalable, since there'll likely build up to be keeping track of a lot of indicators.
        - feed the price action to a Simple Moving Average function or other indicator function as needed. 

### Monitor your position:
- Know what your position is.

    - provide settled cash amount as needed

    - provide information on being in a position 

### Use strategy to determine buy and sell moments: integrator()
- The initial strategy will be the SimpleMA crossover strategy, requiring that the monitor keep track of the moving averages of the stock price, among other things from position monitoring.

    - Change the buy_SMA flag to true when the data coming from market monitoring, passed to the desired buy_SMA function or any modular strat function, results in a "True".

    - Change the sell_SMA flag to true when the data coming from market monitoring, passed to the desired sell_SMA function or any modular strat function, results in a "True".

    - retrieve the settled cash amount from position monitoring, passed to the conditional buy function

    - determine if in a long position or no position from position monitoring, passed to both conditional buy and sell functions

    - retrieve the stop-loss flag from position monitoring, passed to the conditional sell function

### Issue Buy and sell moments
- the API call to buy that stock will wait until 1 and 2 and 3 == True
    - 1. Is price of stock x buy size < settled cash amount?
    - 2. Am I not in any positions? 
    - 3. Does the desired buy strategy function flag say True? 

- the API call to sell that stock will wait until 1 or (2 and 3) == True
    - 1. Is price of stock less than a defined moving stop-loss? 
    - 2. Am I in a long position?
    - 3. Does the desired sell strategy function flag say True?

