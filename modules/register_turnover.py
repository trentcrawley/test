from flask import Blueprint, render_template, request
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Import the Google Drive API class and the download function
from modules.driveupload import GoogleDriveAPI, get_tracked_ticker_from_cloud

# Define the Blueprint for Register Turnover
register_turnover_bp = Blueprint('register_turnover', __name__)

CSV_FILE_PATH = os.path.join(os.getcwd(), 'tracking.csv')
file_downloaded = False
@register_turnover_bp.before_app_request
def download_tracking_file():
    global file_downloaded
    """Download the latest tracking.csv from Google Drive only once, on the first request."""
    
    # Check if the file has been downloaded
    if not file_downloaded:
        get_tracked_ticker_from_cloud(CSV_FILE_PATH)        
        # Set the flag to True after the file has been downloaded
        file_downloaded = True

@register_turnover_bp.route("/", methods=["GET", "POST"])
def register_turnover():
    today = datetime.today().strftime('%Y-%m-%d')
    ticker, exchange, start_date, end_date = "", "", today, today

    # Load tracking.csv
    if os.path.exists(CSV_FILE_PATH):
        tracking_data = pd.read_csv(CSV_FILE_PATH)
        tracking_data = tracking_data[['ticker', 'tracked_since']].rename(columns={'tracked_since': 'eventdate'})
        tracking_html = tracking_data.to_html(index=False, classes='table table-striped', border=0)
    else:
        tracking_html = "<p>No tracking data found.</p>"

    if request.method == "POST":
        ticker = request.form.get("ticker")
        exchange = request.form.get("exchange")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Add 1 day to the end date (since yFinance is not inclusive of the end date)
        end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        ticker_with_exchange = f"{ticker}.{exchange}" if exchange else ticker
        stock_data = yf.Ticker(ticker_with_exchange)
        history = stock_data.history(start=start_date, end=end_date)

        if not history.empty:
            # Format the index as strings (YYYY-MM-DD)
            history.index = history.index.strftime('%Y-%m-%d')

            # Get shares outstanding
            shares_outstanding = stock_data.info.get('sharesOutstanding', 'N/A')
            register_turnover = None

            if shares_outstanding != 'N/A':
                # Calculate register turnover
                register_turnover = (history['Volume'] / shares_outstanding).cumsum()

            # VWAP calculation
            typical_price = (history['High'] + history['Low'] + history['Close']) / 3
            vwap = (typical_price * history['Volume']).cumsum() / history['Volume'].cumsum()
            latest_register_turnover = register_turnover.iloc[-1] * 100 if register_turnover is not None else 0

            # Create subplots with secondary y-axis for Register Turnover
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05,
                specs=[[{"secondary_y": True}], [{}]]
            )

            # Add Candlestick chart
            fig.add_trace(go.Candlestick(x=history.index, open=history['Open'], high=history['High'],
                                         low=history['Low'], close=history['Close'], name='Candlestick'),
                          row=1, col=1)

            # Add VWAP line (smooth)
            fig.add_trace(go.Scatter(x=history.index, y=vwap, mode='lines', name="VWAP", line=dict(color='orange')),
                          row=1, col=1)

            # Add Register Turnover (secondary y-axis)
            if register_turnover is not None:
                fig.add_trace(go.Scatter(x=history.index, y=register_turnover, mode='lines+markers', name="Register Turnover", line=dict(color='green')), row=1, col=1, secondary_y=True)

            # Add Volume bar chart
            fig.add_trace(go.Bar(x=history.index, y=history['Volume'], name="Volume"), row=2, col=1)

            # Set layout, disable range slider
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='white',
                title=f'{ticker} Register Turnover: {latest_register_turnover:.2f}%',
                xaxis_rangeslider_visible=False,
                height=750
            )

            # Ensure date axis is properly formatted
            fig.update_xaxes(type='category')

            # Adjust y-axis labels
            fig.update_yaxes(title_text="Price", secondary_y=False, row=1, col=1)
            fig.update_yaxes(title_text="Register Turnover", secondary_y=True, row=1, col=1)

            plot_html = fig.to_html(full_html=False)
            return render_template("index.html", plot_html=plot_html, today=today, ticker=ticker, exchange=exchange, start_date=start_date, end_date=end_date, tracking_html=tracking_html)

    return render_template("index.html", today=today, ticker=ticker, exchange=exchange, start_date=start_date, end_date=end_date, tracking_html=tracking_html)

if __name__ == "__main__":
    app.run(debug=True)
