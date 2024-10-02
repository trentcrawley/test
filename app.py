from flask import Flask, redirect, url_for
from modules.register_turnover import register_turnover_bp  # Import Register Turnover blueprint
from modules.hot_copper import hot_copper_bp  # Import Hot Copper blueprint

app = Flask(__name__)

# Register both blueprints
app.register_blueprint(register_turnover_bp, url_prefix='/register_turnover')
app.register_blueprint(hot_copper_bp, url_prefix='/hot_copper')

# Root route to home page, you can choose to redirect to either of the pages
@app.route("/")
def home():
    return redirect(url_for('register_turnover.register_turnover'))  # Or customize based on your preference

if __name__ == "__main__":
    app.run(debug=True)


