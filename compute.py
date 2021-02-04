import io, base64

import bs4 as bs
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader.data as web
import requests


def time_stamp():
    return dt.datetime.now().strftime("%c")

def is_number(shortTerm, longTerm):
    ''' error validator for short/long term (not used) '''
    try:
        float(shortTerm)
        return True, float(shortTerm)
    except:
        return False

def abs_min_max(*df):
    ''' abs min/max for plot limits '''
    absMax = 0
    for col in df:
        absCol = max(abs(col.min()), col.max())
        #print(f"absCol {absCol}, absminmax {absMax}")
        if absCol > absMax:
            absMax = absCol
    
    '''#abscol2 = max(abs(col2.min()), col2.max()) if absCol2>absMax2 for col2 in df]
    absCol2 = [max(abs(col2.min()), col2.max()) for col2 in df]
    print(f"abscol2 {absCol2}")
    absMax2 = 0
    if max(absCol2) > absMax2:
        absMax2 = max(absCol2)
        print(f"absMax2 {absMax2}")
    '''
    return absMax

def MA_term(shortTerm, longTerm):
    ''' convert the monthly term to weekdays 
        "window" in statistical dataframes needs to be an integer'''
    
    shortTerm = 22 * shortTerm
    longTerm = 22 * longTerm

    shortTerm, longTerm = int(shortTerm), int(longTerm)
    
    return shortTerm, longTerm

def FTSE100_EPIC():
    ''' soups all FTSE100 EPIC and company names frtom wikipedia
    adds ".L" to EPIC to ensure it is on LSE
    returns EPIC and names'''
    
    url = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index')

    soup = bs.BeautifulSoup(url.text, "html.parser")
    table = soup.find('table', {'id': 'constituents'})
    
    #print(url.encoding) # checks encoding method
    
    FTSE100NameAll, FTSE100EpicAll = [], []
    for row in table.findAll('tr')[1:]:
        FTSE100Name = row.findAll('td')[0].text
        FTSE100Epic = row.findAll('td')[1].text
        FTSE100NameAll.append(FTSE100Name) 
        FTSE100EpicAll.append(FTSE100Epic)

    '''update EPIC to use Ldn stock exchange'''
    FTSE100EpicAll = [
                    w+'L' if w[-1] == '.' 
                    else w+'.L' if w[-1] != '.' 
                    else w if w[-2] == '.L' 
                    else w 
                    for w in FTSE100EpicAll
                  ]
    
    '''with open ('wikiPage.txt', 'w', encoding="utf-8") as f:
        f.write(url.text)
    with open ('epicHtmlTable.txt', 'w', encoding="utf-8") as f:
        f.write(table.text)
    '''
    
    ''' testing for API '''
    FTSE100EpicAllTest = "N"
    if FTSE100EpicAllTest == "Y":
        FTSE100EpicAll, FTSE100NameAll = ["AAPL", "TSLA", "AMZN", "FB", "BP.L", "AZN.L"], \
                                         ['Apple', 'Tesla', 'Amazon', "Facebook", "BP", "AstraZeneca"]
        #FTSE100EpicAll, FTSE100NameAll = ["AAPL", "AMZN", "AMZN"], \
        #                                 ['Apple', "Amazon", "Facebook"]

    return FTSE100EpicAll, FTSE100NameAll

