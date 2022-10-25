import ccxt
import numpy as np
import pandas as pd

# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터

#df = pyupbit.get_ohlcv("USDT-BTC", count=14)
symbol = "BTC/USDT"
binance = ccxt.binance()
btc_ohlcv = binance.fetch_ohlcv("BTC/USDT",'1d')


df = pd.DataFrame(btc_ohlcv,columns=['datetime','open','high','low','close','volume'])
df['datetime'] = pd.to_datetime(df['datetime'],unit='ms')
df.set_index('datetime',inplace=True)


# 변동폭 * k 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.9

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] + df['range'].shift(1)

# ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)


# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

#MDD 계산
print("MDD(%): ", df['dd'].max())

#export as an exel file
df.to_excel("dd.xlsx")