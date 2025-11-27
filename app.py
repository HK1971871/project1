from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # đổi thành key riêng của bạn

# Giả lập database bằng dictionary
users = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("User đã tồn tại!")
            return redirect(url_for("register"))

        users[username] = generate_password_hash(password)
        flash("Đăng ký thành công, mời login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            flash("Login thành công!")
            return redirect(url_for("dashboard"))
        else:
            flash("Sai username hoặc password.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    else:
        flash("Bạn cần login trước.")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Đã logout.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)