def statistics_data(epicAll, t0, t1, shortTerm, longTerm):
    ''' Statistics on data.
        ewma - exp decaying weighted average, priority on most recent dates, 
        adjust=false for recursion, ie new values use old calcd ewma values
        
        The rate of change of MA is calculated based on the term length, not 
        yesterday's change (eg  MA over days 10 to 20 / MA over days 0 to 10, 
        not MA over days 10 to 20 / MA over days 9 to 19)
    
        using offset window for MA as it will use the datetime info in the index,
        so will take into account weekends - but then dont need 22 days
        
        Dont grow a DataFrame! Cheaper to append to a python list, 
        convert to DataFrame at the end, both in terms of memory and performance.
    '''
    
    if t1 == "today":
        t1 = dt.datetime.now()

    # convert to list to get multilevel on multiindex dataframe
    if type(epicAll) != list:
        epicAll = [epicAll]
        
    dfEpic = web.DataReader(epicAll, 'yahoo', t0, t1)
    dfEpic = dfEpic.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1)
    
    shortTerm, longTerm = MA_term(shortTerm, longTerm)

    if type(epicAll) == list:
        for i, epic in enumerate(epicAll):
            
            dfEpic['Normalised from t0', epic] = dfEpic['Adj Close', epic] / dfEpic['Adj Close', epic][0]
    
            dfEpic['ShortMA', epic] = dfEpic['Adj Close', epic].rolling(window=shortTerm, min_periods=0).mean()
            dfEpic['LongMA', epic] = dfEpic['Adj Close', epic].rolling(window=longTerm, min_periods=0).mean()
            dfEpic['ShortEWMA', epic] = dfEpic['Adj Close', epic].ewm(span=shortTerm, adjust=False).mean()
            #dfEpic['ShortMAOffset', epic] = dfEpic['Adj Close', epic].rolling(window=str(shortTerm) + 'D', min_periods=0).mean()
            
            dfEpic['ShortMAChange', epic] = (dfEpic['ShortMA', epic] / dfEpic['ShortMA', epic].shift(shortTerm)) - 1
            #dfEpic['ShortMAChange'] = dfEpic['ShortMAChange'].fillna(0)
            dfEpic['ShortEWMAChange', epic] = (dfEpic['ShortEWMA', epic] / dfEpic['ShortEWMA', epic].shift(shortTerm)) - 1
            #dfEpic['ShortEWMAChange'] = dfEpic['ShortEWMAChange'].fillna(0)
            dfEpic['LongMAChange', epic] = (dfEpic['LongMA', epic] / dfEpic['LongMA', epic].shift(longTerm)) - 1
            #dfEpic['LongMAChange'] = dfEpic['LongMAChange'].fillna(0)

    else:
        dfEpic['LongMA'] = dfEpic['Adj Close'].rolling(window=longTerm, min_periods=0).mean()
        dfEpic['ShortEWMA'] = dfEpic['Adj Close'].ewm(span=shortTerm, adjust=False).mean()
        dfEpic['ShortEWMAChange'] = (dfEpic['ShortEWMA', epic] / dfEpic['ShortEWMA'].shift(shortTerm)) - 1
        dfEpic['LongMAChange'] = (dfEpic['LongMA'] / dfEpic['LongMA'].shift(longTerm)) - 1
 
    return dfEpic

def current_price(epicAll):
    ''' return the current price, yesterdays price, and change '''

    # data. t0, short/long term temp values are placeholders for pandas datareader
    t0 = (dt.datetime.now() - dt.timedelta(days=10))
    shortTermTemp =  longTermTemp = 1
    
    # failure escape for unknown EPIC
    try:
        dfEpic = statistics_data(epicAll, t0, dt.datetime.now(), shortTermTemp, longTermTemp)
    except (IOError, KeyError):
        failure = f"Failed to read EPIC for {epicAll}.  \
        Please check you are using symbol not company name,  \
        and that the dates are accurate."
        strPriceData = 0
        
        return failure, strPriceData

    # Adj close results
    currClose = dfEpic['Adj Close', epicAll][-1]
    prevClose = dfEpic['Adj Close', epicAll][-2]
    changeClose = currClose - prevClose
    changePercClose = changeClose/prevClose * 100

    # formatting
    currPrice = round(currClose, 6)
    changePercClose = round(changePercClose, 2)
    
    if changeClose > 0:
        changeClose = "+" + str(round(changeClose, 2))
    else:
        changeClose = round(changeClose, 2)

    strPriceData = str(changeClose) + ", (" + str(changePercClose) + "%)"

    #return curr_price, change_close, change_perc_close
    return currPrice, strPriceData

