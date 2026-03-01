from flask import Flask, render_template
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

def run_dashboard():
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
