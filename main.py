import schwabdev 
import os
import logging
import time
import json
from dotenv import load_dotenv


shared_list = []
def response_handler(message):
    shared_list.append(message)

# Trader 
def main():

    # load env vars from .env file
    load_dotenv()
    
    # set logging level
    logging.basicConfig(level=logging.INFO) 
    
    # create client and streamer
    client = schwabdev.Client(app_key=os.getenv('app_key'),
                              app_secret=os.getenv('app_secret'),
                              callback_url=os.getenv('callback_url'))
    streamer = client.stream

    # start streamer and send request for what symbols we want.
    streamer.start(response_handler)
    streamer.send(streamer.level_one_equities("AMD", "0", "ADD"))

    secondoldest_response = 0

    # create a while loop to handle reading the streamer
    while True:
        while len(shared_list) > 0:
            oldest_response = json.loads(shared_list.pop(0)) # load oldest data from the list.
            for rtype, services in oldest_response.items():
                if rtype == "data":
                    print(oldest_response)
                    for service in services:
                        print(service)
                elif rtype == "response":
                    print(oldest_response)
                elif rtype == "notify":
                    print(oldest_response['notify'][0]['heartbeat'])

        time.sleep(0.5) # slow down check of list length.


if __name__ == '__main__':
    main()
# To access the access token, call: client.tokens.access_token
# To access the refresh token, call: client.tokens.refresh_token
# To force update the refresh token, call: client.tokens.update_tokens(force=True)