def statistics_plots(epicAll, t0, t1, shortTerm, longTerm):
    ''' produce statistical plots on share price '''
           
    if t1 == "today":
        t1 = dt.datetime.now()
    
    # convert to list to get multilevel on multiindex dataframe
    if type(epicAll) != list:
        epicAll = [epicAll]

    #failure plot escape for unknown epic (return plot without data)
    try:
        dfEpic = statistics_data(epicAll, t0, t1, shortTerm, longTerm)
    except (IOError, KeyError):
        fig, ax = plt.subplots(1, 1)
        ax.set_title(f"Failed to read symbol for {epicAll}. Please use symbol, \
        not company name")
        img = io.BytesIO()    
        plt.savefig(img, format='png')
        img.seek(0)
    
        if __name__ != '__main__':
            plt.close() # close to overwrite plot when using controller.py7
    
        plot_url = base64.b64encode(img.getvalue()).decode()

        return plot_url

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex='col', figsize=(14,6), gridspec_kw={'hspace': 0})
    #fig, (ax1, ax2) = plt.subplots(2, 1, dpi = 200, sharex='col')
    fig.autofmt_xdate()
    #plt.tight_layout()
    fig.patch.set_alpha(0.01)

    for epic in epicAll:
        # https://matplotlib.org/3.1.0/gallery/color/named_colors.html
        ax1.plot(
            dfEpic.index, 
            dfEpic['Adj Close', epic], 
            label = epic + " Adj Close",
            color = 'red',
            linewidth=2.0
            )
        ax1.plot(
            dfEpic.index, 
            dfEpic['ShortMA', epic], 
            label = "Short Term MA",
            color = 'dodgerblue',
            #marker = 'o',
            linewidth=1.5
            )
        ax1.plot(
            dfEpic.index, 
            dfEpic['LongMA', epic], 
            label = "Long Term MA",
            color = 'yellowgreen',
            linewidth=1.5
            )
            
        ax2.plot(
            dfEpic['ShortEWMAChange', epic].index, 
            dfEpic['ShortEWMAChange', epic] * 100, 
            label = 'Short Term (\u0394EWMA)',
            color = 'orange',
            marker = 'x',
            linewidth=1.5,
            linestyle = ''
            )
        ax2.plot(
            dfEpic['ShortMAChange', epic].index, 
            dfEpic['ShortMAChange', epic] * 100, 
            label = 'Short Term (\u0394MA)',
            color = 'dodgerblue',
            linewidth=1.5
            )
        ax2.plot(
            dfEpic['LongMAChange', epic].index, 
            dfEpic['LongMAChange', epic] * 100, 
            label = 'Long Term (\u0394MA)',
            color = 'yellowgreen',
            linewidth=1.5
            )

    # This function works for a single EPIC, not a list
    axFaceColour = 'white'#'xkcd:light grey'
    ax1.set_title('Share Price for %s' % (epic))
    ax1.set_ylabel('Adj. Close Price')
    ax1.legend()
    ax1.grid()
    ax1.set_facecolor(axFaceColour)
    
    ax2.set_ylabel('\u0394% Rolling Average') 
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.grid()
    ax2.set_facecolor(axFaceColour)

    # equal y axis scale ΔMA with 10% padding (* 110) 
    maxMAChange = abs_min_max(dfEpic['ShortMAChange', epic], 
                              dfEpic['ShortEWMAChange', epic], 
                              dfEpic['LongMAChange', epic]
                              )
    ax2.set_ylim(-maxMAChange * 110, maxMAChange * 110)
    
    # encode plot into byte stream
    img = io.BytesIO()    
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    # close plot to overwrite (when NOT running local module. ie when using controller.py)
    if __name__ != '__main__':
        plt.close()
        
    return plot_url

    '''
    dfEpicAll, dfEpicAllErrors = [], []
   
    try:
        dfEpicAll = web.DataReader(epic, 'yahoo', t0, t1)
        dfEpicAll = dfEpicAll.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1)
    except (IOError, KeyError):
        print('test')
        dfEpicAllErrors.append(epic)

    print(dfEpicAll)
    print(dfEpicAllErrors)

    return dfEpicAll, dfEpicAllErrors
    '''

