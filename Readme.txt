npm install zacks-api --global
pip install npm



for now, tipranks is blocking me for 2 minutes excactly every 4 scrapping.
with sleep of 10 seconds, the script doing 25 stocks in 8.3 minutes.
with sleep of 5 seconds, the script doing 25 stocks in 

------------V2-------------------

Changing scrapping tipRanks to seeking alpha alone.

----------------------------------


-------------V3------------------

-Adding Sector & Industry for each stock
-Removing 'Fundamental Score' coulumn from dataframe
- adding 'Tip Ranks Score' column to dataframe as epty column(manual fill)
- adding new folder 'results' to saves all the results
- changing column whights:
	SA wall street : 10%
	SA authors: 10%
	SA quant: 15%
	Zacks: 10%
	P123 : 25%
	tip ranks score: 10%
	Technical score: 15%	

---------------------------------

-------------V4------------------

-MultyThreading programm for more fluid app running

---------------------------------
-------------V4.1------------------

-Fixing SA authors Bug

---------------------------------
-------------V5------------------

-changing from tipRanks to GuruFocous api
-Fixing sector & industry Bug

---------------------------------
-------------V5.1------------------

-Added the next fund factors from finviz (using finvizfinance):
*Market Cap
*Volatility Month
*Beta
*P\E
*Forword P\E
---------------------------------
-------------V5.2------------------

-Encrypted Version
*S1 -> SA wall street
*S2->  SA authors
*S3 -> SA quant
*Z - >  Zacks
*P - >	P123
*G -> GuruFocus

-Added myapp.spec for pyinstaller myapp.spec 
---------------------------------
-------------V6------------------
-Change column name 'Final Score' to 'RankToGod Score'
-change code to support Encrypted Version and Non Encrypted Fast
-Added 3 more column as Lior asks (TipRanks,AI,Final Score)
---------------------------------
-------------V7------------------
-deleted 'weekly' and 'monthly' options
-added 'Valuations' option - take a lot of valuations per stock
---------------------------------
-------------V2.2------------------
-added valuation datas
-added RankToGod Analaysis - mix of ChartToGod and original RankToGod
---------------------------------

-------------V2.3------------------
- Fixed charttogod problem with stocks like br.a\br.k 
---------------------------------

-------------V2.31------------------
- Deleting AI column
- Update SA API
---------------------------------