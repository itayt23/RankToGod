import pandas as pd
from bs4 import BeautifulSoup
import requests
import subprocess
import p123api
import pandas as pd
from datetime import date
import random
import time
import selenium.webdriver as webdriver
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import finvizfinance.quote as finviz
import chart_to_god
import numpy as np


# fin_info = finviz.finvizfinance(symbol)
# fin_info = fin_info.ticker_fundament()
# self.stocks_df.loc[index, 'Market Cap'] = fin_info['Market Cap']
# self.stocks_df.loc[index, 'P/E'] = fin_info['P/E']
# self.stocks_df.loc[index, 'Forward P/E'] = fin_info['Forward P/E']
# self.stocks_df.loc[index, 'Volatility (Month)'] = fin_info['Volatility M']
# self.stocks_df.loc[index, 'Beta'] = fin_info['Beta']
# self.stocks_df.loc[index, 'Earnings'] = fin_info['Earnings']

rank_to_god_score_weight = 0.14285714
final_score_weight = 0.1111
fundamental_score = 0
first_blocked = 0
secret = False
if(secret):
    saw_name = 'S1'
    saa_name = 'S2'
    saq_name = 'S3'
    zacks_name = 'Z'
    p123_name = 'P'
    guru_name = 'G'
    tipranks_name = 'T'
else:
    saw_name = 'SA wall street'
    saa_name = 'SA authors'
    saq_name = 'SA quant'
    zacks_name = 'Zacks'
    p123_name = 'P123'
    guru_name = 'GuruFocus'
    tipranks_name = 'TipRanks'

