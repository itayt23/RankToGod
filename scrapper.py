from typing import final
import pandas as pd
from bs4 import BeautifulSoup
import requests
import subprocess
import p123api
import pandas as pd
from datetime import date
import random
import time
import yfinance as yf
import selenium.webdriver as webdriver
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os


fundamental_score = 0
first_blocked = 0

class ClientsScraper:
    def __init__(self, file_path, stock_interval):
        self.stocks_df = pd.DataFrame(columns=['Symbol','SA wall st','SA authors','SA quant','Zacks','P123','Tip Ranks Score','Technical Score',
                        'Final Score','Sector','Industry'])   
        self.read_file(file_path, stock_interval)
        load_dotenv()

    def getDataFrame(self):
        return self.stocks_df

    def scrap(self, symbol, index):
        global fundamental_score
        fundamental_score = 0
        symbol = str(symbol)
        #page = 'https://www.tipranks.com/stocks/'+symbol+'/stock-analysis'
        page = 'https://www.tipranks.com/'
        # self.tip_scrapper(page, index, symbol)
        self.alpha_scrapper_api(symbol, index)
        self.zacks_scrapper(symbol, index)
        self.portfolio123_scrapper(symbol, index)
        self.portfolio123_technical_scrapper(symbol, index)
        self.stocks_df.loc[index, 'Tip Ranks Score'] = ''
        self.stocks_df.loc[index, 'Final Score'] =f"={fundamental_score}+0.15*I{index+2}+0.1*H{index+2}"
        sector = self.getSector(symbol)
        industry = self.getIndustry(symbol)
        self.stocks_df.loc[index, 'Sector'] = sector
        self.stocks_df.loc[index, 'Industry'] = industry

    def tip_scrapper(self, url, index,symbol):
        global fundamental_score, first_blocked
        blocked = True
        flag_time = False
        headers = agent_maker()
        if((index - first_blocked) % 4 == 0 and index != 0):
            time.sleep(random.uniform(2.5,6))
            first_blocked = index
        try:
            browser = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
            if browser.findAll('title').pop().string in 'Page Not Found :(':
                self.stocks_df.loc[index, 'Tip score'] = 3
                #self.stocks_df.loc[index, 'Tip analyst'] = 3
                fundamental_score += 0.1 * 3
                #fundamental_score += 0.1 * 3
                return
            while(blocked):
                if browser.findAll('title').pop().string in {'Error Page','Security Violation (503)'}:
                    print("Tip ranks blocked you for 2 minutes....Please wait")
                    time.sleep(122)
                    if(flag_time == False):
                        first_blocked = index
                        flag_time = True
                    blocked = True
                    headers = agent_maker()
                    browser = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
                else: blocked = False
        except Exception as e:
            print('Problem with FIRST TipRanks WebSite: '+str(e))
        try:
            smart_score = browser.find('div', class_="flexrsc displayflex fontSize1").find('tspan')
            #consensus_score_string = browser.find('div', class_="pt4 pl3 grow1 flexr_bf").find_next().find_next('span').find_next_sibling()
            #consensus_score_string = consensus_score_string.text
            smart_score = smart_score.text
            #consensus_score = ratingToNumber(consensus_score_string)
            if smart_score == 'N/A' : 
                smart_score = 6
            smart_score = int(smart_score)/2
            self.stocks_df.loc[index, 'Tip score'] = smart_score
            #self.stocks_df.loc[index, 'Tip analyst'] = consensus_score
            fundamental_score += 0.1 * smart_score
            #fundamental_score += 0.1 * consensus_score
        except Exception as e:
            print('Problem with TipRanks WebSite: '+str(e))
            self.stocks_df.loc[index, 'Tip score'] = 3
            fundamental_score += 0.1 * 3

    def alpha_scrapper_api(self, symbol, index):
        quant_rating = None
        sa_authors_rating = None
        sa_wall_street = None
        sa_wall_flag = False
        sa_quant_flag = False
        sa_authors_flag = False
        global fundamental_score
        try:
            url = "https://seeking-alpha.p.rapidapi.com/symbols/get-ratings"
            querystring = {"symbol":symbol}
            headers = {'x-rapidapi-host': "seeking-alpha.p.rapidapi.com",
                    'x-rapidapi-key': os.getenv('sa_api_key')}
            response = requests.request("GET", url, headers=headers, params=querystring)
            ranking = response.json()
        except Exception as e:
            print("Problem with SeekingAlpha WebSite: "+str(e))
        try:
            quant_rating = ranking['data'][0]['attributes']['ratings']['quantRating']
        except:
            sa_quant_flag = True
        try:
            sa_authors_rating = ranking['data'][0]['attributes']['ratings']['authorsRatingPro']
        except:
            sa_authors_flag = True
        try:
            sa_wall_street = ranking['data'][0]['attributes']['ratings']['sellSideRating']
        except:
            sa_wall_flag = True
        self.sa_score_handle(sa_authors_rating, quant_rating, sa_wall_street, sa_authors_flag, sa_quant_flag, sa_wall_flag, index)

    def zacks_scrapper(self, symbol, index):
        try:
            global fundamental_score
            data = subprocess.Popen("zacks-api "+symbol, shell=True, stdout=subprocess.PIPE).stdout.read()
            data = str(data, 'utf-8')
            data = data.strip("\r\n")
            data = data.split(',')
            for line in data:
                if 'zacksRank' in line and line != 'zacksRankText':
                    rating = line
            rating = rating.split(":")
            rating = rating[1]
            rating = rating.strip(" ").replace('"',"")
            rating = 6 - int(rating)
            fundamental_score +=  0.15 * rating
            self.stocks_df.loc[index, 'Zacks'] = rating
        except Exception as e:
            print('Problem with Zacks website: '+str(e))
            self.stocks_df.loc[index, 'Zacks'] = 3
            fundamental_score += 0.15 * 3

    def portfolio123_scrapper(self, symbol, index):
        try:
            global fundamental_score
            today = date.today()
            client = p123api.Client(api_id='179', api_key=os.getenv('p123_api_key'))
            data = client.rank_ranks(
                {
                    "rankingSystem": "itay sector best - Copy(3)",
                    "asOfDt": str(today), #yyyy-mm-dd
                    # Optional parameters
                    "pitMethod": "Prelim",  #Prelim or Complete
                    "precision": 2,  # 2,3,4
                    "rankingMethod": 2, #2-Percentile NAs Negative, 4-Percentile NAs Neutral
                    "universe": "All Fundamentals - USA",
                    "tickers": symbol,
                    "includeNames": False,
                    "includeNaCnt": False,
                    "includeFinalStmt": False
                }
                )
            rank = str(data['ranks'])
            if(len(rank) == 2):
                self.stocks_df.loc[index, 'P123'] = 3
                fundamental_score += 0.25 * 3
                return
            rank = float(rank.replace("[","").replace("]",""))
            #rank = portfolio123_to_rank(rank)
            rank = rank/20
            fundamental_score += 0.25 * rank
            self.stocks_df.loc[index, 'P123'] = rank
        except p123api.ClientException as e:
            print(e)
            self.stocks_df.loc[index, 'P123'] = 3
            fundamental_score += 0.25 * 3

    def portfolio123_technical_scrapper(self, symbol, index):
        try:
            today = date.today()
            client = p123api.Client(api_id='179', api_key=os.getenv('p123_api_key'))
            data_technical = client.rank_ranks(
                {
                    "rankingSystem": "technical rank",
                    "asOfDt": str(today), #yyyy-mm-dd
                    # Optional parameters
                    "pitMethod": "Prelim",  #Prelim or Complete
                    "precision": 2,  # 2,3,4
                    "rankingMethod": 2, #2-Percentile NAs Negative, 4-Percentile NAs Neutral
                    "universe": "All Fundamentals - USA",
                    "tickers": symbol,
                    "includeNames": False,
                    "includeNaCnt": False,
                    "includeFinalStmt": False
                }
                )
            rank_technical = str(data_technical['ranks'])
            if(len(rank_technical) == 2):
                self.stocks_df.loc[index, 'Technical Score'] = 3
                return
            rank_technical = float(rank_technical.replace("[","").replace("]",""))
            #rank_technical = portfolio123_to_rank(rank_technical)
            self.stocks_df.loc[index, 'Technical Score'] = (rank_technical/20)
        except p123api.ClientException as e:
            print(e)
            self.stocks_df.loc[index, 'Technical Score'] = 3

    def ratingToNumber(rating):
            if rating == 'N/A': return 3
            if rating == 'Strong Buy': return 5
            if rating == 'Moderate Buy': return 4
            if rating == 'Hold': return 3
            return 1 

    def portfolio123_to_rank(rank):
        if rank >= 90: return 5
        if rank <=20: return 1 #check it with itay
        return rank/20
    
    def getSector(self,symbol):
        try:
            ticker_data = yf.Ticker(symbol)
            sector = ticker_data.get_info()['sector']
        except:
            sector = 'None'
        return sector

    def getIndustry(self,symbol):
        try:
            ticker_data = yf.Ticker(symbol)
            industry = ticker_data.get_info()['industry']
        except:
            industry = 'None'
        return industry

    def sa_score_handle(self, sa_authors_rating, quant_rating, sa_wall_street, sa_authors_flag, sa_quant_flag, sa_wall_flag, index):
        global fundamental_score
        if sa_authors_flag == False and sa_quant_flag == False and sa_wall_flag == False: 
                self.stocks_df.loc[index, 'SA authors'] = sa_authors_rating
                self.stocks_df.loc[index, 'SA quant'] = quant_rating
                self.stocks_df.loc[index, 'SA wall st'] = sa_wall_street
                fundamental_score += 0.1 * sa_authors_rating
                fundamental_score += 0.15 * quant_rating
                fundamental_score += 0.1 * sa_wall_street
        elif sa_authors_flag == False and sa_quant_flag == False and sa_wall_flag == True: 
                self.stocks_df.loc[index, 'SA authors'] = sa_authors_rating
                self.stocks_df.loc[index, 'SA quant'] = quant_rating
                self.stocks_df.loc[index, 'SA wall st'] = 3
                fundamental_score += 0.1 * sa_authors_rating
                fundamental_score += 0.15 * quant_rating
                fundamental_score += 0.1 * 3
        elif sa_authors_flag == False and sa_quant_flag == True and sa_wall_flag == False: 
                self.stocks_df.loc[index, 'SA authors'] = sa_authors_rating
                self.stocks_df.loc[index, 'SA quant'] = 3
                self.stocks_df.loc[index, 'SA wall st'] = sa_wall_street
                fundamental_score += 0.1 * sa_authors_rating
                fundamental_score += 0.15 * 3
                fundamental_score += 0.1 * sa_wall_street
        elif sa_authors_flag == False and sa_quant_flag == True and sa_wall_flag == True: 
                self.stocks_df.loc[index, 'SA authors'] = sa_authors_rating
                self.stocks_df.loc[index, 'SA quant'] = 3
                self.stocks_df.loc[index, 'SA wall st'] = 3
                fundamental_score += 0.1 * sa_authors_rating
                fundamental_score += 0.15 * 3
                fundamental_score += 0.1 * 3
        elif sa_authors_flag == True and sa_quant_flag == False and sa_wall_flag == False: 
                self.stocks_df.loc[index, 'SA authors'] = 3
                self.stocks_df.loc[index, 'SA quant'] = quant_rating
                self.stocks_df.loc[index, 'SA wall st'] = sa_wall_street
                fundamental_score += 0.1 * 3
                fundamental_score += 0.15 * quant_rating
                fundamental_score += 0.1 * sa_wall_street
        elif sa_authors_flag == True and sa_quant_flag == False and sa_wall_flag == True: 
                self.stocks_df.loc[index, 'SA authors'] = 3
                self.stocks_df.loc[index, 'SA quant'] = quant_rating
                self.stocks_df.loc[index, 'SA wall st'] = 3
                fundamental_score += 0.1 * 3
                fundamental_score += 0.15 * quant_rating
                fundamental_score += 0.1 * 3
        elif sa_authors_flag == True and sa_quant_flag == True and sa_wall_flag == False: 
                self.stocks_df.loc[index, 'SA authors'] = 3
                self.stocks_df.loc[index, 'SA quant'] = 3
                self.stocks_df.loc[index, 'SA wall st'] = sa_wall_street
                fundamental_score += 0.1 * 3
                fundamental_score += 0.15 * 3
                fundamental_score += 0.1 * sa_wall_street
        elif sa_authors_flag == True and sa_quant_flag == True and sa_wall_flag == True: 
                self.stocks_df.loc[index, 'SA authors'] = 3
                self.stocks_df.loc[index, 'SA quant'] = 3
                self.stocks_df.loc[index, 'SA wall st'] = 3
                fundamental_score += 0.1 * 3
                fundamental_score += 0.15 * 3
                fundamental_score += 0.1 * 3

    def read_file(self, file_path, stock_interval):
        try:
            symbol_pd = pd.DataFrame()
            if(".xlsx" in file_path or '.xls' in file_path):
                symbol_pd = pd.read_excel(file_path)
            elif '.csv' in file_path:
                symbol_pd = pd.read_csv(file_path, encoding = 'cp1255')
            else:
                print("Problem with reading file")
                return
            if(stock_interval == "Future-Tech"):
                symbol_np = symbol_pd['symbol'].to_numpy()
                symbol_arr = fixingArray(symbol_np)
                self.stocks_df['Symbol'] = symbol_arr
                return
            symbol_weekly = []
            symbol_monthly = []
            for index, value in symbol_pd.iterrows():
                if value['גרף'] == 'שבועי':
                    symbol_weekly.append(value['נייר'])
                if value['גרף'] == 'חודשי':
                    symbol_monthly.append(value['נייר'])

            symbol_weekly = fixingArray(symbol_weekly)
            symbol_monthly = fixingArray(symbol_monthly)
            if(stock_interval in "Weekly"):
                self.stocks_df['Symbol'] = symbol_weekly
            elif(stock_interval in "Monthly"):
                self.stocks_df['Symbol'] = symbol_monthly
        except Exception as e:
            print(f'problem with reading excel file! {str(e)}')
            print('check again the column name, it should be "symbol"')
            self.stocks_df['Symbol'] = None


def agent_maker():
    user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    ]
    #Pick a random user agent
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    return headers

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

def setBrowser(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    return driver

print(__name__)