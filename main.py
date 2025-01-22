import schwabdev 
import os
import logging
from dotenv import load_dotenv

# Here are initial set-up steps to initialize Trader.
def initialize():
    # load env vars from .env file
    load_dotenv()
    
    # set logging level
    logging.basicConfig(level=logging.INFO) 
    
    # create client
    client = schwabdev.Client(app_key=os.getenv('app_key'),
                              app_secret=os.getenv('app_secret'),
                              callback_url=os.getenv('callback_url'))

    # create streamer
    streamer = client.stream

def example_response_handler(message):
    print("Test" + message)



# Trader 
def main():

    # Initialize the variables / objects of trader.
    initialize()
    
    # We need something to begin the streamer, so we do:
    streamer.start(example_response_handler)





if __name__ == '__main__':
    main()
# To access the access token, call: client.tokens.access_token
# To access the refresh token, call: client.tokens.refresh_token
# To force update the refresh token, call: client.tokens.update_tokens(force=True)