class Ranker:
    def __init__(self, file_path, stock_interval):
        self.scrap_type = stock_interval
        self.technical_score = 0
        if(stock_interval == 'RankToGod Analysis'):
            self.stocks_df = pd.DataFrame(columns=['Symbol',saw_name,saa_name,saq_name,zacks_name,p123_name,guru_name,'Technical Score',
                            'RankToGod Score',tipranks_name,'AI','Final Score','Sector','Industry','Market Cap','P/E','Forward P/E','Beta','Earnings'])
        elif(stock_interval == 'Valuations'):
            self.stocks_df = pd.DataFrame(columns=['Symbol','P/E','Forward P/E','Beta','WACC %(TTM)','Buyback Yield %(TTM)','Dividend %','Shs Outstand','Basic Eps TTM'
                            ,'Consensus EPS Estimates','Sector','Industry','Market Cap','Earnings','Purchase Of Property, Plant, Equipment TTM'
                            ,'Purchase Of Property, Plant, Equipment AVG3Y'])
        self.read_file(file_path, stock_interval)
        load_dotenv()

    def get_rank_type(self):
        return self.scrap_type

    def getDataFrame(self):
        return self.stocks_df
    
    def run_technical(self,symbol,index):
        score = chart_to_god.run_technical(symbol,index)
        self.technical_score = score
        self.stocks_df.loc[index, 'Technical Score'] = score
        

    # def run_sentiment(self, symbol, index):
    #     if(self.scrap_type == 'Sentiment Rank'):
    #         self.run_sentiment_rank(symbol,index)
    #     elif(self.scrap_type == 'Valuations'):
    #         self.run_valuations(symbol,index)

    def run_valuations(self, symbol, index):
        self.guru_value_scrapper(symbol,index)
        self.sa_value_scrapper(symbol,index)
        # self.finviz_value_scrapper(symbol,index)
    
    def run_sentiment_rank(self, symbol, index):
        global fundamental_score
        fundamental_score = 0
        symbol = str(symbol)
        #page = 'https://www.tipranks.com/stocks/'+symbol+'/stock-analysis'
        # page = 'https://www.tipranks.com/'
        # self.tip_scrapper(page, index, symbol)
        self.alpha_scrapper_api(symbol, index)
        self.zacks_scrapper(symbol, index)
        self.portfolio123_scrapper(symbol, index)
        # self.portfolio123_technical_scrapper(symbol, index)
        self.guru_scrapper(symbol,index)
        self.stocks_df.loc[index, 'RankToGod Score'] =f"={fundamental_score}+0.14285714*(I{index+2}*5)"
        self.stocks_df.loc[index, 'Final Score'] =f"=0.7777*J{index+2} + 0.1111*K{index+2} + 0.1111*L{index+2}"
        api_key = os.getenv('guru_api_key')
        try:
            url = f"https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/financials"
            response = requests.request("GET", url)
            stock_info = response.json()
            self.stocks_df.loc[index, 'P/E'] = stock_info['financials']['annuals']['valuation_ratios']['PE Ratio without NRI'][-1]
            self.stocks_df.loc[index, 'Beta'] = stock_info['financials']['annuals']['valuation_and_quality']['Beta'][-1]
            self.stocks_df.loc[index, 'Market Cap'] = stock_info['financials']['annuals']['valuation_and_quality']['Market Cap'][-1]
            self.stocks_df.loc[index, 'Shs Outstand'] = stock_info['financials']['annuals']['income_statement']['Shares Outstanding (Diluted Average)'][-1]
            self.stocks_df.loc[index, 'Dividend %'] = stock_info['financials']['annuals']['valuation_ratios']['Dividend Yield %'][-1]
        except Exception as e:
            print('Problem with Guru Fundamental API '+str(e))
        try:
            url = f"https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/summary"
            response = requests.request("GET", url)
            stock_info = response.json()
            self.stocks_df.loc[index, 'Sector'] = stock_info['summary']['general']['sector']
            self.stocks_df.loc[index, 'Industry'] = stock_info['summary']['general']['industry']
            self.stocks_df.loc[index, 'Earnings'] = stock_info['summary']['company_data']['next_earnings_date']
            self.stocks_df.loc[index, 'Forward P/E'] = (stock_info['summary']['ratio']['Forward P/E']['value'])
        except Exception as e:
            print("Problem with Guru 'summary' Fundamental API "+str(e))
            
          
    


    def sa_value_scrapper(self,symbol,index):
        try:
            url = "https://seeking-alpha.p.rapidapi.com/symbols/get-metrics"
            querystring = {"symbols":f"{symbol}","fields":"eps_ltg"}

            headers = {
                "X-RapidAPI-Key": os.getenv('sa_api_key'),
                "X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"}

            response = requests.get(url, headers=headers, params=querystring).json()
            eps_long = response['data'][0]['attributes']['value']
            eps_long = round(eps_long,2)
            self.stocks_df.loc[index, 'EPS FWD Long Term Growth(SA)'] = eps_long
        except Exception as e:
            print('Problem with Seeking alpha Scrapping '+str(e))
            self.stocks_df.loc[index, 'EPS FWD Long Term Growth(SA)'] = 'N/A'

    def sa_value_scrapper_old(self,symbol,index):
        try:
            url = "https://seeking-alpha.p.rapidapi.com/symbols/get-metrics"
            querystring = {"symbols":f"{symbol}","fields":"eps_ltg"}

            headers = {
                "X-RapidAPI-Key": os.getenv('sa_api_key'),
                "X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"}

            response = requests.get(url, headers=headers, params=querystring).json()
            eps_long = response['data'][0]['attributes']['value']
            eps_long = round(eps_long,2)
            ticker_id = response['data'][0]['relationships']['ticker']['data']['id']

            url = "https://seeking-alpha.p.rapidapi.com/symbols/get-earnings"
            querystring = {f"ticker_ids":{ticker_id},"period_type":"annual","relative_periods":"0,1","estimates_data_items":"eps_normalized_consensus_mean"}
            response = requests.get(url, headers=headers, params=querystring).json()
            eps_consensus = round(float(response['estimates'][ticker_id]['eps_normalized_consensus_mean']['1'][0]['dataitemvalue']),2)

            url = "https://seeking-alpha.p.rapidapi.com/symbols/get-financials"
            querystring = {"symbol":"NVDA","target_currency":"USD","period_type":"annual","statement_type":"income-statement"}
            response = requests.get(url, headers=headers, params=querystring).json()
            if(response[4]['rows'][1]['value'] == 'Basic EPS'):
                eps_val =  response[4]['rows'][2]['cells'][-1]['value']
            else:
                print("Could not succeed in obtaining Basic EPS TTM")
                eps_val = 'N\A'

            self.stocks_df.loc[index, 'EPS FWD Long Term Growth'] = eps_long
            self.stocks_df.loc[index, 'Consensus EPS Estimates'] = eps_consensus
            self.stocks_df.loc[index, 'Basic Eps TTM'] = eps_val
        except Exception as e:
            print('Problem with Seeking alpha Scrapping '+str(e))

    def finviz_value_scrapper(self,symbol,index):
        try:
            fin_info = finviz.finvizfinance(symbol)
            fin_info = fin_info.ticker_fundament()
            self.stocks_df.loc[index, 'Beta'] = fin_info['Beta']
            self.stocks_df.loc[index, 'Market Cap'] = fin_info['Market Cap']
            self.stocks_df.loc[index, 'P/E'] = fin_info['P/E']
            self.stocks_df.loc[index, 'Dividend %'] = fin_info['Dividend %']
            self.stocks_df.loc[index, 'Shs Outstand'] = fin_info['Shs Outstand']
            self.stocks_df.loc[index, 'Forward P/E'] = fin_info['Forward P/E']
            self.stocks_df.loc[index, 'Volatility (Month)'] = fin_info['Volatility M']
            self.stocks_df.loc[index, 'LT Debt/Eq'] = fin_info['LT Debt/Eq']            
            self.stocks_df.loc[index, 'Earnings'] = fin_info['Earnings']
            self.stocks_df.loc[index, 'EPS (ttm)'] = fin_info['EPS (ttm)']
            self.stocks_df.loc[index, 'EPS next Y'] = fin_info['EPS next Y']
            self.stocks_df.loc[index, 'EPS next 5Y'] = fin_info['EPS next 5Y']
        except Exception as e:
            print('Problem with Finviz Scrapping '+str(e))
            
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
                fundamental_score += rank_to_god_score_weight * 3
                #fundamental_score += rank_to_god_score_weight * 3
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
            fundamental_score += rank_to_god_score_weight * smart_score
            #fundamental_score += rank_to_god_score_weight * consensus_score
        except Exception as e:
            print('Problem with TipRanks WebSite: '+str(e))
            self.stocks_df.loc[index, 'Tip score'] = 3
            fundamental_score += rank_to_god_score_weight * 3

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
            sa_authors_rating = ranking['data'][0]['attributes']['ratings']['authorsRating']
        except:
            sa_authors_flag = True
        try:
            sa_wall_street = ranking['data'][0]['attributes']['ratings']['sellSideRating']
        except:
            sa_wall_flag = True
        self.sa_score_handle(sa_authors_rating, quant_rating, sa_wall_street, sa_authors_flag, sa_quant_flag, sa_wall_flag, index)

    def zacks_scrapper(self, symbol, index):
        try:
            global fundamental_score,zacks_name
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
            fundamental_score +=  rank_to_god_score_weight * rating
            self.stocks_df.loc[index, zacks_name] = rating
        except Exception as e:
            print('Problem with Zacks website: '+str(e))
            self.stocks_df.loc[index, zacks_name] = 3
            fundamental_score += rank_to_god_score_weight * 3

    def portfolio123_scrapper(self, symbol, index):
        try:
            global fundamental_score,p123_name
            today = date.today()
            client = p123api.Client(api_id='179', api_key= os.getenv('p123_api_key'))
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
                self.stocks_df.loc[index, p123_name] = 3
                fundamental_score += rank_to_god_score_weight * 3
                return
            rank = float(rank.replace("[","").replace("]",""))
            #rank = portfolio123_to_rank(rank)
            rank = rank/20
            fundamental_score += rank_to_god_score_weight * rank
            self.stocks_df.loc[index, p123_name] = rank
        except p123api.ClientException as e:
            print(f"P123 problem: {str(e)}, Ticker: {symbol}")
            self.stocks_df.loc[index, p123_name] = 3
            fundamental_score += rank_to_god_score_weight * 3

    def portfolio123_technical_scrapper(self, symbol, index):
        try:
            today = date.today()
            client = p123api.Client(api_id='179', api_key= os.getenv('p123_api_key'))
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
            print(f"Technical P123 problem: {str(e)}, Ticker: {symbol}" )
            self.stocks_df.loc[index, 'Technical Score'] = 3

    def guru_scrapper(self, symbol, index):
        try:
            global fundamental_score,guru_name
            # response = urllib.request.urlopen('https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/summary')
            # content = response.read()
            # data = json.loads(content.decode('utf8'))
            # print(data['Valuation Ratio']['PS Ratio'])
            api_key = os.getenv('guru_api_key')
            url = f"https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/summary"
            response = requests.request("GET", url)
            stock_info = response.json()
            gf_score = float(stock_info['summary']['general']['gf_score'])
            gf_score = (gf_score/20)
            self.stocks_df.loc[index, guru_name] = (gf_score)
            fundamental_score += rank_to_god_score_weight * gf_score
           
        except Exception as e:
            info =""
            if("message" in stock_info):
                info = stock_info["message"]
            print('Problem with GuruFoucus website: '+str(e) + ", API info: " +  info)
            self.stocks_df.loc[index, guru_name] = 3
            fundamental_score += rank_to_god_score_weight * 3


    def guru_value_scrapper(self, symbol, index):
        api_key = os.getenv('guru_api_key')
        try:
            url = f"https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/financials"
            response = requests.request("GET", url)
            stock_info = response.json()
            #stock_info['financials']['annuals'].keys() - dict_keys(['Fiscal Year', 'Preliminary', 'per_share_data_array', 'common_size_ratios', 
            # 'income_statement', 'balance_sheet', 'cashflow_statement', 'valuation_ratios', 'valuation_and_quality'])
            wacc = stock_info['financials']['annuals']['common_size_ratios']['WACC %'][-1]
            buyback = stock_info['financials']['annuals']['valuation_and_quality']['Buyback Yield %'][-1]
            basic_eps = stock_info['financials']['annuals']['income_statement']['EPS (Diluted)'][-1]
            self.stocks_df.loc[index, 'P/E'] = stock_info['financials']['annuals']['valuation_ratios']['PE Ratio without NRI'][-1]
            self.stocks_df.loc[index, 'Beta'] = stock_info['financials']['annuals']['valuation_and_quality']['Beta'][-1]
            self.stocks_df.loc[index, 'Market Cap'] = stock_info['financials']['annuals']['valuation_and_quality']['Market Cap'][-1]
            self.stocks_df.loc[index, 'Shs Outstand'] = stock_info['financials']['annuals']['income_statement']['Shares Outstanding (Diluted Average)'][-1]
            self.stocks_df.loc[index, 'Dividend %'] = stock_info['financials']['annuals']['valuation_ratios']['Dividend Yield %'][-1]
            basic_eps = stock_info['financials']['annuals']['per_share_data_array']['EPS without NRI'][-1]
            self.stocks_df.loc[index, 'WACC %(TTM)'] = wacc
            self.stocks_df.loc[index, 'Buyback Yield %(TTM)'] = buyback
            self.stocks_df.loc[index, 'Basic Eps TTM'] = basic_eps
            cash_flow_parchase_ttm = stock_info['financials']['annuals']['cashflow_statement']['Purchase Of Property, Plant, Equipment'][-1]
            avg_3y_cash_flow_parchase = cal_avg( stock_info['financials']['annuals']['cashflow_statement']['Purchase Of Property, Plant, Equipment'],3)
            self.stocks_df.loc[index, 'Purchase Of Property, Plant, Equipment TTM'] = cash_flow_parchase_ttm
            self.stocks_df.loc[index, 'Purchase Of Property, Plant, Equipment AVG3Y'] = avg_3y_cash_flow_parchase
            tax_rate_avg_5y = cal_avg( stock_info['financials']['annuals']['income_statement']['Tax Rate %'],5)
            self.stocks_df.loc[index, 'Tax Rate % AVG5Y'] = tax_rate_avg_5y
            pe_avg_10y = cal_avg( stock_info['financials']['annuals']['valuation_ratios']['PE Ratio without NRI'],10)
            pe_high_10y,pe_low_10y = get_high_low( stock_info['financials']['annuals']['valuation_ratios']['PE Ratio without NRI'],10)
            self.stocks_df.loc[index, 'PE AVG10Y'] = pe_avg_10y
            self.stocks_df.loc[index, 'PE High 10Y'] = pe_high_10y
            self.stocks_df.loc[index, 'PE Low 10Y'] = pe_low_10y
            cash_from_operations_ttm = stock_info['financials']['annuals']['cashflow_statement']['Cash Flow from Operations'][-1]
            cash_from_operation_avg_3y = cal_avg( stock_info['financials']['annuals']['cashflow_statement']['Cash Flow from Operations'],3)
            self.stocks_df.loc[index, 'Cash Flow from Operations TTM'] = cash_from_operations_ttm
            self.stocks_df.loc[index, 'Cash Flow from Operations AVG10Y'] = cash_from_operation_avg_3y
            net_income_countinuing_operation_avg_10y = cal_avg( stock_info['financials']['annuals']['income_statement']['Net Income (Continuing Operations)'],10)
            free_cash_flow_avg_10y = cal_avg( stock_info['financials']['annuals']['cashflow_statement']['Free Cash Flow'],10)
            self.stocks_df.loc[index, 'FCF/NetInc'] = free_cash_flow_avg_10y /net_income_countinuing_operation_avg_10y
            total_debt_per_share_ttm = float(stock_info['financials']['annuals']['per_share_data_array']['Total Debt per Share'][-1])
            cash_per_share_ttm = float(stock_info['financials']['annuals']['per_share_data_array']['Cash per Share'][-1])
            ebiddta_per_share_ttm = float(stock_info['financials']['annuals']['per_share_data_array']['EBITDA per Share'][-1])
            self.stocks_df.loc[index, '(DebtPs-CashPs)/EBITDAPS'] = (total_debt_per_share_ttm - cash_per_share_ttm) /ebiddta_per_share_ttm 
            self.stocks_df.loc[index, 'Debt/Eq'] = stock_info['financials']['annuals']['common_size_ratios']['Debt-to-Equity'][-1]
           
        except Exception as e:
            info =""
            if("message" in stock_info):
                info = stock_info["message"]
            print('Problem with GuruFoucus website: '+str(e) + ", API info: " +  info)

        try:
            url = f"https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/analyst_estimate"
            response = requests.request("GET", url)
            stock_info = response.json()
            # dict_keys(['date', 'revenue_estimate', 'ebit_estimate', 'ebitda_estimate', 'dividend_estimate', 'per_share_eps_estimate',
            #  'eps_nri_estimate', 'long_term_growth_rate_mean', 'long_term_revenue_growth_rate_mean'])
            self.stocks_df.loc[index, 'Consensus EPS Estimates'] = stock_info['annual']['eps_nri_estimate'][0]
           
        except Exception as e:
            info =""
            if("message" in stock_info):
                info = stock_info["message"]
            print('Problem with GuruFoucus website: '+str(e) + ", API info: " +  info)
        try:
            url = f"https://api.gurufocus.com/public/user/{api_key}/stock/{symbol}/summary"
            response = requests.request("GET", url)
            stock_info = response.json()
            # stock_info['summary'] - dict_keys(['general', 'chart', 'ratio', 'guru', 'insider', 'company_data', 'estimate'])
            # print( stock_info['summary']['estimate'].keys()) dict_keys(['count', 'percentage', 'quarter', 'Revenue', 'per share eps', 'eps_nri', 'Dividends Per Share', 'LongTermGrowthRateMean', 'LongTermRevenueGrowthRateMean'])
            future_eps_fwd = stock_info['summary']['ratio']['Future 3-5Y EPS without NRI Growth Rate']['value']
            revenue_growth_1y = stock_info['summary']['company_data']['rvn_growth_1y']
            revenue_growth_3y = stock_info['summary']['company_data']['rvn_growth_3y']
            revenue_growth_5y = stock_info['summary']['company_data']['rvn_growth_5y']
            revenue_growth_10y = stock_info['summary']['company_data']['rvn_growth_10y']
            ebitda_growth_1y = stock_info['summary']['company_data']['ebitda_growth_1y']
            ebitda_growth_3y = stock_info['summary']['company_data']['ebitda_growth_3y']
            ebitda_growth_5y = stock_info['summary']['company_data']['ebitda_growth_5y']
            ebitda_growth_10y = stock_info['summary']['company_data']['ebitda_growth_10y']
            self.stocks_df.loc[index, 'Revenue Growth 1Y'] = revenue_growth_1y
            self.stocks_df.loc[index, 'Revenue Growth 3Y'] = revenue_growth_3y
            self.stocks_df.loc[index, 'Revenue Growth 5Y'] = revenue_growth_5y
            self.stocks_df.loc[index, 'Revenue Growth 10Y'] = revenue_growth_10y
            self.stocks_df.loc[index, 'EBITDA Growth 1Y'] = ebitda_growth_1y
            self.stocks_df.loc[index, 'EBITDA Growth 3Y'] = ebitda_growth_3y
            self.stocks_df.loc[index, 'EBITDA Growth 5Y'] = ebitda_growth_5y
            self.stocks_df.loc[index, 'EBITDA Growth 10Y'] = ebitda_growth_10y
            self.stocks_df.loc[index, 'Sector'] = stock_info['summary']['general']['sector']
            self.stocks_df.loc[index, 'Industry'] = stock_info['summary']['general']['industry']
            self.stocks_df.loc[index, 'Earnings'] = stock_info['summary']['company_data']['next_earnings_date']
            self.stocks_df.loc[index, 'Forward P/E'] = (stock_info['summary']['ratio']['Forward P/E']['value'])
            self.stocks_df.loc[index, 'Future 3-5Y EPS'] = future_eps_fwd 
           
        except Exception as e:
            info =""
            if("message" in stock_info):
                info = stock_info["message"]
            print('Problem with GuruFoucus website: '+str(e) + ", API info: " +  info)

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

    def sa_score_handle(self, sa_authors_rating, quant_rating, sa_wall_street, sa_authors_flag, sa_quant_flag, sa_wall_flag, index):
        global fundamental_score,saw_name,saa_name,saq_name
        if sa_authors_flag == False and sa_quant_flag == False and sa_wall_flag == False: 
                self.stocks_df.loc[index, saa_name] = sa_authors_rating
                self.stocks_df.loc[index, saq_name] = quant_rating
                self.stocks_df.loc[index, saw_name] = sa_wall_street
                fundamental_score += rank_to_god_score_weight * sa_authors_rating
                fundamental_score += rank_to_god_score_weight * quant_rating
                fundamental_score += rank_to_god_score_weight * sa_wall_street
        elif sa_authors_flag == False and sa_quant_flag == False and sa_wall_flag == True: 
                self.stocks_df.loc[index, saa_name] = sa_authors_rating
                self.stocks_df.loc[index, saq_name] = quant_rating
                self.stocks_df.loc[index, saw_name] = 3
                fundamental_score += rank_to_god_score_weight * sa_authors_rating
                fundamental_score += rank_to_god_score_weight * quant_rating
                fundamental_score += rank_to_god_score_weight * 3
        elif sa_authors_flag == False and sa_quant_flag == True and sa_wall_flag == False: 
                self.stocks_df.loc[index, saa_name] = sa_authors_rating
                self.stocks_df.loc[index, saq_name] = 3
                self.stocks_df.loc[index, saw_name] = sa_wall_street
                fundamental_score += rank_to_god_score_weight * sa_authors_rating
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * sa_wall_street
        elif sa_authors_flag == False and sa_quant_flag == True and sa_wall_flag == True: 
                self.stocks_df.loc[index, saa_name] = sa_authors_rating
                self.stocks_df.loc[index, saq_name] = 3
                self.stocks_df.loc[index, saw_name] = 3
                fundamental_score += rank_to_god_score_weight * sa_authors_rating
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * 3
        elif sa_authors_flag == True and sa_quant_flag == False and sa_wall_flag == False: 
                self.stocks_df.loc[index, saa_name] = 3
                self.stocks_df.loc[index, saq_name] = quant_rating
                self.stocks_df.loc[index, saw_name] = sa_wall_street
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * quant_rating
                fundamental_score += rank_to_god_score_weight * sa_wall_street
        elif sa_authors_flag == True and sa_quant_flag == False and sa_wall_flag == True: 
                self.stocks_df.loc[index, saa_name] = 3
                self.stocks_df.loc[index, saq_name] = quant_rating
                self.stocks_df.loc[index, saw_name] = 3
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * quant_rating
                fundamental_score += rank_to_god_score_weight * 3
        elif sa_authors_flag == True and sa_quant_flag == True and sa_wall_flag == False: 
                self.stocks_df.loc[index, saa_name] = 3
                self.stocks_df.loc[index, saq_name] = 3
                self.stocks_df.loc[index, saw_name] = sa_wall_street
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * sa_wall_street
        elif sa_authors_flag == True and sa_quant_flag == True and sa_wall_flag == True: 
                self.stocks_df.loc[index, saa_name] = 3
                self.stocks_df.loc[index, saq_name] = 3
                self.stocks_df.loc[index, saw_name] = 3
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * 3
                fundamental_score += rank_to_god_score_weight * 3

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
            if(stock_interval == "RankToGod Analysis" or stock_interval == 'Valuations'):
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


def cal_avg(arr,years:int):
    if(arr[-1] == 'At Loss'):
        return 'At Loss'
    arr = arr[:-1]
    new_arr = []
    for num in arr:
        if num != 'At Loss' and num != 'N/A':
            new_arr.append(float(num))
    if(len(new_arr) < years):
        years = len(new_arr)
    return np.mean([float(num) for num in arr[-years:]])
    
def get_high_low(arr,years:int):
    if(arr[-1] == 'At Loss'):
        return 'At Loss','At Loss'
    arr = arr[:-1]
    new_arr = []
    for num in arr:
        if num != 'At Loss' and num != 'N/A':
            new_arr.append(float(num))
    if(len(new_arr) < years):
        years = len(new_arr)
    arr_float = [float(num) for num in arr[-years:]]
    return np.max(arr_float), np.min(arr_float)