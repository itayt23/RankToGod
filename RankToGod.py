from ranker import Ranker
import time
from window import Layout
import PySimpleGUI as sg
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup


working_sentiment = False
working_technical = False
working_valuations = False
start_time = None
name = str(time.ctime().replace('"',"").replace(':',".").replace('?',"").replace('\\',"").replace('/',"").replace('<',"").replace('>',"").replace('*',"").replace('|',""))
layout = Layout()
window = layout.setWindow(layout.getMainLayout())

def run_valuations(file_path, stock_interval):
    global  window, name, working_valuations,start_time
    start_time = time.time()
    window["-PROG-"].UpdateBar(0)
    if not working_valuations:
        working_valuations = True
        print('Starting...')
        ranker = Ranker(file_path, stock_interval)
        window.perform_long_operation(lambda: get_valuations(ranker), '-OPERATION DONE-')
    else: sg.popup_quick_message("Running right now\nPlease wait until finish running the program",auto_close_duration=5)

def run_ranking(file_path, stock_interval):
    global window, name, working_sentiment,working_technical,text,start_time
    start_time = time.time()
    window["-PROG-"].UpdateBar(0)
    text = window["-OUT1-"].Widget
    text.tag_config("Fundamental", foreground="orange")
    text.tag_config("technical", foreground="cyan")
    text.tag_config("warning",background="yellow", foreground="red")
    if not working_sentiment and not working_technical:
        working_sentiment = True
        working_technical = True
        print('Starting...')
        ranker = Ranker(file_path, stock_interval)
        window.perform_long_operation(lambda: run_sentiment(ranker), '-OPERATION DONE-')
        window.perform_long_operation(lambda: run_technical(ranker), '-OPERATION DONE-')
        window.perform_long_operation(lambda: final_merge(ranker), '-OPERATION DONE-')
    else: sg.popup_quick_message("Running right now\nPlease wait until finish running the program",auto_close_duration=5)

def get_valuations(ranker:Ranker):
    global window, name, working_valuations
    column_check = 'P/E'
    file_first_name = 'Value'
    stocks_df = ranker.getDataFrame()
    df_size = stocks_df.shape
    df_size = df_size[0]
    prog_jump = 1000/df_size
    if(prog_jump < 1): prog_jump = 1
    bar_update = prog_jump
    try:
        for index, stock in enumerate(stocks_df['Symbol']):
            ranker.run_valuations(stock, index)
            window["-PROG-"].UpdateBar(bar_update)
            bar_update = bar_update + prog_jump
            print(f"Finish {index+1} Symbol")
    except Exception as e:
        print('Problem accured during scarp: '+str(e))
        print(f'the data was export to excel, scarp was stop at symbol No.{index}')
    working_valuations = False
    window["-PROG-"].UpdateBar(1000)
    results_scrap_path = Path.cwd() / 'results'
    if not results_scrap_path.exists():
        results_scrap_path.mkdir(parents=True)
    file_name = file_first_name + "_" + name+".xlsx"
    ranker.getDataFrame().to_excel(results_scrap_path / file_name)
    if(not pd.isna(stocks_df.iloc[df_size-1][column_check])): print("Valuation app was finish successfully! =)")
    print(f"Total runtime of the program is {round((time.time() - start_time)/60, 2)} minutes")

def run_sentiment(ranker:Ranker):
    global window, working_sentiment
    stocks_df = ranker.getDataFrame()
    df_size = stocks_df.shape
    df_size = df_size[0]
    prog_jump = 1000/df_size
    if(prog_jump < 1): prog_jump = 1
    bar_update = prog_jump
    try:
        for index, stock in enumerate(stocks_df['Symbol']):
            ranker.run_sentiment_rank(stock, index)
            window["-PROG-"].UpdateBar(bar_update)
            bar_update = bar_update + prog_jump
            text.insert("end",f"Finish Fundamental {index+1} Symbol\n", "Fundamental")
    except Exception as e:
        text.insert("end",'Problem Accured During Fundamental Analysis: '+str(e)+"\n", "warning")
    working_sentiment = False
    window["-PROG-"].UpdateBar(1000)
    text.insert("end","Fundamental Analysis Was Finish Successfully!\n", "Fundamental")

def run_technical(ranker:Ranker):
    global working_technical, window, text
    stocks_df = ranker.getDataFrame()
    try:
        for index, stock in enumerate(stocks_df['Symbol']):
            ranker.run_technical(stock, index)
            text.insert("end",f"Finish Technical {index+1} Symbol\n", "technical")
    except Exception as e:
        text.insert("end",'Problem Accured During Technical Analysis - ChartToGod: '+str(e)+"\n", "warning")
    working_technical = False
    text.insert("end","Technical Analysis - ChartToGod Was Finish Successfully!\n", "technical")

def final_merge(ranker:Ranker):
    global name, working_technical, working_sentiment
    while(working_technical or working_sentiment):
        time.sleep(2)
    results_scrap_path = Path.cwd() / 'results'
    if not results_scrap_path.exists():
        results_scrap_path.mkdir(parents=True)
    file_name = "RankToGod" + "_" + name+".xlsx"
    ranker.getDataFrame().to_excel(results_scrap_path / file_name)
    print("RankToGod Was Finish Successfully! =)")
    print(f"Total Runtime of The Program is {round((time.time() - start_time)/60, 2)} minutes")

def process_user_input():
    global window, name
   
    event, values = window.read()
    while not (event == sg.WIN_CLOSED or event=="Exit"):
        if event == "Submit":
            file_path = values["-FILE-"]
            stock_interval = values["-INTERVAL_NAME-"]
            if(stock_interval == 'Valuations'): run_valuations(file_path, stock_interval)
            else: run_ranking(file_path, stock_interval)
        event, values = window.read()
    window.close()

if __name__ == '__main__':
    process_user_input()
    # symbols = ['MSFT','NVDA']
    # for sym in symbols:
    #     pass
        