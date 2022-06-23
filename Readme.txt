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