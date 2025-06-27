# A Stock Viewer Application 
This is a work in progress build with the intentions of eventually letting the user manage their stock portfolio and have a more in-depth view of their portfolio.
As of now, it is a simple stock viewer.

## Features
- View stock prices
- See open, close, high, low prices, and volume amount
- Search for stocks by symbol
- Stock prices are adjusted daily

## Technologies Used
HTML, Python, Flask, Alpha Vantage API

## How to Run:
In order to run this application, you must have an Alpha Vantage API key

You may generate a free Alpha Vantage API key at https://www.alphavantage.co/support/#api-key

You must also type the following commands in your terminal:

- env/Scripts/activate
- $env:FLASK_APP = 'StockManagement.py'
- $env:FLASK_ENV = 'development'
- flask run

If the app still doesn't run, try executing this command into your windows terminal:
- Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Unsure if this can be made easier, will be looking for solutions.

## Lessons Learned
This was my first experience trying to make a full blown web application outside of my console text projects I did in school. There was a lot to learn, including how to set up Flask and properly route the app and handle errors. I was also exposed to pandas which is a convenient package to nicely format data tables. Lastly, I learned about how I could render HTML templates, all of which was completely foreign to me before this. I still plan on further improving this project, adding more features and possibly experimenting in integrating other technologies.

