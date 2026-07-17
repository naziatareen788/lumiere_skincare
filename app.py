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


# ===== HELPERS =====

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please login to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return view(*args, **kwargs)
    return wrapped


def get_cart_items():
    cart = session.get('cart', {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(product_id)
        if not product:
            continue
        item_total = product.price * quantity
        items.append({
            'id': product_id,
            'name': product.name,
            'image': product.image,
            'price': 'PKR {:,}'.format(product.price),
            'quantity': quantity,
            'total': item_total,
        })
        total += item_total
    return items, total


def slugify(text):
    slug = re.sub(r'[^a-z0-9]+', '-', text.strip().lower()).strip('-')
    return slug or 'product'


def unique_slug(name):
    base = slugify(name)
    slug = base
    suffix = 2
    while Product.query.get(slug):
        slug = '{}-{}'.format(base, suffix)
        suffix += 1
    return slug


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_product_image(slug, image_file):
    ext = image_file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename('{}.{}'.format(slug, ext))
    image_file.save(os.path.join(app.static_folder, 'images', filename))
    return filename


# ===== SKIN QUIZ RECOMMENDATION RULES =====

SKIN_TYPE_ROUTINE = {
    'Oily': {
        'cleanser': 'mochi-cleanser',
        'toner': 'swimming-pool-toner',
        'moisturizer': 'oat-gel-cream',
        'sunscreen': 'relief-sun',
    },
    'Dry': {
        'cleanser': 'hyaluronic-cleanser',
        'toner': 'milky-toner',
        'moisturizer': 'ceramide-cream',
        'sunscreen': 'spf50-sunscreen',
    },
    'Sensitive': {
        'cleanser': 'black-rice-cleanser',
        'toner': 'heartleaf-toner',
        'moisturizer': 'bamboo-cream',
        'sunscreen': 'centella-sunscreen',
    },
    'Combination': {
        'cleanser': 'lowph-cleanser',
        'toner': 'black-rice-toner',
        'moisturizer': 'centella-cream',
        'sunscreen': 'ultralight-sunscreen',
    },
}

CONCERN_SERUM_MAP = {
    'Large Pore': 'niacinamide-serum',
    'Blackheads': 'niacinamide-serum',
    'Excess Oil': 'niacinamide-serum',
    'Wrinkles': 'retinal-shot',
    'Acne': 'azelaic-serum',
    'Rosacea': 'azelaic-serum',
    'Hyperpigmentation': 'vitaminc-serum',
    'Dark Spots': 'vitaminc-serum',
    'Hydration': 'snail-serum',
}





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)