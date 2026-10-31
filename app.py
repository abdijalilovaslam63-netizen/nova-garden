import os
import sys
import subprocess
from flask import Flask, send_from_directory

app = Flask(__name__)

bot_process = subprocess.Popen([sys.executable, "bot.py"])

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/health")
def health():
    return "NOVA ishlayapti!"

