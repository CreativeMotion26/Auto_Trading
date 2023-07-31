# Claculate target price
import pandas as pd
import requests
import math
import ai


myToken = "Your_slack_token"

# Alter meassage from Slack 
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )


# checkin balance
def cal_amount(usdt_balance, cur_price):
    protion = 1 #Proportion 10%
    usdt_trade = usdt_balance * protion
    amount = math.floor((usdt_trade*1000000) / cur_price) / 1000000
    return amount

symbol = "BTC/USDT"

def cal_target(exchange,symbol):
    # Get ohlcv from exchanges
    data = exchange.fetch_ohlcv(
        symbol =symbol,
        timeframe='1d',
        since=None,
        limit=10
    ) 
    
    # chage ohlcv to dataframe object
    df = pd.DataFrame(
        data=data,
        columns=['datetime','open','high','low','close','volume']
    )
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime',inplace=True)

    
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    
    long_target = today['open'] + (yesterday['high'] - yesterday['low'])*0.7
    short_target = today['open'] - (yesterday['high'] - yesterday['low'])*0.5
    return (long_target, short_target) #tuple


def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position):
    if cur_price > long_target and ai.predicted_close_price > cur_price: # long position
        position['type'] = 'long'
        position['amount'] = amount
        exchange.create_market_buy_order(symbol=symbol, amount = amount)
        post_message(myToken,"#autotrading","get long position")
    
    elif cur_price < short_target and ai.predicted_close_price > cur_price: # short position 
        position['type'] = 'short'
        position['amount'] = amount
        exchange.create_market_sel_order(symbol=symbol, amount = amount)
        post_message(myToken,"#autotrading","get Short position")

def exit_postion(exchange, symbol,  position):
    amount = position['amount']
    if position['type'] == 'long':
        exchange.create_market_sel_order(symbol=symbol, amount = amount)
        post_message(myToken,"#autotrading","exit long position")
        position['type'] == None
    elif position['type'] == 'short':
        exchange.create_market_buy_order(symbol=symbol, amount = amount)
        post_message(myToken,"#autotrading","exit short position")
        position['type'] == None


 
