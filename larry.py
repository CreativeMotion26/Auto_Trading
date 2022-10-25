# 목표가 계산 price
import pandas as pd
import requests
import math
import ai


myToken = "xoxb-4263756875586-4249588574535-MvoQsiuBPzU1DLFQfql7Agby"

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
    #  거래소에서 symbol에 대한  ohlcv 일봉을 얻기
    data = exchange.fetch_ohlcv(
        symbol =symbol,
        timeframe='1d',
        since=None,
        limit=10
    ) 
    
    # 일봉 데이터를 데이터프레임 객체로 변환
    df = pd.DataFrame(
        data=data,
        columns=['datetime','open','high','low','close','volume']
    )
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime',inplace=True)

    # 일봉 데이터를 데이터 프레임 객체로 전환
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


 
