'''This is ready verison of trading algorithm '''


import datetime
import pandas as pd
from ib_insync import *
import pytz
import time

time.sleep(120)
# Set pandas display option
pd.set_option('display.max_columns', None)

# Define timezone
eastern_tz = pytz.timezone('US/Eastern')

# Initialize IB
ib = IB()

def connect_to_ib():
    ib.connect('127.0.0.1', 7497, clientId=1)

def disconnect_from_ib():
    ib.disconnect()

def get_forex_contract(symbol, currency):
    return Forex(symbol, currency=currency)

def fetch_historical_data(contract, duration, bar_size):
    """Fetch historical data for the given contract."""
    return ib.reqHistoricalData(contract, endDateTime='', durationStr=duration,
                                barSizeSetting=bar_size, whatToShow='MIDPOINT', useRTH=True)

def calculate_sma(data, period):
    """Calculate Simple Moving Average."""
    return data['close'].rolling(window=period).mean()

def place_order(contract, quantity, action):
    """Place an order."""
    order = MarketOrder(action, quantity)

    trade = ib.placeOrder(contract, order)
    return trade

                
def main():
    try:
        if (datetime.datetime.now().weekday() in range(0,5)) and (datetime.datetime.now(eastern_tz).time()>datetime.time(4,0)) and (datetime.datetime.now(eastern_tz).time()<datetime.time(15, 30)):

            connect_to_ib()
            contract = get_forex_contract('USDJPY', 'JPY')
            ib.qualifyContracts(contract)

            # SMA periods
            short_sma_period = 11
            long_sma_period =117
            quantity = 1000

            i = 0
            ff = 0
            while (datetime.datetime.now().weekday() in range(0,5)) and (datetime.datetime.now(eastern_tz).time()>datetime.time(4,0)) and (datetime.datetime.now(eastern_tz).time()<datetime.time(15, 30)):
                print(i)
                i += 1

                # Fetch historical data (e.g., last 24 hours with 1-hour bars)
                bars = fetch_historical_data(contract, '3600 S', '5 secs')
                df = util.df(bars)

                # Calculate SMAs
                df['short_sma'] = calculate_sma(df, short_sma_period)
                df['long_sma'] = calculate_sma(df, long_sma_period)

                # Determine trade action
                if df['short_sma'].iloc[-2] < df['long_sma'].iloc[-2] and df['short_sma'].iloc[-1] > df['long_sma'].iloc[-1]:
                    print("Buy Signal")
                    # close_opposite_positions(contract, 'SELL')
                    if ff < 0:
                        place_order(contract, abs(ff), 'BUY')
                        ff = 0
                    
                    place_order(contract, quantity, 'BUY')
                    ff += quantity
                elif df['short_sma'].iloc[-2] > df['long_sma'].iloc[-2] and df['short_sma'].iloc[-1] < df['long_sma'].iloc[-1]:
                    print("Sell Signal")
                    if ff > 0:
                        place_order(contract, abs(ff), 'SELL')
                        ff = 0

                    place_order(contract, quantity, 'SELL')
                    ff += -quantity


                ib.sleep(5)  
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            if ff > 0:
                place_order(contract, abs(ff), 'SELL')
            if ff < 0:
                place_order(contract, abs(ff), 'BUY')
        except: pass


        disconnect_from_ib()

if __name__ == "__main__":
    try:
        main()
    except:
        time.sleep(120)
        main()
        
