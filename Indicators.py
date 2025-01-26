class Indicators:
    def __init__(self):
        self.sma_values = {}
        self.sma_lasttime = {}
        self.hourlysma_values = {}
        self.timeElapsed = None

    # Simple Moving Average
    def SMA(self, input, length, timeSinceEpoch):
        #print(f"SMA: {input}, {length}, {timeSinceEpoch}")

        if length not in self.sma_lasttime:
            self.sma_lasttime[length] = 0

        if self.sma_lasttime[length] == 0:
            #print("Last time:", self.sma_lasttime)
            self.sma_lasttime[length] = timeSinceEpoch
        
        #print("Last Time 2: ", self.sma_lasttime)
        #print("Current time: ", timeSinceEpoch)

        timediff = timeSinceEpoch - self.sma_lasttime[length]
        #print("TimeDiff: ", timediff)

        if timediff >= 59999:
            self.sma_lasttime[length] = timeSinceEpoch

            if length not in self.sma_values:
                self.sma_values[length] = []

            if len(self.sma_values[length]) < length:
                    print(f"Adding {input} to  {self.sma_values[length]}")
                    self.sma_values[length].append(input)
                    print(f"Added {input} to  {self.sma_values[length]}")
                    return 
            else:
                self.sma_values[length].pop(0)
                self.sma_values[length].append(input)
                print("Values to be averaged: ",self.sma_values[length])
                return sum(self.sma_values[length])/length
        else:
            return
        
    # Hourly SimpleMovingAverage
    def hourlySMA(self, input, length):
        
        if length not in self.hourlysma_values:
            self.hourlysma_values[length] = []
        


        if len(self.hourlysma_values[length]) < length:
            self.hourlysma_values[length].append(input)
            return 
        else:
            self.hourlysma_values[length].pop(0)
            self.hourlysma_values[length].append(input)
            return sum(self.hourlysma_values[length])/length
        


    # Add cross object.