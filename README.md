# Lumière Skincare — Quiz-Based Recommendation System

## Project Overview
A quiz-based skincare product recommendation system with full 
e-commerce functionality, built as a BSc Computer Science 
Final Year Project at the University of Hertfordshire.

## Developer
Nazia Tareen | SRN: 25012937
BSc (Hons) Computer Science
University of Hertfordshire — TMUC Campus, Gujranwala
Supervisor: Dr. Trevor Barker

## Features
- **Product catalogue** — browse, filter (skin type / category / price) and search, backed by a database (admin can add/edit/delete products)
- **Skin quiz** — a rule-based recommendation engine that suggests a personalised routine from skin type + skin concerns
- **Accounts** — registration and login with Werkzeug-hashed passwords
- **Cart & checkout** — session-based cart, Cash on Delivery or Online Transfer, order history under "My Orders" (login required)
- **Product reviews** — star ratings and written reviews on every product page
- **Admin panel** — dashboard with live stats, order management, user management, full product CRUD with image upload

## Technologies Used
- Python (Flask)
- SQLite (Flask-SQLAlchemy)
- HTML, CSS, JavaScript
- Werkzeug (Password Hashing)

## Getting Started

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
```bash
python app.py
```

The site will be available at `http://127.0.0.1:5000`. The database (`instance/lumiere.db`) and its tables are created automatically the first time the app runs.

### Admin Panel
Available at `/admin/login`.
- Email: `admin@lumiere.co`
- Password: `admin123`

## Project Structure
```
app.py                  Flask app: routes + database models
templates/               Jinja2 HTML templates
static/css/style.css     All styling
static/js/main.js        All client-side behaviour
static/images/           Product photos
instance/lumiere.db      SQLite database (auto-created)
```

## Project Status
Core features complete and tested — product catalogue, quiz engine, accounts, cart/checkout, reviews, and admin panel are all functional. Remaining work: Nielsen's Heuristic Evaluation and Final Report write-up.
