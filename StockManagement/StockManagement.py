print("--- Starting script ---")

from flask import Flask, render_template, request
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)   

def get_daily_stock_data(api_key, symbol):
    '''
        Fetch daily stock data from Alpha Vantage API.

        param p1: api_key: Your Alpha Vantage API key.
        param p2: symbol: The stock symbol to fetch data for.
    '''

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if 'Error Message' in data or 'Note' in data:
            #Handle API errors or informational messages
            error_message = data.get('Error Message', data.get('Note', 'An error occurred while fetching data.'))
            print(f"API Error/Info: {error_message}")
            return None, error_message

        time_series_data = data.get('Time Series (Daily)')
        if not time_series_data:
            print("No data found for the given symbol.")
            return None, "No data found for the given symbol."

        df = pd.DataFrame.from_dict(time_series_data, orient='index')
        df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'volume',
            }, inplace=True)

        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)
        
        return df, None, 
    
    except requests.exceptions.RequestException as e:
        print(f"An error has occured with this request: {e}")
        return None, str(e)
    except Exception as e:
        print(f"An unexpected error has occured: {e}")
        return None, {e}

#Define main route for application
@app.route('/', methods=['GET', 'POST'])

def index():

    API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

    if request.method == 'POST':
        #User submits form
        stock_symbol = request.form.get('symbol')
        if not stock_symbol:
            #Render page with error message if the form is empty
            return render_template('index.html', error="Please enter a stock symbol.")

        daily_data, error_message = get_daily_stock_data(API_KEY, stock_symbol)

        if error_message:
            #Pass error message to template
            return render_template('index.html', error=error_message)

        #Pass data and symbol to template after converting to HTML
        return render_template('index.html', data=daily_data.head(10).to_html(classes='table table-striped'), symbol=stock_symbol)

    # For GET request to intially load the page
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)