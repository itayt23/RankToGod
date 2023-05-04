import PySimpleGUI as sg

class Layout:
    def __init__(self):
        sg.theme("DarkBrown4") 

        self.layout_main = [[sg.T("")],
        [sg.Text("Please Enter Rank Interval: "), sg.Combo(key="-INTERVAL_NAME-" ,values=["Sentiment Rank",'Valuations'], default_value="Sentiment Rank")],
        [sg.Text("Choose a File: "), sg.Input(key="-IN2-" ,change_submits=True), sg.FileBrowse(key="-FILE-", file_types=(("Excel Files", "*.xlsx"),("Excel Files", "*.xls"),("CSV Files", "*.csv")))],
        [sg.Button("Submit")],
        [sg.T("")],
        [sg.Text("Progress: "), sg.ProgressBar(max_value=1000, orientation='h', size=(30,20), key="-PROG-",bar_color="gray")],
        [sg.Output(key='-OUT1-', size=(100, 8))],
        [sg.Button("Exit",size=(8,1),button_color=('red','white'))]]          

    def getMainLayout(self):
        return self.layout_main
    
    def setWindow(self, layout):
        return sg.Window('Rank To God',layout, size=(750,350),element_justification='c')
    