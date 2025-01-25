class Indicators:
    def __init__(self):
        self.sma_values = {}
        self.sma_minutetime = []
        self.hourlysma_values = {}
        self.timeElapsed = 0

    # Simple Moving Average
    def SMA(self, input, length, timeSinceEpoch):
        
        # if there are less than 2 entries
        if len(self.sma_minutetime) <= 1: 
            # add entry to time list and return since there
            # is no way to validate that a minute has passed
            self.sma_minutetime.append(timeSinceEpoch)
            return
        elif len(self.sma_minutetime) == 2:
            self.sma_minutetime.pop(0)
            self.sma_minutetime.append(timeSinceEpoch)

        self.timeElapsed = self.sma_minutetime[1] - self.sma_minutetime[0]

        if length not in self.sma_values and self.timeElapsed > 59999:
            self.sma_values[length] = []
            
        if len(self.sma_values[length]) < length:
            self.sma_values[length].append(input)
            return 
        else:
            self.sma_values[length].pop(0)
            self.sma_values[length].append(input)
            return sum(self.sma_values[length])/length

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