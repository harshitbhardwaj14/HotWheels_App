# app.py — single-file corrected app (Flask + Flask-SQLAlchemy)
from flask import (
    Flask, request, redirect, url_for, render_template, session,
    send_from_directory, jsonify, flash
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

# -------------------- Config --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, "instance", "hotwheels.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# Optional Gemini env vars (used if configured)
GEMINI_API_URL = os.environ.get("GEMINI_API_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# -------------------- Models --------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    cars = db.relationship("Car", back_populates="owner")
    posts = db.relationship("FeedPost", back_populates="user")


class FeedPost(db.Model):
    __tablename__ = "feed_posts"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.Text, nullable=True)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    car = db.relationship("Car", back_populates="feed_posts")
    user = db.relationship("User", back_populates="posts")


class Car(db.Model):
    __tablename__ = "cars"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    image_filename = db.Column(db.String(512), nullable=False)
    notes = db.Column(db.Text, default="")
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="cars")
    feed_posts = db.relationship("FeedPost", back_populates="car")


# Create tables
with app.app_context():
    db.create_all()

# -------------------- Helpers --------------------
def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

def save_image_file(file_storage, prefix=""):
    filename = secure_filename(file_storage.filename)
    name = f"{int(datetime.utcnow().timestamp())}_{prefix}_{filename}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], name)
    file_storage.save(path)
    return name

def fetch_more_info_from_gemini(name):
    if not GEMINI_API_URL or not GEMINI_API_KEY:
        return "Gemini API not configured."
    try:
        payload = {"prompt": f"Tell me about Hot Wheels car '{name}'.", "max_tokens": 400}
        headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
        r = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        j = r.json()
        # try common keys
        return j.get("text") or j.get("output") or str(j)
    except Exception as e:
        return f"Error: {e}"

# -------------------- Routes --------------------
@app.route("/")
def index():
    user = get_current_user()
    return redirect(url_for("collection") if user else url_for("login"))

# Auth
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Provide username and password", "error")
            return redirect(url_for("signup"))
        if User.query.filter_by(username=username).first():
            flash("Username already taken", "error")
            return redirect(url_for("signup"))
        u = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
        session["user_id"] = u.id
        return redirect(url_for("collection"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        u = User.query.filter_by(username=username).first()
        if not u or not check_password_hash(u.password_hash, password):
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))
        session["user_id"] = u.id
        return redirect(url_for("collection"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Serve uploads
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Collection (search)
@app.route("/collection")
def collection():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    q = request.args.get("q", "").strip().lower()
    cars_q = Car.query.filter_by(user_id=user.id).order_by(Car.added_at.desc())
    cars = cars_q.all()
    if q:
        cars = [c for c in cars if q in c.name.lower() or q in (c.notes or "").lower()]
    return render_template("collection.html", user=user, cars=cars)

# Upload car (from form)
@app.route("/upload_file", methods=["POST"])
def upload_file():
    user = get_current_user()
    if not user:
        return "Not logged in", 401
    if "image" not in request.files:
        return "No image", 400
    image = request.files["image"]
    name = request.form.get("name", "Unnamed HotWheels")
    notes = request.form.get("notes", "")
    fname = save_image_file(image, prefix="up")
    car = Car(user_id=user.id, name=name, image_filename=fname, notes=notes)
    db.session.add(car)
    db.session.commit()
    return redirect(url_for("collection"))

# Car detail
@app.route("/car/<int:car_id>")
def car_detail(car_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    car = Car.query.filter_by(id=car_id, user_id=user.id).first()
    if not car:
        return "Not found", 404
    return render_template("car_detail.html", car=car, user=user)

# Gemini info (AJAX)
@app.route("/car/<int:car_id>/more")
def car_more(car_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "not logged in"}), 401
    car = Car.query.filter_by(id=car_id, user_id=user.id).first()
    if not car:
        return jsonify({"error": "not found"}), 404
    return jsonify({"info": fetch_more_info_from_gemini(car.name)})

# Post a car to the feed (from car detail)
@app.route("/post_to_feed/<int:car_id>", methods=["POST"])
def post_to_feed(car_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    car = Car.query.get_or_404(car_id)
    description = request.form.get("description", "")

    post = FeedPost(car_id=car.id, user_id=user.id, description=description)
    db.session.add(post)
    db.session.commit()

    return redirect(url_for("feed"))


# Feed listing (public to all)
@app.route("/feed")
def feed():
    posts = FeedPost.query.order_by(FeedPost.created_at.desc()).all()
    # each post has .car and .user relationship available in template
    return render_template("feed.html", posts=posts, user=get_current_user())

# Like a post (increments)
@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    user = get_current_user()
    if not user:
        flash("You must be logged in to like.", "error")
        return redirect(url_for("login"))
    post = FeedPost.query.get(post_id)
    if not post:
        return "Post not found", 404
    post.likes = post.likes + 1
    db.session.commit()
    return redirect(url_for("feed"))

@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    car = db_session.query(Car).filter_by(id=car_id).first()
    if car:
        db_session.delete(car)
        db_session.commit()
    return redirect(url_for('collection'))


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=True)
