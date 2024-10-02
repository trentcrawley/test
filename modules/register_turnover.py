from flask import Blueprint, render_template, request
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta

# Define the Blueprint for Register Turnover
register_turnover_bp = Blueprint('register_turnover', __name__)

@register_turnover_bp.route("/", methods=["GET", "POST"])
def register_turnover():
    today = datetime.today().strftime('%Y-%m-%d')

    # Default form values for GET request
    ticker = ""
    exchange = ""
    start_date = today
    end_date = today

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
            return render_template("index.html", plot_html=plot_html, today=today, ticker=ticker, exchange=exchange, start_date=start_date, end_date=end_date)

    return render_template("index.html", today=today, ticker=ticker, exchange=exchange, start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    app.run(debug=True)
