from datetime import date, datetime

import datetime
import json
import requests
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template

application = Flask(__name__)

@application.route("/")
def index():
    return render_template('index.html')

@application.route("/data/<string:symbol>", methods=['GET'])
def getSymbol(symbol):
    headers = {'Content-Type': 'application/json'}
    company_outlook = requests.get("https://api.tiingo.com/tiingo/daily/" + symbol + "?token=196e5f07943589b362493421eeb94fff8af1e993", headers=headers)
    if (company_outlook.json() == {'detail' : 'Not found.'}):
        return json.dumps(['fail'])
    stock_summary = requests.get("https://api.tiingo.com/iex/?tickers=" + symbol + "&token=196e5f07943589b362493421eeb94fff8af1e993", headers=headers)
    start_date = date.today() + relativedelta(months=-6)
    history = requests.get("https://api.tiingo.com/iex/" + symbol + "/prices?startDate=" + str(start_date) + "&resampleFreq=12hour&columns=open,high,low,close,volume&token=196e5f07943589b362493421eeb94fff8af1e993", headers=headers)
    charts = []
    for record in history.json():
        timestamp = int((datetime.datetime.strptime(record['date'], "%Y-%m-%dT%H:%M:%S.000Z") + datetime.timedelta(hours=-16)).timestamp() * 1000)
        charts.append([timestamp, record['close'], record['volume']])
    all_news = requests.get("https://newsapi.org/v2/everything?q=" + symbol + "&apiKey=762ed7ca638c4da5abde56e6b81c15d9", headers=headers)
    five_articles = []
    i = 0
    for article in all_news.json()['articles']:
        if (i == 5):
            break
        if all(v is not None for v in [article['title'], article['url'], article['urlToImage'], article['publishedAt']]):
            five_articles.append([article['title'], article['url'], article['urlToImage'], article['publishedAt']])
            i+=1
    return json.dumps([{'company' : company_outlook.json()}, {'stock' : stock_summary.json()}, {'chart' : charts}, {'news' : five_articles}])

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()