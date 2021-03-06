from sre_constants import SUCCESS
from PySimpleGUI.PySimpleGUI import WINDOW_CLOSE_ATTEMPTED_EVENT
from scrapper import ClientsScraper
from datetime import date
import time
from window import Layout
import PySimpleGUI as sg
from pathlib import Path

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
        window["-PROG-"].UpdateBar(1)
        scrapper = ClientsScraper(file_path, stock_interval)
        window.perform_long_operation(lambda: run(scrapper), '-OPERATION DONE-')
    else: sg.popup_quick_message("Running other program right now\nPlease wait until finish running the program",auto_close_duration=5)


def run(scrapper):
    global done, window, name, working
    stocks_df = scrapper.getDataFrame()
    df_size = stocks_df.shape
    df_size = df_size[0]
    prog_jump = 1000/df_size
    if(prog_jump < 1): prog_jump = 1
    try:
        for index, stock in enumerate(stocks_df['Symbol']):
            scrapper.scrap(stock, index)
            print(f"Finish {index+1} Symbol")
            window["-PROG-"].UpdateBar(prog_jump)
    except Exception as e:
        print('Problem accured during scarp: '+str(e))
        print(f'the data was export to excel, scarp was stop at symbol No.{index}')
    if(not stocks_df['Final Score'].empty): done = True
    working = False
    window["-PROG-"].UpdateBar(1000)
    if(done):
        results_scrap_path = Path.cwd() / 'results'
        if not results_scrap_path.exists():
            results_scrap_path.mkdir(parents=True)
        file_name = "Rank" +name+".xlsx"
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
