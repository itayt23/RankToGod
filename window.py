import PySimpleGUI as sg

class Layout:
    def __init__(self):
        # sg.theme("DarkBlue7") 
        sg.theme("DarkAmber") 

        self.layout_main = [[sg.T("")],
        [sg.Text("Please Enter Rank Interval: ",font=("Comic Sans MS",12)), sg.Combo(key="-INTERVAL_NAME-" ,values=["Sentiment Rank",'Valuations'], default_value="Sentiment Rank",font=("Comic Sans MS",11))],
        [sg.Text("Choose a File: ",font=("Comic Sans MS",12)), sg.Input(key="-IN2-" ,change_submits=True), sg.FileBrowse(key="-FILE-",font=("Comic Sans MS",10), file_types=(("Excel Files", "*.xlsx"),("Excel Files", "*.xls"),("CSV Files", "*.csv")))],
        [sg.Button("Submit",font=("Comic Sans MS",13))],
        [sg.T("")],
        [sg.Text("Progress: ",font=("Comic Sans MS",12)), sg.ProgressBar(max_value=1000, orientation='h', size=(30,20), key="-PROG-",bar_color="gray")],
        [sg.Output(key='-OUT1-', size=(100, 8))],
        [sg.Button("Exit",size=(8,1),button_color=('red','#fdcb52'),font=("Comic Sans MS",13))]]          

    def getMainLayout(self):
        return self.layout_main
    
    def setWindow(self, layout):
        main_window = sg.Window('Rank To God',layout, size=(830,425),element_justification='c')
        version_layout = [
                sg.Text('', size=(85, 1)),  # empty space to push the text to the right
                sg.Text("Version V2.1", font=("Comic Sans MS", 9), justification='right')
            ]
        main_window.add_row(version_layout)
        return main_window
    