def FTSE100_plots(t0, t1, shortTerm, longTerm):
    ''' plot all FTSE100 normalised adj close 
        plot all FTSE100 Δ short EWMA and Δ Long MA
        get highest normalised adj close (most accl. since t0), replot 
        get highest MA for latest date, replot
    '''

    epicAll, epicNameAll = FTSE100_EPIC()   

    dfEpic = statistics_data(epicAll, t0, t1, shortTerm, longTerm)

    ''' level 0 returns all stocks for selected header '''
    maxPriceLatestEpic = dfEpic['Normalised from t0'].idxmax(axis=1)[-1]
    maxPriceLatestEpicNameIndex = epicAll.index(maxPriceLatestEpic)
    maxPriceLatestEpicName = epicNameAll[maxPriceLatestEpicNameIndex]
    
    maxShortEWMALatestEpic = dfEpic['ShortEWMAChange'].idxmax(axis=1)[-1]
    maxShortEWMALatestEpicNameIndex = epicAll.index(maxShortEWMALatestEpic)
    maxShortEWMALatestEpicName = epicNameAll[maxShortEWMALatestEpicNameIndex]

    maxLongMALatestEpic = dfEpic['LongMAChange'].idxmax(axis=1)[-1]
    maxLongMALatestEpicNameIndex = epicAll.index(maxLongMALatestEpic)
    maxLongMALatestEpicName = epicNameAll[maxLongMALatestEpicNameIndex]

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex='col', figsize=(14,6), gridspec_kw={'hspace': 0})
    fig.autofmt_xdate()
    fig.patch.set_alpha(0.01)
    
    ''' plot adj close and ΔMA '''
    for epic in epicAll:
        ax1.plot(
            dfEpic.index, 
            dfEpic['Normalised from t0', epic], 
            #label = 'Adj Close (normalised with t0), ' + epic, 
            label = '', 
            color = 'gray', 
            #legend = False, 
            )
        ax2.plot(
            dfEpic.index, 
            dfEpic['ShortEWMAChange', epic]  * 100, 
            #label = 'ShortEWMAChange, ' + epic, 
            label = '', 
            color = 'gray', 
            )
        ax2.plot(
            dfEpic.index, 
            dfEpic['LongMAChange', epic] * 100, 
            #label = 'Change in Long Term Moving Average, ' + epic, 
            label = '', 
            color = 'gray', 
            linestyle = 'dashed', 
            )

    ''' plot maximum adj close and ΔMA '''
    ax1.plot(
        dfEpic.index, 
        dfEpic['Normalised from t0', maxPriceLatestEpic], 
        color='red', 
        #legend=True, 
        linewidth=2.0, 
        label = maxPriceLatestEpicName, 
        )
    ax2.plot(
        dfEpic.index, 
        dfEpic['ShortEWMAChange', maxShortEWMALatestEpic] * 100, 
        color='red', 
        #legend=True, 
        linewidth=2.0, 
        label = 'Short Term, ' + maxShortEWMALatestEpicName, 
        )
    ax2.plot(
        dfEpic.index, 
        dfEpic['LongMAChange', maxLongMALatestEpic] * 100, 
        color='red', 
        linestyle = 'dashed', 
        linewidth=2.0, 
        label = 'Long Term, ' + maxLongMALatestEpicName, 
        )
    
    ax1.set(xlabel='', ylabel='Normalised Adj. Close')
    ax2.set(xlabel='Date', ylabel='\u0394% Rolling Average')
    ax1.set_title('FTSE100 Comparison')
        
    ax1.legend()
    ax1.grid()
    ax2.legend()
    ax2.grid()

    # equal y axis scale ΔMA with 10% padding (* 110) 
    maxMAChange = 0    
    for epic in epicAll:

        _ = abs_min_max(dfEpic['ShortEWMAChange', epic], 
                        dfEpic['LongMAChange', epic], 
                        )
        if _ > maxMAChange:
            maxMAChange = _
        
    ax2.set_ylim(-maxMAChange * 110, maxMAChange * 110)

    # encode plot into byte stream
    img = io.BytesIO()    
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()    
    
    # close plot to overwrite (when NOT running local module. ie when using controller.py)
    if __name__ != '__main__':
        plt.close()
        
    return plot_url, maxPriceLatestEpicName, maxShortEWMALatestEpicName, maxLongMALatestEpicName
    
