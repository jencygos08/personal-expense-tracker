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

@app.get("/api/summary")
def summary():
    month = date.today().strftime("%Y-%m")

    with get_db() as conn:
        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE substr(expense_date, 1, 7) = ?",
            (month,)
        ).fetchone()[0]

        count = conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE substr(expense_date, 1, 7) = ?",
            (month,)
        ).fetchone()[0]

        categories = con.execute(
            """SELECT category, SUM(amount) AS total
                FROM expenses
                WHERE substr(expense_date, 1, 7) = ?
                GROUP BY category ORDER BY total DESC""",
            (month,)
        ).fetchall()
        recent = conn.execute(
            "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC LIMIT 6"
        ).fetchall()

    budget = 20000
    return jsonify({
        "spent": round(total, 2),
        "count": count,
        "budget": budget,
        "remaining": round(max(budget - total, 0), 2),
        "categories": [dict(row) for row in categories],
        "recent": [dict(row) for row in recent]
})

@app.post("/api/expenses")
def add_expense():
    data = request.get_json()
    title = (data.get("title") or "").strip()
    category = (data.get("category") or "").strip()
    amount = data.get("amount")
    expense_date = data.get("date") or date.today().isoformat()

    if not title or not category or amount is None:
        return jsonify({"error": "Please fill in every field"}),400

    try:
        amount = float(amount)
        if amount<= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Enter an amount greater than zero"}), 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO expenses (title, category, amount, expense_date) VALUES (?,?,?,?)",
            (title, category, amount, expense_date)
        )
    return jsonify({"message": "Expense added successfully"}), 201

@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    with get_db() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        return jsonify({"message": "Expense deleted successfully"})

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)