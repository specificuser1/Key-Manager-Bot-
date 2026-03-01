from flask import Flask, render_template
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

def run_dashboard():
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