def buy_or_sell(epic, t0, t1, shortTerm, longTerm):
    ''' create short term and long term buy/sell date lists '''
    
    if t1 == "today":
        t1 = dt.datetime.now()
    
    try:
        dfEpic = statistics_data(epic, t0, t1, shortTerm, longTerm)
    except (IOError, KeyError):
        failure = f"Failed to read symbol for {epic}. Please use symbol, \
        not company name"
        shortBuyDates, shortSellDates, longBuyDates, longSellDates = 0, 0, 0, 0
                
        return shortBuyDates, shortSellDates, longBuyDates, longSellDates, failure

    # buy, sell, hold
    ''' check if there is a buy/sell, if not, then hold
     list of all buy/sell dates (but only need last date for now)
    '''
    buyRequirement = 0.1
    sellRequirement = buyRequirement / 2
    
    shortBuyDates, shortSellDates, longBuyDates, longSellDates = [], [], [], []
    
    for index, change_in_shares in dfEpic['ShortEWMAChange', epic].iteritems():
        if change_in_shares > buyRequirement:
            shortBuyDates.append(index)
        elif change_in_shares < -sellRequirement:
            shortSellDates.append(index)   
            
    for index, change_in_shares in dfEpic['LongMAChange', epic].iteritems():
        if change_in_shares > buyRequirement:
            longBuyDates.append(index)
        elif change_in_shares < -sellRequirement:
            longSellDates.append(index)

    return shortBuyDates, shortSellDates, longBuyDates, longSellDates

def outcome_text(MAbuySellDays, buyOrSell, term):
    ''' outcome of the moving average, if less than 24 h then shortMAbuyDays = 0 '''

    if MAbuySellDays == 1 or MAbuySellDays == 0:
        MAoutcome = f"The last {buyOrSell} day was within 24 hours."
        
        MArecommend = f"Based on a {term} term moving average (\u0394MA) it is \
                      recommended to {buyOrSell} this share."
        
    elif MAbuySellDays > 1 and MAbuySellDays < 1.0E09:
        MAoutcome = f"The last {term} term {buyOrSell} day was {MAbuySellDays} days ago."
   
        MArecommend = f"This share has gained {buyOrSell}ing momentum based on a {term} \
        term moving average (\u0394MA). It is recommended to use the long term \
        trend due to short term fluctuations."

    else:
        MAoutcome = f"There were no {term} term {buyOrSell} days over the period selected. \
        It is not recommended to {buyOrSell} this share today."
      
        MArecommend = f"There are no {term} term {buyOrSell} periods, \
        based on a {term} term moving average (\u0394MA) it is not recommended \
        to {buyOrSell} this share."

    return MAoutcome, MArecommend

