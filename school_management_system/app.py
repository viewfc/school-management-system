import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")

# ================= DB =================
def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ================= INIT DB =================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        role VARCHAR(50)
    );
    """)

    conn.commit()
    cur.close()

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, password, role)
            )
            conn.commit()
            flash("สมัครสำเร็จ", "success")
            return redirect(url_for("login"))
        except:
            flash("อีเมลซ้ำ", "danger")

        cur.close()

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[4]
            return redirect(url_for("dashboard"))

        flash("ข้อมูลไม่ถูกต้อง", "danger")

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", name=session["name"])

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        init_db()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
