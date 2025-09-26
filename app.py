from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os, base64, requests
from io import BytesIO
from PIL import Image

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, 'instance', 'hotwheels.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

# Database setup
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    cars = relationship('Car', back_populates='owner')

class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(256), nullable=False)
    image_filename = Column(String(512), nullable=False)
    notes = Column(Text, default='')
    added_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='cars')

Base.metadata.create_all(engine)

# Helpers
def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return db.query(User).filter_by(id=uid).first()

def save_image_file(file_storage, prefix=''):
    filename = secure_filename(file_storage.filename)
    name = f"{int(datetime.utcnow().timestamp())}_{prefix}_{filename}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], name)
    file_storage.save(path)
    return name

# Gemini API
GEMINI_API_URL = os.environ.get('GEMINI_API_URL')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

def fetch_more_info_from_gemini(name):
    if not GEMINI_API_URL or not GEMINI_API_KEY:
        return 'Gemini API not configured.'
    try:
        payload = {'prompt': f"Tell me about Hot Wheels car '{name}'.", 'max_tokens': 400}
        headers = {'Authorization': f'Bearer {GEMINI_API_KEY}', 'Content-Type': 'application/json'}
        r = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        j = r.json()
        return j.get('text') or r.text
    except Exception as e:
        return f'Error: {e}'

# Routes
@app.route('/')
def index():
    user = get_current_user()
    return redirect(url_for('collection') if user else url_for('login'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if db.query(User).filter_by(username=username).first():
            return 'Username already taken', 400
        u = User(username=username, password_hash=generate_password_hash(password))
        db.add(u); db.commit()
        session['user_id'] = u.id
        return redirect(url_for('collection'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = db.query(User).filter_by(username=request.form['username']).first()
        if not u or not check_password_hash(u.password_hash, request.form['password']):
            return 'Invalid credentials', 401
        session['user_id'] = u.id
        return redirect(url_for('collection'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/collection')
def collection():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    cars = db.query(Car).filter_by(user_id=user.id).order_by(Car.added_at.desc()).all()
    return render_template('collection.html', user=user, cars=cars)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    user = get_current_user()
    if not user: return 'Not logged in', 401
    if 'image' not in request.files: return 'No image', 400
    image = request.files['image']
    name = request.form.get('name', 'Unnamed HotWheels')
    notes = request.form.get('notes', '')
    fname = save_image_file(image, prefix='up')
    car = Car(user_id=user.id, name=name, image_filename=fname, notes=notes)
    db.add(car); db.commit()
    return redirect(url_for('collection'))

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    car = db.query(Car).filter_by(id=car_id, user_id=user.id).first()
    if not car: return 'Not found', 404
    return render_template('car_detail.html', car=car)

@app.route('/car/<int:car_id>/more')
def car_more(car_id):
    user = get_current_user()
    if not user: return jsonify({'error':'not logged in'}), 401
    car = db.query(Car).filter_by(id=car_id, user_id=user.id).first()
    if not car: return jsonify({'error':'not found'}), 404
    return jsonify({'info': fetch_more_info_from_gemini(car.name)})

@app.route('/delete/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    user = get_current_user()
    if not user: return 'Not logged in', 401
    car = db.query(Car).filter_by(id=car_id, user_id=user.id).first()
    if not car: return 'Not found', 404
    try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], car.image_filename))
    except: pass
    db.delete(car); db.commit()
    return redirect(url_for('collection'))

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

from flask import render_template, request, redirect, url_for
from models import Car # Assuming models.py contains the Car model and database setup
from flask_login import login_required, current_user

@app.route("/collection", methods=["GET"])
@login_required
def collection():
    query = request.args.get("q", "").strip().lower()

    # Fetch cars of the logged-in user
    cars = Car.query.filter_by(user_id=current_user.id).all()

    if query:
        cars = [car for car in cars if query in car.name.lower() or query in (car.notes or "").lower()]

    return render_template("collection.html", cars=cars, user=current_user)

