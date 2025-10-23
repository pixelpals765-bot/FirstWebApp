# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this for production

init_db()  # create DB and admin user if missing


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "error")

    return render_template("index.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Admins are redirected to admin dashboard
    if session["username"] == "admin":
        return redirect(url_for("admin_dashboard"))

    return render_template("dashboard.html", username=session["username"])


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or session["username"] != "admin":
        flash("Access denied. Admins only.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    users = conn.execute("SELECT id, username FROM users").fetchall()
    conn.close()

    return render_template("admin_dashboard.html", users=users)


# ---------- DELETE USER ----------
@app.route("/admin/delete/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session["username"] != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    flash("User deleted successfully!", "info")
    return redirect(url_for("admin_dashboard"))


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
