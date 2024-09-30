from flask import Flask, render_template, request
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # Get today's date in the format YYYY-MM-DD
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == "POST":
        ticker = request.form.get("ticker")
        exchange = request.form.get("exchange")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Combine ticker with exchange (if needed)
        ticker_with_exchange = f"{ticker}.{exchange}" if exchange else ticker

        # Retrieve stock data
        stock_data = yf.Ticker(ticker_with_exchange)
        history = stock_data.history(start=start_date, end=end_date)

        # Convert the datetime index to just date (YYYY-MM-DD)
        history.index = history.index.strftime('%Y-%m-%d')

        # Create a candlestick chart using Plotly
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=history.index,
                                     open=history['Open'],
                                     high=history['High'],
                                     low=history['Low'],
                                     close=history['Close'],
                                     name="Candlestick"))

        # Update x-axis: Remove range slider and format dates without time
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_xaxes(type='category', tickformat='%Y-%m-%d', tickangle=-45)

        # Save plot as HTML to embed in the template
        plot_html = fig.to_html(full_html=False)

        # Pass form data back to the template so it persists after submission
        return render_template("index.html", plot_html=plot_html, today=today, end_date=end_date)

    # On GET, pass today's date as the default end date
    return render_template("index.html", plot_html=None, today=today, end_date=today)

if __name__ == "__main__":
    app.run(debug=True)
