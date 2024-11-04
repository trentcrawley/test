# from flask import Flask, redirect, url_for
# from modules.register_turnover import register_turnover_bp  # Import Register Turnover blueprint
# from modules.driveupload import get_tracked_ticker_from_cloud  # Correct the import
# import os

# app = Flask(__name__)

# # Register the blueprint
# app.register_blueprint(register_turnover_bp, url_prefix='/register_turnover')

# # Dynamically get the current working directory and use it for tracking.csv
# CSV_FILE_PATH = os.path.join(os.getcwd(), 'tracking.csv')
# CSV_FILE_PATH_SOI = os.path.join(os.getcwd(), 'soi.csv')
# first_request_made = False

# @app.before_request
# def before_request_func():
#     global first_request_made
#     if not first_request_made:
#         # Download tracking.csv from Google Drive only on the first request
#         if not os.path.exists(CSV_FILE_PATH):
#             get_tracked_ticker_from_cloud(CSV_FILE_PATH,"tracking")
#         if not os.path.exists(CSV_FILE_PATH_SOI):
#             get_tracked_ticker_from_cloud(CSV_FILE_PATH_SOI,"soi")
#         first_request_made = True

# # Root route
# @app.route("/")
# def home():
#     return redirect(url_for('register_turnover.register_turnover'))

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, redirect, url_for
from modules.register_turnover import register_turnover_bp  # Import Register Turnover blueprint
from modules.driveupload import get_tracked_ticker_from_cloud  # Correct the import
import os

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(register_turnover_bp, url_prefix='/register_turnover')

# Dynamically get the current working directory and use it for tracking.csv
CSV_FILE_PATH = os.path.join(os.getcwd(), 'tracking.csv')
CSV_FILE_PATH_SOI = os.path.join(os.getcwd(), 'soi.csv')
first_request_made = False

# Root route
@app.route("/")
def home():
    global first_request_made
    if not first_request_made:
        # Download tracking.csv from Google Drive only on the first request
        if not os.path.exists(CSV_FILE_PATH):
            get_tracked_ticker_from_cloud(CSV_FILE_PATH, "tracking")
        if not os.path.exists(CSV_FILE_PATH_SOI):
            get_tracked_ticker_from_cloud(CSV_FILE_PATH_SOI, "soi")
        first_request_made = True
    return redirect(url_for('register_turnover.register_turnover'))

if __name__ == "__main__":
    app.run(debug=True)