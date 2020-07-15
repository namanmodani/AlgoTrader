import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import numpy as np

import datetime

def gs_factors(tickerId, startDate, endDate):
    if type(tickerId) != str or type(startDate) != str or type(endDate) != str:
        raise "Invalid input type(s), must be strings"

    auth_data = {
        'grant_type'    : 'client_credentials',
        'client_id'     : 'CLIENT_ID',
        'client_secret' : 'CLIENT_SECRET', #Authentication for Goldman Sachs API
        'scope'         : 'read_product_data read_financial_data read_content'
    }
    session = requests.Session()
    auth_request = session.post('https://idfs.gs.com/as/token.oauth2', data = auth_data)
    access_token_dict = json.loads(auth_request.text)
    access_token = access_token_dict['access_token']
    session.headers.update({'Authorization':'Bearer '+ access_token})
    request_url = "https://api.marquee.gs.com/v1/data/USCANFPP_MINI/query"
    request_query = {
                    "where": {
                        "ticker": [tickerId]
                    },
                    "startDate": startDate,
                    "endDate": endDate
               }
    request = session.post(url=request_url, json=request_query)
    results = json.loads(request.text)

    return results

def gs_df(aDict):
    alist = aDict['data']
    compiledDict = {}
    for dicts in alist:
        compiledDict[dicts["date"]] = [dicts['financialReturnsScore']
        , dicts['growthScore'], dicts['multipleScore'], dicts['integratedScore']]
    gs_df = pd.DataFrame.from_dict(compiledDict, orient='index', columns=['Financial Returns Score'
        , 'Growth Score', 'Multiple Score', 'Integrated Score'])

    return gs_df

def get_rolling_mean(df, window):

    return df.rolling(window=window).mean()

def get_rolling_std(df, window):
    return df.rolling(window=window).std()

def get_bollinger_bands(rm, rstd):

    upper_band = rm + rstd*2
    lower_band = rm - rstd*2
    return upper_band, lower_band

def plot_data_gs(df, title="Stock Data"):
    plt.figure(1)
    ax = df.plot(title=title, fontsize = 14)
    ax.set_xlabel("Date")
    if "Price" in df.columns.values.tolist():
        ax.set_ylabel("Price")
    else:
        ax.set_ylabel("Score")
    plt.show()


def get_price_data(tickerId):
    request_url = "https://api.iextrading.com/1.0/stock/" +tickerId+"/chart/6m"
    request = requests.get(request_url)
    results = json.loads(request.text)
    compiledDict = {}
    for adict in results:
        compiledDict[adict['date']] = adict['close']
    price_df = pd.DataFrame.from_dict(compiledDict, orient='index', columns=["Price"])
    return price_df

def main():

    tickerId = input("Enter the ticket ID")


    df = get_price_data(tickerId)
    rm = get_rolling_mean(df, window = 20)
    rst = get_rolling_std(df, window = 20)

    upper_band, lower_band = get_bollinger_bands(rm, rst)

    ax = df["Price"].plot(title = "Bollinger Bands", label = tickerId)
    rm.plot(label ='rolling mean', ax = ax)
    lower_band.plot(label = "lower band", ax = ax)
    upper_band.plot(label = "upper band", ax = ax)


    plot_data_gs(gs_df(gs_factors(tickerId, "yyyy-mm-dd", "yyyy-mm-dd")))


if __name__== "__main__":
  main()
