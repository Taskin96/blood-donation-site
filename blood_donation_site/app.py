from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

def get_db():
    return sqlite3.connect("database.db")

# Create table
with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            blood_group TEXT,
            last_donation TEXT
        )
    """)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        blood = request.form["blood"]
        last = request.form["last"]

        with get_db() as db:
            db.execute(
                "INSERT INTO users (name,email,password,blood_group,last_donation) VALUES (?,?,?,?,?)",
                (name,email,password,blood,last)
            )
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        ).fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    last_date = datetime.strptime(user[5], "%Y-%m-%d")
    eligible_date = last_date + timedelta(days=90)
    eligible = datetime.now() >= eligible_date

    return render_template(
        "dashboard.html",
        user=user,
        eligible_date=eligible_date.date(),
        eligible=eligible
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

