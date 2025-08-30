

import pandas as pd
import requests
from datetime import timedelta
#from dhanhq import dhanhq
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)

CLIENT_ID = "2508306234"
AKEY = '''eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJwYXJ0bmVySWQiOiIiLCJkaGFuQ2xpZW50SWQiOiIyNTA4MzA2MjM0Iiwid2ViaG9va1VybCI6IiIsImlzcyI6ImRoYW4iLCJleHAiOjE3NTkxMzQ4OTd9.f8LxzXzLnjHrvLEPUVNY0zAkw1A61PaR9iW6DZ3t8JkPLjywJCKfdE7z9qTBXa_SwYBKydk136MPwMcJw9wsqg'''
URL = "https://sandbox.dhan.co/v2/charts/intraday"


securityId_map = {
    '13':'Nifty',
}
def dowload_eod_ohlc(securityId,exchangeSegment,instrument, interval,fromDate, toDate ):
    headers = {
    "access-token": AKEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
        }
    payload = {
        "securityId": str(securityId),
        "exchangeSegment": exchangeSegment,
        "instrument": instrument,
        "interval": str(interval),
        "fromDate": fromDate,
        "toDate": toDate
        }
    try:
        response = requests.post(URL, json=payload, headers=headers)
        json_res = response.json()
        df = pd.DataFrame(json_res)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit = 's')
        df['timestamp'] = df['timestamp'] + timedelta(hours=5, minutes=30)
        df['date'] = df['timestamp'].dt.date
        df['securityId'] = securityId_map[securityId]
    except:
        df = pd.DataFrame(columns=['open','high','low','close','volume','timestamp','open_interest','date','securityId'])
        
    return df


def find_longest_streak_indices(arr):
    """
    Finds the longest streak in an array of 1, 0, and -1.
    """
    max_streak_length = 0
    max_streak_start_index = None
    max_streak_end_index = None
    current_streak_length = 0
    current_streak_start_index = None
    in_streak = False
    # Enumerate allows us to iterate through the array with both the index and the value
    for i, element in enumerate(arr):
        # Condition to start a new streak
        if not in_streak and element == 1:
            in_streak = True
            current_streak_length = 1
            current_streak_start_index = i
        # Condition to continue the current streak
        elif in_streak and element != -1:
            current_streak_length += 1
        # Condition to end the current streak
        elif in_streak and element == -1:
            current_streak_length += 1
            # Check if this completed streak is the new longest
            if current_streak_length > max_streak_length:
                max_streak_length = current_streak_length
                max_streak_start_index = current_streak_start_index
                max_streak_end_index = i
            # Reset for the next potential streak
            in_streak = False
            current_streak_length = 0
    return max_streak_length, max_streak_start_index, max_streak_end_index

def run(dt):
    dt_str = dt.strftime('%Y-%m-%d')
    df_orig =  dowload_eod_ohlc("13","IDX_I","INDEX","1",dt_str,dt_str)
    df = df_orig
    df['ema_f'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_s'] = df['close'].ewm(span=20, adjust=False).mean()
    df['is_bullish'] = df['ema_f'] > df['ema_s']
    df['is_bearish'] = df['ema_f'] < df['ema_s']
    thresh_up = 3 #(atleast check 3 consecutive ticks)

    conf_bullish = df['is_bullish'].rolling(window=thresh_up).sum()

    df['signal'] = 0
    df.loc[conf_bullish == thresh_up, 'signal'] =  1
    df.loc[df['is_bearish'], 'signal'] = -1

    a, b, c = find_longest_streak_indices(df.signal)
    if b is None:
        return pd.DataFrame()
    else:
        return df[df.index.isin([b,c]) ]