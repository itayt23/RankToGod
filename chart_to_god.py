from sre_constants import SUCCESS
from PySimpleGUI.PySimpleGUI import WINDOW_CLOSE_ATTEMPTED_EVENT
from datetime import date
import time
from window import Layout
import PySimpleGUI as sg
from pathlib import Path
import pandas as pd
from sequencing import SequenceMethodSymbol,SequenceMethod
import yfinance as yf
import ta
import numpy as np
from datetime import datetime, timedelta

done = False
working = False
start_time = time.time()
name = str(time.ctime().replace('"',"").replace(':',".").replace('?',"").replace('\\',"").replace('/',"").replace('<',"").replace('>',"").replace('*',"").replace('|',""))
layout = Layout()
window = layout.setWindow(layout.getMainLayout())



def run_technical(symbol,index):
    final_score = seq_score_monthly = seq_score_weekly = rsi_score_monthly = rsi_score_weekly = ma_score_monthly = ma_score_weekly = tense_score_weekly = tense_score_monthly = 0
    today = date.today()
    try:
        if(symbol == 'BRK.B'): symbol = 'BRK-B'
        if(symbol == 'BRK.A'): symbol = 'BRK-A'
        if(symbol == 'BF.B'): symbol = 'BF-B'
        if(symbol == 'BF.A'): symbol = 'BF-A'
        data_monthly = pd.DataFrame(yf.download(tickers=symbol, period='5y',interval='1mo',progress=False)).dropna()
        data_weekly = pd.DataFrame(yf.download(tickers=symbol, period='5y',interval='1wk',progress=False)).dropna()
        seq_monthly = SequenceMethod(data_monthly,'monthly',today)
        seq_weekly = SequenceMethod(data_weekly,'weekly',today)
        data_monthly['RSI14'] = ta.momentum.RSIIndicator(data_monthly['Close'], window=14).rsi()
        data_weekly['RSI14'] = ta.momentum.RSIIndicator(data_weekly['Close'], window=14).rsi()
        data_monthly['SMA13'] = data_monthly['Close'].rolling(window=13).mean()
        data_monthly['SMA5'] = data_monthly['SMA13'].rolling(window=5).mean()
        data_weekly['SMA13'] = data_weekly['Close'].rolling(window=13).mean()
        data_weekly['SMA5'] = data_weekly['SMA13'].rolling(window=5).mean()
        seq_score_monthly = seqence_compute_monthly(seq_monthly)
        seq_score_weekly = seqence_compute_weekly(seq_weekly)
        rsi_score_monthly = rsi_compute_monthly(data_monthly)
        rsi_score_weekly = rsi_compute_weekly(data_weekly)
        ma_score_monthly = is_moving_away_monthly(data_monthly)
        ma_score_weekly = is_moving_away_weekly(data_weekly)
        tense_score_monthly = tense_compute_monthly(data_monthly,seq_monthly)
        tense_score_weekly = tense_compute_weekly(data_weekly,seq_weekly)
        final_score = seq_score_monthly + seq_score_weekly + rsi_score_monthly + rsi_score_weekly + ma_score_monthly + ma_score_weekly + tense_score_monthly + tense_score_weekly
        return final_score
    except Exception as e:
        print('Problem Accured During Technical Analysis - ChartToGod: '+str(e))
        print(f'Analysis Run Into A Problem At Symbol - {symbol}, No.{index}')
        return final_score

def excel_reader(file_path):
    try:
        symbol_pd = pd.DataFrame()
        stocks_df = pd.DataFrame()
        if(".xlsx" in file_path or '.xls' in file_path):
            symbol_pd = pd.read_excel(file_path)
        elif '.csv' in file_path:
            symbol_pd = pd.read_csv(file_path, encoding = 'cp1255')
        else:
            print("Problem with reading file")
            return
        symbol_np = symbol_pd['symbol'].to_numpy()
        symbol_arr = fixingArray(symbol_np)
        stocks_df['Symbol'] = symbol_arr
        return stocks_df
    except Exception as e:
        print(f'problem with reading excel file! {str(e)}')
        print('check again the column name, it should be "symbol"')

def fixingArray(arr):
    temp_arr = []
    final_arr = []
    for i in arr:
        symbol = i.split()
        temp_arr.append(symbol[0])
    for i in temp_arr:
        if i not in final_arr:
            final_arr.append(i)
    return final_arr

def rank(final_score,index):
    pass

def seqence_compute_monthly(sequence:SequenceMethod):
    if(sequence.get_last_sequence() == 1): return 0.15
    return 0

def seqence_compute_weekly(sequence:SequenceMethod):
    if(sequence.get_last_sequence() == 1): return 0.15
    return 0

def rsi_compute_monthly(data_monthly:pd.DataFrame):
    if(data_monthly['RSI14'].iloc[-1] > 50): return 0.2
    return 0

def rsi_compute_weekly(data_weekly:pd.DataFrame):
    check = data_weekly['RSI14'].iloc[-1]
    if(data_weekly['RSI14'].iloc[-1] > 50): return 0.2
    return 0

