from flask import Blueprint, render_template, request
from modules.scraper import get_data_all  # Import the scraper function

# Define the blueprint
hot_copper_bp = Blueprint('hot_copper', __name__)

# Define the route for Hot Copper
@hot_copper_bp.route('/', methods=["GET", "POST"])
def hot_copper():
    data = []  # Empty data to start with
    title = "Hot Copper"
    
    if request.method == "POST":
        ticker = request.form.get("ticker")  # Get the ticker from the form
        if ticker:
            data = get_data_all(ticker)  # Call the scraper with the ticker

    # Make sure 'title' and 'data' are passed to the template
    return render_template("hot_copper.html", title=title, data=data)

