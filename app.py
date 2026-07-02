from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re

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
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_link = db.Column(db.String(500))


# ---------------- CREATE DATABASE ---------------- #

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if not admin:

        admin = User(
            name="Admin",
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

    setting = Settings.query.first()
    
    youtube_video = ""
    
    print("SETTING:", setting)
    
    if setting:
        print("LINK:", setting.youtube_link)
        youtube_video = get_embed_url(setting.youtube_link)
        print("EMBED:", youtube_video)
    else:
        print("NO SETTINGS FOUND")
    
    return render_template(
        "dashboard.html",
        youtube_video=youtube_video
    )


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    user_count = User.query.filter_by(role="user").count()

    if request.method == "POST":

        user = User(
            name=request.form["name"],
            address=request.form["address"],
            phone=request.form["phone"]
        )

        db.session.add(user)
        db.session.commit()

        flash("User Registered Successfully", "success")
        return redirect(url_for("home"))

    return render_template("register.html", user_count=user_count)





# ---------------- LOGIN ---------------- #

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["role"] = "admin"
            session["user"] = "admin"

            return redirect(url_for("admin_panel"))

        flash("Invalid Admin Credentials", "error")

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")

def logout():

    session.clear()

    return redirect(url_for("home"))




def get_embed_url(url):

    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]

    elif "shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0]

    else:
        return ""

    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"



# ---------------- ADMIN ---------------- #

@app.route("/admin")

def admin_panel():

    if session.get("role") != "admin":

        return redirect(url_for("home"))

    users = User.query.filter_by(role="user").all()

    print("========== USERS ==========")
    print(users)

    for u in users:
        print(u.id, u.name, u.role)

    return render_template("admin.html", users=users)


@app.route("/save_video", methods=["POST"])
def save_video():

    if session.get("role") != "admin":
        return redirect(url_for("home"))

    link = request.form["youtube_link"]

    setting = Settings.query.first()

    if not setting:
        setting = Settings(youtube_link=link)
        db.session.add(setting)
    else:
        setting.youtube_link = link

    db.session.commit()

    flash("Video Updated Successfully", "success")

    return redirect(url_for("admin_panel"))


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