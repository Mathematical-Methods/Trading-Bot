import asyncio
import threading
import logging
import time
import random
import json

class ResponseFabricator:
    def __init__(self):
        self.active = 0
        self.CHART_EQUITY = True
        self._thread = None
        self._logger = logging.getLogger('ResponseFabricator.Stream')
        self._chart_time = []
        self._chart_equity_fields = {
                                    "0": "",            # Ticker symbol in upper case: string
                                    "1": 149.81,        # Open price: double
                                    "2": 152.93,        # High price: double
                                    "3": 132.56,        # Low price: double
                                    "4": 140.32,        # Close price: double
                                    "5": 202323,        # Volume: double
                                    "6": 1,             # Sequence: long
                                    "7": time.time(),   # Chart time: (milliseconds since epoch)
                                    "8": 520,           # Chart day: int
                                    "key": "",
                                    "delayed": "false", # if delayed
                                    }


    def _start_streamer(self, receiver, **kwargs):
        # start the stream
        while True:
            start_time = time.time()
            if self.CHART_EQUITY == True:
                receiver(self.chart_equity(start_time, **kwargs))
            time.sleep(60)

    def start(self,  receiver=print, daemon: bool = True, **kwargs):
        if self.active == 0:
            def _start_async():
                asyncio.run(self._start_streamer(receiver, **kwargs))

            self._thread = threading.Thread(target=_start_async, daemon=daemon)
            self._thread.start()
        else:
            self._logger.warning("Stream already active.")

    def setchart_equity(self, switch):
        self.CHART_EQUITY = switch

    def chart_equity(self, inputtime, key, fields):
        
        if len(self._chart_time) < 1:
            self._chart_time.append(inputtime)
        
        timediff = inputtime - self._chart_time[0]
        #print(timediff)
        if timediff >= 60:

            for char in fields:
                if char == "0":
                    self._chart_equity_fields[char] = key # Ticker symbol in upper case
                    self._chart_equity_fields["key"] = key
                if char == "1":
                    self._chart_equity_fields[char] = self._chart_equity_fields["4"]
                if char == "2":
                    self._chart_equity_fields[char] = self._chart_equity_fields["1"] + random.uniform(0.00, 10.00)
                if char == "3":
                    self._chart_equity_fields[char] = self._chart_equity_fields["1"] - random.uniform(0.00, 10.00)
                if char == "4":
                    self._chart_equity_fields[char] = random.uniform(self._chart_equity_fields["2"],self._chart_equity_fields["3"])
                if char == "5":
                    self._chart_equity_fields[char] = random.randint(20000, 2000000)
                if char == "6":
                    self._chart_equity_fields[char] += 1
                if char == "7":
                    self._chart_equity_fields[char] = int((time.time() * 1000))

            self._chart_time.pop(0)
            self._chart_time.append(inputtime)
            chart_equity = {"data": [
                              {
                                "service": "CHART_EQUITY",
                                "timestamp": time.time()*1000,
                                "command": "SUBS",
                                "content": [self._chart_equity_fields
                               ]
                              }
                             ]
                            }
            return json.dumps(chart_equity)
        else:
            chart_equity = {"data": [
                              {
                                "service": "Unchanged",
                                "timestamp": time.time(),
                                "command": "None",
                                "content": []
                              }
                             ]
                            }
            return json.dumps(chart_equity)
        




