from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "rushika_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- USER TABLE ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    address = db.Column(db.String(300))

    phone = db.Column(db.String(20))

    username = db.Column(db.String(50), unique=True)

    password = db.Column(db.String(250))

    role = db.Column(db.String(20), default="user")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- CREATE DATABASE ---------------- #

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if not admin:

        admin = User(
            name="Admin",
            address="Dashboard",
            phone="0000000000",
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )

        db.session.add(admin)

        db.session.commit()


# ---------------- HOME ---------------- #

@app.route("/")
def home():

    expiry = datetime.utcnow() - timedelta(days=5)

    old_users = User.query.filter(
        User.role=="user",
        User.created_at < expiry
    ).all()

    for user in old_users:
        db.session.delete(user)

    db.session.commit()

    users=[]

    if session.get("role")=="admin":
        users=User.query.filter_by(role="user").all()

    return render_template(
        "dashboard.html",
        users=users
    )


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    user_count = User.query.filter_by(role="user").count()

    if request.method == "POST":

        if user_count >= 5:

            flash("Registration Closed", "error")

            return redirect(url_for("register"))

        username = request.form["username"]

        check = User.query.filter_by(username=username).first()

        if check:

            flash("Username Already Exists", "error")

            return redirect(url_for("register"))

        user = User(

            name=request.form["name"],

            address=request.form["address"],

            phone=request.form["phone"],

            username=username,

            password=generate_password_hash(request.form["password"])

        )

        db.session.add(user)

        db.session.commit()

        session["user"] = username
        session["role"] = "user"

        flash("Registration Successful", "success")

        return redirect(url_for("home"))

    return render_template("register.html", user_count=user_count)


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user"] = user.username

            session["role"] = user.role

            flash("Login Successful", "success")

            return redirect(url_for("home"))

        flash("Invalid Username or Password", "error")

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")

def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- ADMIN ---------------- #

@app.route("/admin")

def admin_panel():

    if session.get("role") != "admin":

        return redirect(url_for("home"))

    users = User.query.filter_by(role="user").all()

    print("========== USERS ==========")
    print(users)

    for u in users:
        print(u.id, u.name, u.username, u.role)

    return render_template("admin.html", users=users)


# ---------------- DELETE USER ---------------- #

@app.route("/delete/<int:id>")

def delete(id):

    if session.get("role") != "admin":

        return redirect(url_for("home"))

    user = db.session.get(User, id)

    if user:

        db.session.delete(user)

        db.session.commit()

    return redirect(url_for("admin_panel"))


# ---------------- RUN ---------------- #

if __name__ == "__main__":

    app.run(debug=True)