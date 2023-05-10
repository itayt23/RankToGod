from scrapper import ClientsScraper
import time
from window import Layout
import PySimpleGUI as sg
from pathlib import Path
import pandas as pd

done = False
working = False
start_time = time.time()
name = str(time.ctime().replace('"',"").replace(':',".").replace('?',"").replace('\\',"").replace('/',"").replace('<',"").replace('>',"").replace('*',"").replace('|',""))
layout = Layout()
window = layout.setWindow(layout.getMainLayout())

def run_ranking(file_path, stock_interval):
    global done, window, name, working
    if not working:
        working = True
        print('Starting...')
        scrapper = ClientsScraper(file_path, stock_interval)
        window.perform_long_operation(lambda: run(scrapper), '-OPERATION DONE-')
    else: sg.popup_quick_message("Scrapping right now\nPlease wait until finish running the program",auto_close_duration=5)

def run(scrapper:ClientsScraper):
    global done, window, name, working
    if(scrapper.get_scrap_type() == 'Sentiment Rank'):
        column_check = 'Final Score'
        file_first_name = 'Rank'
    elif(scrapper.get_scrap_type() == 'Valuations'):
        column_check = 'P/E'
        file_first_name = 'Values'
    stocks_df = scrapper.getDataFrame()
    df_size = stocks_df.shape
    df_size = df_size[0]
    prog_jump = 1000/df_size
    if(prog_jump < 1): prog_jump = 1
    bar_update = prog_jump
    try:
        for index, stock in enumerate(stocks_df['Symbol']):
            scrapper.scrap(stock, index)
            window["-PROG-"].UpdateBar(bar_update)
            bar_update = bar_update + prog_jump
            print(f"Finish {index+1} Symbol")
    except Exception as e:
        print('Problem accured during scarp: '+str(e))
        print(f'the data was export to excel, scarp was stop at symbol No.{index}')
    if(not pd.isna(stocks_df.iloc[df_size-1][column_check])): done = True
    working = False
    window["-PROG-"].UpdateBar(1000)
    if(done or scrapper.get_scrap_type() == 'Valuations'):
        results_scrap_path = Path.cwd() / 'results'
        if not results_scrap_path.exists():
            results_scrap_path.mkdir(parents=True)
        file_name = file_first_name + "_" + name+".xlsx"
        scrapper.getDataFrame().to_excel(results_scrap_path / file_name)
        print("Scrap was finish successfully! =)")
    print(f"Total runtime of the program is {round((time.time() - start_time)/60, 2)} minutes")



def process_user_input():
    global done, window, name
   
    event, values = window.read()
    while not (event == sg.WIN_CLOSED or event=="Exit"):
        if event == "Submit":
            file_path = values["-FILE-"]
            stock_interval = values["-INTERVAL_NAME-"]
            run_ranking(file_path, stock_interval)
        event, values = window.read()
    window.close()

if __name__ == '__main__':
    process_user_input()
