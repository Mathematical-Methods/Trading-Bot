import schwabdev 
import os
import logging
import time
import json
from Indicators import Indicators
from datetime import datetime
from responseFabricator import ResponseFabricator

from dotenv import load_dotenv

# initialize Indicator class
indicators = Indicators()

shared_list = []
def response_handler(message):
    shared_list.append(message)

def screener(service):
    """
    This is the screenerFilter function. It is intended to take the "SCREENER_EQUITY" data service message 
    and review the provided symbols to narrow down the potential options on what to buy.
    
    this function should output a stock to focus on.

    Under construction, currently Returns None. Below is a placeholder operation to practice json parsing.
    """
    #content = service["content"]
    #listOfSymbols = content[0]["4"]
    #for symbolinfo in listOfSymbols:
    #    print(str(symbolinfo["symbol"]) + ", " + str(symbolinfo["lastPrice"]))


def buyCondition(content):
    closePriceMinutely =  content.get("4")
    chartTime = content.get("7")
    twoSMA = indicators.SMA(closePriceMinutely, 2, chartTime)
    fourSMA = indicators.SMA(closePriceMinutely, 4, chartTime)
    
    print(f"TwoSMA:{twoSMA}")
    print(f"FourSMA:{fourSMA}")

    '''
        Stopped HERE! attempting to work out a time-based recording of price data. 
    '''


def stockTrader(service):
    """
    stockTrader()
    Input: LEVELONE_EQUITIES data service message 
    Action:
        1. Extract all details given in the service message
        2. Buy and Sell conditionally.
    """
    # 1. Extracting details
    service_type = service.get("service", None)
    service_timestamp = service.get("timestamp", 0)
    contents = service.get("content", [])
    for content in contents:
        symbol = content.pop("key", "NO KEY")
        fields = content
        # print received details
        print(f"[{service_type} - {symbol}]({datetime.fromtimestamp(service_timestamp//1000)}): {fields}")

    if buyCondition(content):
        pass #logging.info("Put in order to buy %s", symbol)

    #print("stockTrader()")
    #print(json.dumps(service, indent=2))

# Trader 
def main():

    """
    Setup
    -----
    """ 
    # load env vars from .env file
    load_dotenv()
    
    # set logging level
    logging.basicConfig(level=logging.INFO) 
    
    # create client and streamer
    client = schwabdev.Client(app_key=os.getenv('app_key'),
                              app_secret=os.getenv('app_secret'),
                              callback_url=os.getenv('callback_url'))
    
    

    # start streamer - Temporarily commented out
    #streamer = client.stream
    #streamer.start(response_handler)

    # Send in what we want to listen to - Temporarily commented out
    #streamer.send(streamer.screener_equity("NASDAQ_VOLUME_30", "0,1,2,3,4,5,6,7,8"))
    #streamer.send(streamer.level_one_equities("QQQ", "0,1,2,3,4,5,6,7,8"))
    #streamer.send(streamer.chart_equity("QQQ","0,1,2,3,4,5,6,7,8"))


    streamer = ResponseFabricator()
    streamer.setchart_equity(switch=True)
    streamer.start(response_handler, key = "APPL",fields = "0,1,2,3,4,5,6,7,8")

    # Temporary flag for being in a longPosition
    longPosition = False

    # create a while loop to handle reading the streamer
    while True:
        start_time = time.time()
        while len(shared_list) > 0:
            oldest_response = json.loads(shared_list.pop(0)) # load oldest data from the list.
            for rtype, services in oldest_response.items():
                if rtype == "data":
                    #print(rtype)
                    for service in services:
                        
                        # check if service type is "SCREENER_EQUITY"
                        if service["service"] == "SCREENER_EQUITY": 
                            screener(service) # Take the SCREENER_EQUITY service load and run it through a filter.
                        
                        # check if service type is CHART_EQUITY
                        elif service["service"] == "CHART_EQUITY":
                            stockTrader(service) # Take the Levelone equities load to listen and execute trades.
                        
                        # Catch all for any other services.
                        else:
                            print(f"Unexpected service: {service["service"]}")

                elif rtype == "response":
                    pass

                elif rtype == "notify":
                    for service in services:
                        service_timestamp = service.get("heartbeat", 0)
                    print(f"[Heartbeat]({datetime.fromtimestamp(int(service_timestamp)//1000)})")
                    pass
        end_time = time.time()
        time_taken = end_time - start_time
        hertz = (1/time_taken)
        logging.debug("Time: %7.6f, Freq: %9.2f", time_taken, hertz)
        time.sleep(0.5) # slow down check of list length.


if __name__ == '__main__':
    main()
# To access the access token, call: client.tokens.access_token
# To access the refresh token, call: client.tokens.refresh_token
# To force update the refresh token, call: client.tokens.update_tokens(force=True)
