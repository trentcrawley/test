from flask import Flask, render_template, request
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == "POST":
        ticker = request.form.get("ticker")
        exchange = request.form.get("exchange")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Handle single-day date range by extending the end date by 1 day
        #if start_date == end_date:
        # add one day as enddate not inclusive
        end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        ticker_with_exchange = f"{ticker}.{exchange}" if exchange else ticker
        stock_data = yf.Ticker(ticker_with_exchange)
        history = stock_data.history(start=start_date, end=end_date)

        if not history.empty:
            # Format the index as strings (YYYY-MM-DD) to avoid time component
            history.index = history.index.strftime('%Y-%m-%d')

            # Get shares outstanding
            shares_outstanding = stock_data.info.get('sharesOutstanding', 'N/A')

            if shares_outstanding == 'N/A':
                register_turnover = None  # Handle missing data scenario
            else:
                # Calculate register turnover as the cumulative sum of volume / shares outstanding
                register_turnover = (history['Volume'] / shares_outstanding).cumsum()

            # VWAP calculation
            #vwap = (history['Close'] * history['Volume']).cumsum() / history['Volume'].cumsum()
            typical_price = (history['High'] + history['Low'] + history['Close']) / 3
            vwap = (typical_price * history['Volume']).cumsum() / history['Volume'].cumsum()
            # Create subplots for price and volume
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05, 
                                specs=[[{"secondary_y": True}], [{}]])

            # Candlestick chart
            fig.add_trace(go.Candlestick(x=history.index,
                                         open=history['Open'],
                                         high=history['High'],
                                         low=history['Low'],
                                         close=history['Close'],
                                         name='Candlestick'),
                          row=1, col=1)

            # Volume chart
            fig.add_trace(go.Bar(x=history.index, y=history['Volume'], name="Volume"),
                          row=2, col=1)

            # VWAP line (no dots, smooth line)
            fig.add_trace(go.Scatter(x=history.index, y=vwap, mode='lines', name="VWAP", line=dict(color='orange')),
                          row=1, col=1)

            # Register Turnover line (join dots for multi-day data)
            if register_turnover is not None:
                fig.add_trace(go.Scatter(x=history.index, y=register_turnover, mode='lines+markers', name="Register Turnover",
                                         line=dict(color='green')),
                              row=1, col=1, secondary_y=True)

                # Get the most recent register turnover value for the title (formatted as %)
                latest_register_turnover = register_turnover.iloc[-1] * 100
            else:
                latest_register_turnover = 'N/A'

            # Update layout for dark theme and title with most recent register turnover value in %
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='white',
                title=f'{ticker} Register Turnover: {latest_register_turnover:.2f}%',
                xaxis_rangeslider_visible=False,
                height=750   # Disable the range slider
            )

            # Ensure the dates are displayed without time (already converted to strings)
            fig.update_xaxes(type='category')

            # Adjust secondary y-axis settings
            fig.update_yaxes(title_text="Price", secondary_y=False, row=1, col=1)
            fig.update_yaxes(title_text="Register Turnover", secondary_y=True, row=1, col=1)

            plot_html = fig.to_html(full_html=False)
            return render_template("index.html", plot_html=plot_html, today=today, end_date=end_date,
                                   ticker=ticker, exchange=exchange, start_date=start_date)

        else:
            # If no data is returned, still show the form with a message
            return render_template("index.html", today=today, end_date=end_date, 
                                   ticker=ticker, exchange=exchange, start_date=start_date,
                                   error_message="No data available for the selected range.")

    return render_template("index.html", today=today, end_date=today)

if __name__ == "__main__":
    app.run(debug=True)
