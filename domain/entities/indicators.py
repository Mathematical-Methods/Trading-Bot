import datetime
import math

class Indicators:
    def __init__(self):
        self.current_hour = {}
        self.accum_volume = {}
        self.last_close = {}
        self.hourly_data = {}
        self.indicators = {}
        self.ema_values = {}

    def update_minute_data(self, symbol, close, volume, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        hour_start = dt.replace(minute=0, second=0, microsecond=0)
        if symbol not in self.current_hour or self.current_hour[symbol] != hour_start:
            if symbol in self.current_hour:
                hourly_close = self.last_close[symbol]
                hourly_volume = self.accum_volume[symbol]
                if symbol not in self.hourly_data:
                    self.hourly_data[symbol] = []
                self.hourly_data[symbol].append((hourly_close, hourly_volume, self.current_hour[symbol]))
                self.calculate_indicators(symbol)
            self.current_hour[symbol] = hour_start
            self.accum_volume[symbol] = volume
            self.last_close[symbol] = close
            return True
        else:
            self.accum_volume[symbol] += volume
            self.last_close[symbol] = close
            return False

    def calculate_indicators(self, symbol):
        if symbol not in self.indicators:
            self.indicators[symbol] = {
                'ma_short_history': [],
                'ma_long_history': [],
                'rsi_history': [],
                'macd_history': [],
                'bollinger_history': [],
                'volume_history': []
            }
        ma_short = self.calculate_SMA(symbol, 10)
        ma_long = self.calculate_SMA(symbol, 20)
        if ma_short is not None and ma_long is not None:
            self.indicators[symbol]['ma_short_history'].append(ma_short)
            self.indicators[symbol]['ma_long_history'].append(ma_long)
            if len(self.indicators[symbol]['ma_short_history']) > 2:
                self.indicators[symbol]['ma_short_history'].pop(0)
                self.indicators[symbol]['ma_long_history'].pop(0)
        rsi = self.calculate_RSI(symbol, 14)
        if rsi is not None:
            self.indicators[symbol]['rsi_history'].append(rsi)
            if len(self.indicators[symbol]['rsi_history']) > 1:
                self.indicators[symbol]['rsi_history'].pop(0)
        macd_line, signal_line = self.calculate_MACD(symbol)
        if macd_line is not None and signal_line is not None:
            self.indicators[symbol]['macd_history'].append((macd_line, signal_line))
            if len(self.indicators[symbol]['macd_history']) > 5:
                self.indicators[symbol]['macd_history'].pop(0)
        bollinger = self.calculate_Bollinger_Bands(symbol, 20, 2)
        if bollinger[0] is not None:
            self.indicators[symbol]['bollinger_history'].append(bollinger)
            if len(self.indicators[symbol]['bollinger_history']) > 1:
                self.indicators[symbol]['bollinger_history'].pop(0)
        hourly_volume = self.hourly_data[symbol][-1][1]
        self.indicators[symbol]['volume_history'].append(hourly_volume)
        if len(self.indicators[symbol]['volume_history']) > 6:
            self.indicators[symbol]['volume_history'].pop(0)

    def calculate_SMA(self, symbol, length):
        if symbol in self.hourly_data and len(self.hourly_data[symbol]) >= length:
            closes = [close for close, _, _ in self.hourly_data[symbol][-length:]]
            return sum(closes) / length
        return None

    def calculate_RSI(self, symbol, length=14):
        if symbol not in self.hourly_data or len(self.hourly_data[symbol]) < length + 1:
            return None
        closes = [close for close, _, _ in self.hourly_data[symbol][-length-1:]]
        gains, losses = [], []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(-change)
        if not gains:
            return 0.0
        if not losses:
            return 100.0
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses) if losses else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_EMA(self, symbol, period):
        alpha = 2 / (period + 1)
        if symbol not in self.ema_values:
            self.ema_values[symbol] = {}
        if period not in self.ema_values[symbol]:
            if len(self.hourly_data[symbol]) >= period:
                closes = [close for close, _, _ in self.hourly_data[symbol][:period]]
                self.ema_values[symbol][period] = sum(closes) / period
            else:
                return None
        prev_ema = self.ema_values[symbol][period]
        new_close = self.hourly_data[symbol][-1][0]
        new_ema = (new_close - prev_ema) * alpha + prev_ema
        self.ema_values[symbol][period] = new_ema
        return new_ema

    def calculate_MACD(self, symbol):
        ema_fast = self.calculate_EMA(symbol, 12)
        ema_slow = self.calculate_EMA(symbol, 26)
        if ema_fast is None or ema_slow is None:
            return None, None
        macd_line = ema_fast - ema_slow
        if 'signal_line' not in self.ema_values[symbol]:
            if len(self.hourly_data[symbol]) >= 35:
                closes = [close for close, _, _ in self.hourly_data[symbol][-35:-9]]
                macd_series = [self.calculate_EMA(symbol, 12) - self.calculate_EMA(symbol, 26) for _ in closes]
                self.ema_values[symbol]['signal_line'] = sum(macd_series) / 9
            else:
                return macd_line, None
        prev_signal = self.ema_values[symbol]['signal_line']
        alpha = 2 / (9 + 1)
        signal_line = (macd_line - prev_signal) * alpha + prev_signal
        self.ema_values[symbol]['signal_line'] = signal_line
        return macd_line, signal_line

    def calculate_Bollinger_Bands(self, symbol, period=20, std_dev=2):
        if symbol not in self.hourly_data or len(self.hourly_data[symbol]) < period:
            return None, None, None
        closes = [close for close, _, _ in self.hourly_data[symbol][-period:]]
        middle_band = sum(closes) / period
        variance = sum((x - middle_band) ** 2 for x in closes) / period
        std = math.sqrt(variance)
        upper_band = middle_band + std_dev * std
        lower_band = middle_band - std_dev * std
        return upper_band, middle_band, lower_band
