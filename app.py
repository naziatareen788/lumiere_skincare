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
    benefits = db.Column(db.Text, nullable=False)  
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

    if 'user_id' not in session:
        flash('Please login to write a review.', 'error')
        return redirect(url_for('login'))

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


# ===== CART =====

@app.route('/cart')
def cart():
    cart_items, total = get_cart_items()
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1) or 1)

    product = Product.query.get(product_id)
    if not product:
        abort(404)
    if quantity < 1:
        quantity = 1

    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart

    flash('{} added to your cart.'.format(product.name), 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1) or 1)

    cart = session.get('cart', {})
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity
    session['cart'] = cart

    return redirect(url_for('cart'))


@app.route('/remove-from-cart/<product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(product_id, None)
    session['cart'] = cart
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))


# ===== CHECKOUT / ORDERS =====

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to place an order.', 'error')
        return redirect(url_for('login'))

    cart_items, total = get_cart_items()

    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))

    shipping = 0 if total >= 5000 else 200
    grand_total = total + shipping

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        payment = request.form.get('payment', 'cod')

        if not all([full_name, email, phone, address, city]):
            flash('Please fill in all delivery details.', 'error')
            return redirect(url_for('checkout'))

        order = Order(
            user_id=session.get('user_id'),
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            payment_method=payment,
            items=json.dumps(cart_items),
            total=grand_total,
            status='Pending',
        )
        db.session.add(order)
        db.session.commit()

        session['cart'] = {}
        return redirect(url_for('order_confirmation', order_id=order.id))

    return render_template(
        'checkout.html', cart_items=cart_items, total=total,
        shipping=shipping, grand_total=grand_total,
    )


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)


@app.route('/my-orders')
def my_orders():
    if 'user_id' not in session:
        flash('Please login to view your orders.', 'error')
        return redirect(url_for('login'))

    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)


# ===== SKIN QUIZ =====

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


@app.route('/quiz-result', methods=['POST'])
def quiz_result():
    user_name = request.form.get('user_name', '').strip() or 'there'
    skin_type = request.form.get('skin_type', 'Combination')
    concerns = request.form.getlist('concerns')

    base = SKIN_TYPE_ROUTINE.get(skin_type, SKIN_TYPE_ROUTINE['Combination'])

    routine_ids = [base['cleanser'], base['toner']]

    for concern in concerns:
        serum_id = CONCERN_SERUM_MAP.get(concern)
        if serum_id and serum_id not in routine_ids:
            routine_ids.append(serum_id)

    routine_ids.append(base['moisturizer'])
    routine_ids.append(base['sunscreen'])

    routine_products = [p for p in (Product.query.get(pid) for pid in routine_ids) if p]

    routine = []
    for step, product in enumerate(routine_products, start=1):
        routine.append({
            'step': step,
            'type': product.category,
            'id': product.slug,
            'name': product.name,
            'image': product.image,
        })

    return render_template(
        'quiz_result.html', user_name=user_name, skin_type=skin_type,
        concerns=concerns, routine=routine,
    )


# ===== ADMIN =====

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['is_admin'] = True
            flash('Welcome back, Admin.', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Invalid admin credentials.', 'error')
        return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Admin logged out.', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    total_users = User.query.count()
    total_revenue = db.session.query(db.func.coalesce(db.func.sum(Order.total), 0)).scalar()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html', total_orders=total_orders, pending_orders=pending_orders,
        total_users=total_users, total_revenue=total_revenue, recent_orders=recent_orders,
    )


@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/update-order-status', methods=['POST'])
@admin_required
def admin_update_order_status():
    order_id = request.form.get('order_id')
    status = request.form.get('status')

    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()

    flash('Order status updated.', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/admin/users')
@admin_required
def admin_users():
    search = request.args.get('search', '').strip()

    query = User.query
    if search:
        like = '%{}%'.format(search)
        query = query.filter(db.or_(User.full_name.ilike(like), User.email.ilike(like)))

    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users, search=search)


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)

    Order.query.filter_by(user_id=user_id).update({'user_id': None})
    db.session.delete(user)
    db.session.commit()

    flash('User removed.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/products')
@admin_required
def admin_products():
    all_products = Product.query.order_by(Product.name).all()
    return render_template('admin_products.html', products=all_products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        category = request.form.get('category', '').strip()
        skin_type = request.form.get('skin_type', '').strip()
        benefits = request.form.get('benefits', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        how_to_use = request.form.get('how_to_use', '').strip()
        image_file = request.files.get('image')

        if not all([name, price, category, skin_type, benefits, ingredients, how_to_use]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('admin_add_product'))

        if not image_file or image_file.filename == '' or not allowed_image(image_file.filename):
            flash('Please choose a valid product image (png, jpg, jpeg, webp or gif).', 'error')
            return redirect(url_for('admin_add_product'))

        try:
            price = int(price)
        except ValueError:
            flash('Price must be a whole number.', 'error')
            return redirect(url_for('admin_add_product'))

        slug = unique_slug(name)
        image_filename = save_product_image(slug, image_file)

        product = Product(
            slug=slug,
            name=name,
            price=price,
            category=category,
            skin_type=skin_type,
            image=image_filename,
            benefits=benefits,
            ingredients=ingredients,
            how_to_use=how_to_use,
        )
        db.session.add(product)
        db.session.commit()

        flash('Product added successfully.', 'success')
        return redirect(url_for('admin_products'))

    return render_template(
        'admin_product_form.html', product=None,
        categories=PRODUCT_CATEGORIES, skin_types=PRODUCT_SKIN_TYPES,
    )


@app.route('/admin/products/edit/<slug>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(slug):
    product = Product.query.get_or_404(slug)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        category = request.form.get('category', '').strip()
        skin_type = request.form.get('skin_type', '').strip()
        benefits = request.form.get('benefits', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        how_to_use = request.form.get('how_to_use', '').strip()
        image_file = request.files.get('image')

        if not all([name, price, category, skin_type, benefits, ingredients, how_to_use]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('admin_edit_product', slug=slug))

        try:
            price = int(price)
        except ValueError:
            flash('Price must be a whole number.', 'error')
            return redirect(url_for('admin_edit_product', slug=slug))

        if image_file and image_file.filename:
            if not allowed_image(image_file.filename):
                flash('Please choose a valid product image (png, jpg, jpeg, webp or gif).', 'error')
                return redirect(url_for('admin_edit_product', slug=slug))
            product.image = save_product_image(slug, image_file)

        product.name = name
        product.price = price
        product.category = category
        product.skin_type = skin_type
        product.benefits = benefits
        product.ingredients = ingredients
        product.how_to_use = how_to_use
        db.session.commit()

        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin_products'))

    return render_template(
        'admin_product_form.html', product=product,
        categories=PRODUCT_CATEGORIES, skin_types=PRODUCT_SKIN_TYPES,
    )


@app.route('/admin/products/delete/<slug>', methods=['POST'])
@admin_required
def admin_delete_product(slug):
    product = Product.query.get_or_404(slug)

    Review.query.filter_by(product_id=slug).delete()
    db.session.delete(product)
    db.session.commit()

    flash('Product removed.', 'success')
    return redirect(url_for('admin_products'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)