from sre_constants import SUCCESS
from PySimpleGUI.PySimpleGUI import WINDOW_CLOSE_ATTEMPTED_EVENT
from scrapper import ClientsScraper
from datetime import date
import time
from window import Layout
import PySimpleGUI as sg
from pathlib import Path

done = False
def run(scrapper):
    global done
    stocks_df = scrapper.getDataFrame()
    try:
        for index, stock in enumerate(stocks_df['Symbol']):
            scrapper.scrap(stock, index)
            print(f"Finish {index+1} Symbol")
    except Exception as e:
        print('Problem accured during scarp: '+str(e))
        print(f'the data was export to excel, scarp was stop at symbol No.{index}')
    if(not stocks_df['Final Score'].empty): done = True


def process_user_input():
    global done
    start_time = time.time()
    name = str(time.ctime().replace('"',"").replace(':',".").replace('?',"").replace('\\',"").replace('/',"").replace('<',"").replace('>',"").replace('*',"").replace('|',""))
    layout = Layout()
    window = layout.setWindow(layout.getMainLayout())
    event, values = window.read()
    while not (event == sg.WIN_CLOSED or event=="Exit"):
        if event == "Submit":
            window["-PROG-"].UpdateBar(1)
            file_path = values["-FILE-"]
            stock_interval = values["-INTERVAL_NAME-"]
            scrapper = ClientsScraper(file_path, stock_interval)
            run(scrapper)
            window["-PROG-"].UpdateBar(2)
            if(done):
                #results_scrap_path = Path('..','results')
                results_scrap_path = Path.cwd() / 'results'
                if not results_scrap_path.exists():
                    results_scrap_path.mkdir(parents=True)
                file_name = "Rank" +name+".xlsx"
                scrapper.getDataFrame().to_excel(results_scrap_path / file_name)
                print("Scrap was finish successfully! =)")
            print(f"Total runtime of the program is {round((time.time() - start_time)/60, 2)} minutes")
        event, values = window.read()
    window.close()

if __name__ == '__main__':
    process_user_input()
