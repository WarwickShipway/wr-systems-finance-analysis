from wtforms import Form, FloatField, IntegerField, StringField, DecimalField, validators
from wtforms.fields.html5 import DateField
import datetime as dt


''' VALIDATORS
startdate must be before end date
add in error message using flask
datetime validator

ticker - unknown ticker works, empty ticker works

dates - validators do not work, try a calendar
        update: using html5 - note error in wtform input format (flask issue)

short term - > 12 works, and short > long works
             strings raise validator 
             
long term - > 60 works. Dont need the number validator, can do custom
             strings raise validator 
             
combinations of short term / long term work
 strings on both long term and short term do not work, due to or statements
 update now works for strings on both terms
'''


def short_term_error(form, field):
    ''' escape for short term period that is too long. Long term captured in 
        another function because it will raise error on both input forms otherwise
    '''
    shortTerm = form.shortTerm.data
    if shortTerm > 12:
        raise validators.ValidationError(f'It is unrealistic to have moving average term over \
                                         {round(shortTerm / 12,1)} years. \
                                         Please define a term < 12 months'
                                         )
    try:
        float(shortTerm)
    except:
        raise validators.ValidationError(f'It is unrealistic to have moving average term over \
                                         {round(shortTerm / 12,1)} years. \
                                         Please define a term < 12 months'
                                        )
    
def long_term_error(form, field):
    longTerm = form.longTerm.data
    if longTerm > 12 * 5:
        raise validators.ValidationError(f'It is unrealistic to have moving \
                                         average term over {round(longTerm / 12,1)} \
                                         years. Please define a term < 60 months'
                                        )

def term_gap(form, field):
    shortTerm = form.shortTerm.data
    longTerm = form.longTerm.data
    
    if shortTerm == type(float):
        if shortTerm > longTerm \
        or longTerm < shortTerm \
        or shortTerm <= 0 \
        or longTerm <= 0:
            raise validators.ValidationError('Short term should be less than long term')

class InputForm(Form):
    epic = StringField(description = 'EPIC:',        
                       label = 'eg. TSLA, AAPL, FB, GOOG, BP.L, XUKS.L',
                       default = 'BP.L',
                       validators = [validators.InputRequired()]
                      )
    
    t0 = DateField(description = 'Start Date:',
                   format = "%Y-%m-%d", 
                   default = dt.datetime(2019, 1, 1), 
                   #default=dt.datetime.now().strftime("2019-10-10"), 
                  )
        
    t1 = DateField(description = 'End Date:', 
                   format = "%Y-%m-%d", 
                   default = dt.datetime.now(), 
                  )
    
    shortTerm = FloatField(description = 'Short Term Moving Average:',
                           label = 'Period over which a moving average is calculated, in months.\
                           Common term is 0.5, 1, 2.',
                           default = 1,
                           validators = [validators.DataRequired(message="Please input a number, \
                                                                 0 < period <= 1 year (12)"),
                                                                 #validators.NumberRange(0, 12),
                                                                 short_term_error,
                                                                 term_gap,                           
                                        ]
                           )
    
    longTerm = FloatField(
               description = 'Long Term Moving Average:',
               label = 'Period over which a moving average is calculated, in months. \
               Common term is 4, 5, 9.',
               default = 4,
               validators = [validators.DataRequired(message="Please Input a number, \
                                                     0 < period <= 5 years (60 months)"
                                                     ),
                                                     #validators.NumberRange(0, 12 * 5),
                                                     long_term_error,
                                                     term_gap,
                            ]                       
                          )