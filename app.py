from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
from datetime import date

app= Flask(__name__)
DB_PATH = Path(__file__).with_name("expenses.db")
 
def get_db():
     conn = sqlite3.connect(DB_PATH)
     conn.row_factory = sqlite3.Row
     return conn

def setup_database():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL
        )
""")

@app.route("/")
def dashboard():
    return render_template("index.html")