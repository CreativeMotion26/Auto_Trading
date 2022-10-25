
from gettext import bind_textdomain_codeset
from matplotlib.pyplot import close
from prophet import Prophet
import pandas as pd
import schedule
import ccxt


predicted_close_price = 0
def predict_price(ticker):
    global predicted_close_price
    binance = ccxt.binance()
    btc_ohlcv = binance.fetch_ohlcv("BTC/USDT",timeframe='1h')
    type(btc_ohlcv)
    df = pd.DataFrame(btc_ohlcv,columns=['datetime','open','high','low','close','volume'])
    df['datetime'] = pd.to_datetime(df['datetime'],unit='ms')
    df.set_index('datetime',inplace=True)
        
    df = df.reset_index()
    df['ds'] = df['datetime']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue

predict_price("BTC/USDT")
schedule.every().hour.do(lambda: predict_price("BTC/USDT"))