def short_term_text_results(epicAll, t0, t1, shortTerm, longTerm):
    ''' short term moving average text results using outcome_text() function '''

    #shortTerm, longTerm = MA_term(shortTerm, longTerm)
    shortBuyDates = buy_or_sell(epicAll, t0, t1, shortTerm, longTerm)[0]
    shortSellDates = buy_or_sell(epicAll, t0, t1, shortTerm, longTerm)[1]

    if __name__ == "__main__":
        print(f"short_term_text_results shortTerm variable :- {shortTerm}")
        print(f"short_term_text_results shortbuydates :- {shortBuyDates[-1]}")

    # last buy/sell day and text outcome. If there were no buy days over period
    # then set to 1E9 (ie a long time ago)
    if shortBuyDates:
        shortMAbuyDays = (dt.datetime.now() - shortBuyDates[-1]).days
    else:
        shortMAbuyDays = 1.0E09
    
    shortMAbuyOutcome = outcome_text(shortMAbuyDays, "buy", "short")[0]
    shortMAbuyRecommend = outcome_text(shortMAbuyDays, "buy", "short")[1]
        
    if shortSellDates:
        shortMAsellDays = (dt.datetime.now() - shortSellDates[-1]).days
    else:
        shortMAsellDays = 1.0E09
    
    shortMAsellOutcome = outcome_text(shortMAsellDays, "sell", "short")[0]
    shortMAsellRecommend = outcome_text(shortMAsellDays, "sell", "short")[1]

    ''' return only recommendation for buy or sell, but outcome for both;
        priority is to buy/not buy so return buy statements, rather than sell
    '''
    if shortMAbuyDays < shortMAsellDays:
        return shortMAbuyOutcome, shortMAbuyRecommend, shortMAsellOutcome, shortBuyDates
    else:
        return shortMAsellOutcome, shortMAsellRecommend, shortMAbuyOutcome, shortSellDates
    
def long_term_text_results(epicAll, t0, t1, shortTerm, longTerm):
    ''' long term moving average text results using outcome_text function '''
    
    longBuyDates = buy_or_sell(epicAll, t0, t1, shortTerm, longTerm)[2]
    longSellDates = buy_or_sell(epicAll, t0, t1, shortTerm, longTerm)[3]
    
    # last buy/sell day and text outcome
    if longBuyDates:
        longMAbuyDays = (dt.datetime.now() - longBuyDates[-1]).days
    else:
        longMAbuyDays = 1.0E09
        
    longMAbuyOutcome = outcome_text(longMAbuyDays, "buy", "long")[0]
    longMAbuyRecommend = outcome_text(longMAbuyDays, "buy", "long")[1]
        
    if longSellDates:
        longMAsellDays = (dt.datetime.now() - longSellDates[-1]).days
    else:
        longMAsellDays = 1.0E09
        
    longMAsellOutcome = outcome_text(longMAsellDays, "sell", "long")[0]
    longMAsellRecommend = outcome_text(longMAsellDays, "sell", "long")[1]
    
    ''' return only recommendation for buy or sell, but outcome for both;
        priority is to buy/not buy so return buy statements, rather than sell
    '''
    if longMAbuyDays < longMAsellDays:
        return longMAbuyOutcome, longMAbuyRecommend, longMAsellOutcome
    else:
        return longMAsellOutcome, longMAsellRecommend, longMAbuyOutcome

if __name__ == '__main__':
    ''' NOTES -
    anything that uses statistics_data() does not need to to call MA_term() (recalling)
       
    statistics_data_FTSE100All wont work for errors within epic symbols as it is a list, not a loop
    '''
       
    shortTerm, longTerm = 1, 3
    t0 = dt.datetime(2020, 1, 5)
    t1 = dt.datetime.now()
    
    epic = "AAPL"
    dfEpic = statistics_data(epic, t0, t1, shortTerm, longTerm)
    #dfEpicMax2 = FTSE100_plot(FTSE100EpicAll, FTSE100NameAll, dfEpic)
    print('\n\n')
    print(current_price(epic))
    #print(statistics_data_FTSE100All(epic, t0, t1, shortTerm, longTerm)[1])
    #FTSE100_plots(epicAll, epicNameAll, t0, t1, shortTerm, longTerm)
    #FTSE100_plots(epicAll, epicNameAll, t0, t1, shortTerm, longTerm)
    
    statistics_plots(epic, t0, t1, shortTerm, longTerm)
    FTSE100_plots(t0, t1, shortTerm, longTerm)
    print(FTSE100_EPIC())
    print('\n\n')
    #print(short_term_text_results(epic, t0, t1, shortTerm, longTerm))
    #print(current_price(epic))
    #short_term_text_results(epic, t0, t1, shortTerm, longTerm)
    #print(buy_or_sell(epic, t0, t1, shortTerm, longTerm))
    
    epicAll = FTSE100_EPIC()[0]
    print(current_price(epicAll))