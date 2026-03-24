import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = "secret-key-change-this"

# ================= DB =================
def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ================= INIT DB =================
def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    db.commit()
    cur.close()

# ================= ROUTES =================

# 🔥 แก้ตรงนี้ (ไม่ใช้ index.html แล้ว)
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, name FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()

        if user:
            session["user_id"] = user[0]
            session["name"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            flash("ข้อมูลไม่ถูกต้อง", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()

        try:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            db.commit()
            return redirect(url_for("login"))
        except:
            flash("อีเมลนี้มีแล้ว", "danger")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", name=session["name"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        init_db()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
