print("--- Starting script ---")

from flask import Flask, render_template, request, redirect, url_for
from matplotlib._api import delete_parameter
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

load_dotenv()  # Load environment variables from .env file

DB_PASSWORD = os.getenv('DBMONGO_PASSWORD')  # Get the MongoDB password from environment variables

mongo_uri = f"mongodb+srv://vuongdylan3:{DB_PASSWORD}@stockcluster.ehakjrx.mongodb.net/?retryWrites=true&w=majority&appName=stockcluster"

app = Flask(__name__)   
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = client['stock_inventory']  # Connect to the MongoDB database
collection = db['stocks']  # Connect to the collection

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")  # Verify connection to MongoDB
except Exception as e:
    print(e)

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

        # Convert the time series data into a DataFrame
        df = pd.DataFrame.from_dict(time_series_data, orient='index')
        df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume',
            }, inplace=True)

        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)
        
        # Create graph of stock data and save it to static folder as png
        df['Close'].plot(label=symbol, xlabel="Date (Monthly)", ylabel="Closing Price ($)")
        plt.legend()
        plt.savefig('static/graph.png')

        return df, None 
    
    except requests.exceptions.RequestException as e:
        print(f"An error has occured with this request: {e}")
        return None, str(e)
    except Exception as e:
        print(f"An unexpected error has occured: {e}")
        return None, {e}

#Define main route for application
@app.route('/', methods=['GET', 'POST'])

def index():
    '''
        Display stock data and handle user input for stock symbol.
    '''
    API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

    if request.method == 'POST':
        #User submits form
        stock_symbol = request.form.get('symbol')
        if not stock_symbol:
            #Render page with error message if the form is empty
            return render_template('index.html', error="Please enter a stock symbol.")

        daily_data, error_message = get_daily_stock_data(API_KEY, stock_symbol)

        if error_message:
            #Pass error message to templateen
            return render_template('index.html', error=error_message)

        #Pass data and symbol to template after converting to HTML
        return render_template('index.html', data=daily_data.head(20).to_html(classes='table table-striped'), symbol=stock_symbol)

    # For GET request to intially load the page
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    '''
        Display the inventory of stocks
    '''
    try:
        # Fetch all stocks from the MongoDB collection
        stocks = collection.find()
        return render_template('inventory.html', stocks=list(stocks))
    except Exception as e:
        print(f"Error in /inventory: {e}")
        return f"Internal Server Error: {e}", 500


@app.route('/add_stock', methods=['POST'])
def add_stock():
    '''
        Add a new stock to the inventory
    '''
    stock_name = request.form['stock_name']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])

    stock = {
        'stock_name': stock_name,
        'quantity': quantity,
        'price': price
        }

    collection.insert_one(stock)  # Insert stock into MongoDB collection

    return redirect(url_for('inventory'))  # Redirect to index page after adding stock))

@app.route('/change_stock/<stock_id>', methods=['POST'])
def change_stock(stock_id):
    '''
        Update or delete a stock in the inventory based on user action
    '''
    action = request.form['action']

    if action == 'update':
        # Update stock quantity and price
        new_quantity = int(request.form['new_quantity'])
        new_price = float(request.form['new_price'])

        collection.update_one(
            { '_id': ObjectId(stock_id) },
            { '$set': { 'quantity': new_quantity, 'price': new_price }}
        )

    elif action == 'delete':
        # Delete stock from the inventory
        collection.delete_one({ '_id': ObjectId(stock_id) })

    return redirect(url_for('inventory'))

if __name__ == '__main__':
    app.run(debug=True)