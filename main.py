# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
import json
from datetime import datetime
from dateutil.relativedelta import *
from flask import Flask, render_template
import finnhub
import time

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
finnhub_client = finnhub.Client(api_key="c8555vaad3i9e9m0ktfg")


@app.route('/')
def hello():
    return app.send_static_file('home.html')

@app.route('/ticker/<ticker>')
def lookup_by_ticker(ticker):
    response = finnhub_client.company_profile2(symbol=ticker)
    #print(response)
    return response

@app.route('/summary/<ticker>')
def stock_summary(ticker):
    response = finnhub_client.quote(ticker)
    recent_trends = recommendation_trends(ticker)
    #print(response)
    #print(recent_trends)

    merged_dict = response.copy()
    merged_dict.update(recent_trends)
    #print(merged_dict)
    return merged_dict

@app.route('/recommendation/<ticker>')
def recommendation_trends(ticker):
    response = finnhub_client.recommendation_trends(symbol=ticker)
    #print(response)
    return response[0]

@app.route('/stockcandles/<ticker>')
def stockcandles(ticker):
    today = datetime.today()
    print(today)
    #print("unix_timestamp => ",(time.mktime(today.timetuple())))
    six_months_one_day_ago_date = today + relativedelta(months=-6)


    print(six_months_one_day_ago_date)
    #print("unix_timestamp => ",(time.mktime(six_months_one_day_ago_date.timetuple())))

    from_date = int(round(time.mktime(six_months_one_day_ago_date.timetuple())))
    to_date = int(round(time.mktime(today.timetuple())))

    response = finnhub_client.stock_candles(ticker, 'D', from_date, to_date)
    #print(response)

    fields_needed = ['t', 'v']
    _date = response['t']
    volume = response['v']
    price = response['c']

    time_volume = merge_lists(_date, volume)
    time_volume = sorted(time_volume, key=lambda x: x[0])
    time_price = merge_lists(_date, price)
    time_price = sorted(time_price, key=lambda x: x[0])

    result = json.dumps([time_volume, time_price])
    #print(result)
    return result

def merge_lists(list1, list2):
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list

@app.route('/companynews/<ticker>')
def company_news(ticker):
    today = datetime.today().date()
    thirty_days_ago_date = today + relativedelta(days=-30)
    print(today)
    result = finnhub_client.company_news(ticker, _from=thirty_days_ago_date, to=today)
    return json.dumps(result)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
