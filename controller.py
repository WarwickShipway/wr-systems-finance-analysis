from model import InputForm
from flask import Flask, render_template, request

#try:
#    from compute import compute
#    from compute import time_stamp
#except:
import compute


''' 
ctrl+shft+R to reload presentation, as it caches the css
ctrl+shft+I in browser (Chrome) to open dev tools
ctrl+U in browser (Chrome) to view source html
'''

app = Flask(__name__)
app.config['SECRET KEY'] = '-'

''' TO DO




try the calendar in a new file     --  done
add this to heroku
look for data scientist course




have a loading bar for FTSE100 data as it takes a long time
make a timer for python calculations and server speed (total - python?)?

the return erros have become muddled, eg current_price[1] inside view, but others are
inside compute. Some errors are in compute.py, some in model.py, for development

better to convert epic non list to list in model.py? Done in statistics_plots()
# convert symbol column to list
tickers = df['Symbol'].values.tolist()
what about epics that do not exist during the start date t0 (exception should handle it)

how to better gauge the buy/sell requirements?

make nice make a pic for the top of html

for FTSE100 plots and normal plots - combine and have an if statement for multiple?

have a statement saying if bought short term/long term ago, x would be profit / lost
add a test method - find a buy date historically, and find how long it took to 
return say 2%, 10%

have more acceptance of dates, eg not "." but "-" as well - seems datetime 
accept this already

make a clearer method for generating the text, and short_term_text_results().

do some crossover analysis - 
    Another strategy is to apply two moving averages to a chart: one longer and 
    one shorter.
    When the shorter-term MA crosses above the longer-term MA, it's a buy signal, 
     as it indicates that the trend is shifting up. This is known as a "golden cross."
    Meanwhile, when the shorter-term MA crosses below the longer-term MA, it's a 
    sell signal,
     as it indicates that the trend is shifting down. This is known as a 
     "dead/death cross."

    Lag is the time it takes for a moving average to signal a potential reversal. 
    Recall that, as a general guideline, when the price is above a moving average,
     the trend is considered up. So when the price drops below that moving average, 
     it signals a potential reversal based on that MA. A 20-day moving average will 
     provide many more "reversal" signals than a 100-day moving average. 
    
    While moving averages are useful enough on their own, they also form the basis 
     for other technical indicators such as the moving average convergence 
     divergence (MACD).
     
drop down menu for different analyses?
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    
    if request.method == 'POST' and form.validate():
        if request.form['button'] == 'stat_plots':
            statistics_plots = compute.statistics_plots(form.epic.data, form.t0.data, form.t1.data, form.shortTerm.data, form.longTerm.data)
            time_stamp = compute.time_stamp()
            current_price = compute.current_price(form.epic.data)
            short_term_text_results = compute.short_term_text_results(form.epic.data, form.t0.data, form.t1.data, form.shortTerm.data, form.longTerm.data)
            long_term_text_results = compute.long_term_text_results(form.epic.data, form.t0.data, form.t1.data, form.shortTerm.data, form.longTerm.data)
            short_term_type = (form.shortTerm.data, type(form.shortTerm.data))
            FTSE100_plots = None # to avoid long dataframe generation time
            FTSE100_EPIC = compute.FTSE100_EPIC()
            
        elif request.form['button'] == 'FTSE100_plots':
            statistics_plots = None
            time_stamp = compute.time_stamp()
            current_price = compute.current_price(form.epic.data)
            short_term_text_results = None
            long_term_text_results = None
            short_term_type = None
            FTSE100_plots = compute.FTSE100_plots(form.t0.data, form.t1.data, form.shortTerm.data, form.longTerm.data)
            FTSE100_EPIC = compute.FTSE100_EPIC()
   
    else:
        statistics_plots = None
        time_stamp = None
        current_price = None
        short_term_text_results = None
        long_term_text_results = None
        short_term_type = None
        FTSE100_plots = None
        FTSE100_EPIC = None

    return render_template( 'view.html', 
                            zip=zip, 
                            form=form, 
                            current_price=current_price, 
                            statistics_plots=statistics_plots, 
                            FTSE100_plots=FTSE100_plots, 
                            time_stamp=time_stamp, 
                            short_term_text_results=short_term_text_results, 
                            long_term_text_results=long_term_text_results, 
                            short_term_type=short_term_type, 
                            FTSE100_EPIC=FTSE100_EPIC
                          )
    
if __name__ == '__main__':
    app.run(debug=True)