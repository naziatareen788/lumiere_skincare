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


# ===== STATIC / INFO PAGES =====

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not full_name or not email or not message:
            flash('Please fill in all required fields.', 'error')
        else:
            flash('Thank you for reaching out! We will get back to you within 24 hours.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip()
    if not email:
        flash('Please enter your email address.', 'error')
    else:
        flash('Thanks for subscribing to Lumière!', 'success')
    return redirect(request.referrer or url_for('home'))


# ===== AUTH =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not email or not password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('register'))

        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.full_name
        session['user_email'] = user.email
        flash('Account created successfully! Welcome to Lumière.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['user_name'] = user.full_name
        session['user_email'] = user.email
        flash('Welcome back, {}!'.format(user.full_name.split()[0]), 'success')
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    cart = session.get('cart')
    session.clear()
    if cart:
        session['cart'] = cart
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# ===== PRODUCTS =====

@app.route('/products')
def products():
    category = request.args.get('category', 'all')
    skin_type = request.args.get('skin_type', 'all')
    search = request.args.get('search', '')
    all_products = Product.query.order_by(Product.name).all()
    return render_template(
        'products.html', category=category, skin_type=skin_type,
        search=search, products=all_products,
    )


@app.route('/category/<name>')
def category(name):
    all_products = Product.query.order_by(Product.name).all()
    return render_template(
        'products.html', category=name, skin_type='all',
        search='', products=all_products,
    )


@app.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.get(slug)
    if not product:
        abort(404)

    display_product = {
        'name': product.name,
        'price': 'PKR {:,}'.format(product.price),
        'category': product.category,
        'skin_type': product.skin_type,
        'images': [product.image],
        'benefits': product.benefits.split('\n'),
        'ingredients': product.ingredients,
        'how_to_use': product.how_to_use,
    }

    reviews = Review.query.filter_by(product_id=slug).order_by(Review.created_at.desc()).all()
    return render_template('product_detail.html', product=display_product, reviews=reviews)


@app.route('/submit-review', methods=['POST'])
def submit_review():
    product_id = request.form.get('product_id')
    reviewer_name = request.form.get('reviewer_name', '').strip()
    rating = request.form.get('rating', '5')
    review_text = request.form.get('review_text', '').strip()

    if not Product.query.get(product_id) or not reviewer_name or not review_text:
        flash('Please fill in all review fields.', 'error')
        return redirect(url_for('product_detail', slug=product_id))

    review = Review(
        product_id=product_id,
        user_id=session.get('user_id'),
        reviewer_name=reviewer_name,
        rating=int(rating),
        review_text=review_text,
    )
    db.session.add(review)
    db.session.commit()
    flash('Thank you for your review!', 'success')
    return redirect(url_for('product_detail', slug=product_id))




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)