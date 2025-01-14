#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 13:15:13 2021
@author: ads2137
"""

import requests
import pandas as pd
import numpy as np
import os
from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from boto.s3.connection import S3Connection
from dotenv import load_dotenv
load_dotenv()  

#s3=S3Connection(os.environ['APIKEY'])
alphav_key = os.environ.get('API_KEY')




def pull_stock_info(symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        "function": 'TIME_SERIES_DAILY_ADJUSTED',
        "symbol": symbol,
        "apikey": str(alphav_key),
        "outputsize": "compact"} 
    r = requests.get(url,params)
    data = r.json()
    return data


def get_month_dates(data):
    dates=data['Time Series (Daily)']
    date_strings=list(dates.keys())
    date_list=[np.datetime64(date) for date in date_strings]
    first_day = date_list[0]
    lastMonth = first_day - np.timedelta64(32,'D')
    month_mask=[date>lastMonth for date in date_list]
    month_indices=np.where(month_mask)[0]
    date_list=date_list[month_indices[0]:month_indices[-1]]
    return dates,date_list

def get_prices(dates,date_list,datatype):
    prices=[]
    for i in range (0,len(date_list)):
        if datatype=='Adjusted Closing Price':
            prices.append(list(list(dates.values())[i].values())[4])
        elif datatype=='Closing Price':
            prices.append(list(list(dates.values())[i].values())[3])
        elif datatype=='Opening Price':
            prices.append(list(list(dates.values())[i].values())[0])
        prices = [float(i) for i in prices]
    return prices

def plot_app_inputs(symbol,datatype):
    
    data=pull_stock_info(symbol)
    dates, date_list=get_month_dates(data)
    prices=get_prices(dates,date_list,datatype)
    
    # create a new plot with a title and axis labels
    p = figure(title=datatype+':  '+symbol, x_axis_label="Time (Days)", y_axis_label=datatype,x_axis_type='datetime')

    # add a line renderer with legend and line thickness
    p.line(date_list,prices, line_width=2)

    # show the results
    html = file_html(p, CDN, "my plot")
    return html


app = Flask(__name__)

app.vars={}

@app.route('/', methods=['GET','POST'])
def input_to_app():
    if request.method == 'GET':
   
        return render_template('input.html')
    else:
       
        #please_gimme=request.form
        #print(please_gimme)
        app.vars['symbol'] = request.form['symbol']
        app.vars['data'] = request.form['data']
        html=plot_app_inputs(app.vars['symbol'],app.vars['data'])
        return html



#@app.route('/about')
#def about():
 # return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

