from datetime import datetime
from datetime import timedelta
import requests
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
news_apikey = os.environ.get("NEWS_APIKEY")
stock_apikey = os.environ.get("STOCK_APIKEY")

curr_time = datetime.now()

yesterday = (curr_time - timedelta(days=1)).date()
YESTERDAY = str(yesterday)

day_before_yesterday = yesterday - timedelta(days=1)
DAY_BEFORE_YESTERDAY = str(day_before_yesterday)


stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_apikey,
}
stock_response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()
closing_price_yesterday = float(stock_data["Time Series (Daily)"][YESTERDAY]["4. close"])
closing_price_day_yesterday = float(stock_data["Time Series (Daily)"][DAY_BEFORE_YESTERDAY]["4. close"])

stock_change = abs(closing_price_yesterday - closing_price_day_yesterday)
stock_percent = (stock_change / closing_price_day_yesterday) * 100

if stock_percent > 1:
    news_parameters = {
        "apikey": news_apikey,
        "q": COMPANY_NAME,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()

    data = [(msg["title"], msg["description"]) for msg in news_data["articles"][:3]]
    print(data[0][1])

    account_sid = os.environ.get("ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    for sent_message in data:
        message = client.messages \
                        .create(
                             body=f"Headline: {sent_message[0]}\nBrief: {sent_message[1]}",
                             from_='+17698881282',
                             to='+916302374604'
                         )

        print(message.sid)


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