def is_moving_away_monthly(data_monthly:pd.DataFrame):
    ma_score = 0
    if(data_monthly['SMA13'].iloc[-1] > data_monthly['SMA5'].iloc[-1]):
        ma_score = 0.075
        slope_monthly_sma13 = round((data_monthly['SMA13'].iloc[-1] - data_monthly['SMA13'].iloc[-2]),2)
        slope_monthly_sma5 = round((data_monthly['SMA5'].iloc[-1] - data_monthly['SMA5'].iloc[-2]),2)
        if(slope_monthly_sma13 >= slope_monthly_sma5): ma_score = ma_score + 0.075
    return ma_score
    
def is_moving_away_weekly(data_weekly:pd.DataFrame):
    ma_score = 0
    if(data_weekly['SMA13'].iloc[-1] > data_weekly['SMA5'].iloc[-1]):
        ma_score = 0.075
        slope_weekly_sma13 = round((data_weekly['SMA13'].iloc[-1] - data_weekly['SMA13'].iloc[-2]),2)
        slope_weekly_sma5 = round((data_weekly['SMA5'].iloc[-1] - data_weekly['SMA5'].iloc[-2]),2)
        if(slope_weekly_sma13 >= slope_weekly_sma5): ma_score = ma_score + 0.075
        return ma_score
    return ma_score


def tense_compute_monthly(data_monthly:pd.DataFrame,sequence:SequenceMethod):
    tense_score_monthly = 0
    consec_counter = 0
    count_candles = sequence.get_last_number_of_seq_candels()
    if(np.isnan(count_candles)): count_candles = 1
    else: count_candles = count_candles + 1
    if(sequence.get_last_sequence() == 1):
        if(count_candles >= 19):
            tense_score_monthly = tense_score_monthly - 0.1
        if(count_candles >= 24):
            tense_score_monthly = tense_score_monthly - 0.1
    week_day = date.today().weekday()
    if(check_end_of_month(data_monthly)): consec_green = data_monthly[['Close','Open']].tail(10)
    else: consec_green = data_monthly[['Close','Open']].tail(11).head(10)
    for i in range(len(consec_green)-1, 0, -1):
        curr_close = round(consec_green.iloc[i]['Close'],2)
        prev_close = round(consec_green.iloc[i-1]['Close'],2)
        if curr_close >= prev_close * 1.01:
            consec_counter = consec_counter + 1
        else:
            break
    if(consec_counter >= 3):
        tense_score_monthly = tense_score_monthly - 0.1
    if(consec_counter >= 4):
        tense_score_monthly = tense_score_monthly - 0.1
    if(consec_counter >= 5):
        tense_score_monthly = tense_score_monthly - 0.1
    if(tense_score_monthly < -0.4): tense_score_monthly = -0.4
    return tense_score_monthly
    
def check_end_of_month(data:pd.DataFrame):
    last_date = data.index[-1].date()
    today = date.today()
    if last_date.month != today.month:
        return True
    else:
        if today.weekday() in [5,6]:
            if today.weekday() == 6: start_week = today + timedelta(days=1)
            if today.weekday() == 5: start_week = today + timedelta(days=2)
            if start_week.month != last_date.month:
                return True
    return False
    


def tense_compute_weekly(data_weekly:pd.DataFrame,sequence:SequenceMethod):
    tense_score_weekly = 0
    consec_counter = 0
    count_candles = sequence.get_last_number_of_seq_candels()
    if(np.isnan(count_candles)): count_candles = 1
    else: count_candles = count_candles + 1
    if(sequence.get_last_sequence() == 1):
        if(count_candles >= 8):
            tense_score_weekly = tense_score_weekly - 0.05
        if(count_candles >= 11):
            tense_score_weekly = tense_score_weekly - 0.05
    week_day = date.today().weekday()
    if(week_day in [5,6]): consec_green = data_weekly[['Close','Open']].tail(10)
    else: consec_green = data_weekly[['Close','Open']].tail(11).head(10)
    for i in range(len(consec_green)-1, 0, -1):
        curr_close = round(consec_green.iloc[i]['Close'],2)
        prev_close = round(consec_green.iloc[i-1]['Close'],2)
        if curr_close > prev_close:
            consec_counter = consec_counter + 1
        else:
            break
    if(consec_counter >= 4):
        tense_score_weekly = tense_score_weekly - 0.1
    if(consec_counter >= 7):
        tense_score_weekly = tense_score_weekly - 0.05
    if(consec_counter >= 9):
        tense_score_weekly = tense_score_weekly - 0.05
    # if(tense_score_weekly < -0.2): tense_score_weekly = -0.2
    return tense_score_weekly
    
   
def calculate_rsi(data:pd.DataFrame,interval=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=14).mean()
    avg_loss = loss.ewm(span=14).mean()
    rs = avg_gain / avg_loss
    rsi14 = 100 - (100 / (1 + rs))
    return rsi14
