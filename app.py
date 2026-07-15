import json
import os
import re
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lumiere-skincare-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lumiere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ADMIN_EMAIL = 'admin@lumiere.co'
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')

PRODUCT_CATEGORIES = ['Cleanser', 'Toner', 'Moisturizer', 'Sunscreen', 'Serum', 'Mask']
PRODUCT_SKIN_TYPES = ['Oily Skin', 'Dry Skin', 'Sensitive Skin', 'Combination Skin', 'All Skin Types']
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


# ===== DATABASE MODELS =====

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.String(20), default='cod')

    items = db.Column(db.Text, nullable=False)  # JSON snapshot of the cart at checkout
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(80), db.ForeignKey('product.slug'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    reviewer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    slug = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    skin_type = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    benefits = db.Column(db.Text, nullable=False)  # newline-separated bullet points
    ingredients = db.Column(db.Text, nullable=False)
    how_to_use = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)