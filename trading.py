from curses import BUTTON1_TRIPLE_CLICKED
from symtable import Symbol
from email import header
import pandas as pd
import datetime
import requests
import larry
import ccxt 
import time
import ai

#binance objects
binance = ccxt.binance(config={
    'apiKey': "your_api_key",
    'secret': "your_secert_key",
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

myToken = "your slack token"

# Alter meassage from Slack 
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )


# Target price
symbol = "BTC/USDT"
long_target, short_target = larry.cal_target(binance,symbol)


# Balance
balance = binance.fetch_balance()
usdt = balance['total']['USDT']
btc = binance.fetch_ticker(symbol=symbol)
cur_price = btc['last']

# Amount
amount = larry.cal_amount(usdt, cur_price)
print("Available amount: ",amount)

print ("Predicted Price",ai.predicted_close_price)

position = {
    "type": None,
    "amount": 0
}

op_mode = False 

# Time line 
# Updatig target price 
post_message(myToken,"#autotrading","Auto_trade start")

while True:
 #time
  try:  
        now = datetime.datetime.now()

        # change position
        if now.hour == 8 and now.minute == 50 and (0 <=now.second < 10):
            if op_mode and position['type'] is None:
                larry.exit_postion(binance,symbol ,position)
                op_mode = False

        #Change Target price (09:00:20 ~ 09:00:30)
        if now.hour == 9 and now.minute == 0 and (20 <=now.second < 30):
            long_target, short_target = larry.cal_target(binance,symbol)
            balance = binance.fetch_balance()
            usdt = balance['total']['USDT']
            post_message(myToken,"#autotrading","changed Traget Price")
            post_message(myToken,"#autotrading",l)
            post_message(myToken,"#autotrading",s)
            post_message(myToken,"#autotrading",usdt)
            op_mode = True
            time.sleep(10)

        #currnet amount to buy ( 10% in your balance )
        btc = binance.fetch_ticker(symbol=symbol)
        cur_price = btc['last']
        amount = larry.cal_amount(usdt, cur_price)

        if op_mode and position['type'] is None:
            larry.enter_position(binance, symbol, cur_price, long_target, short_target, amount, position)
        
        l = ("long target", long_target)
        s = ("short target", short_target)
        print(now, cur_price, l, s)
        time.sleep(1) 
   
  except Exception as e:
       print(e)
       post_message(myToken,"#autotrading",e)
       time.sleep(1)
