from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__, template_folder='template', static_folder='static')
# Secret key for session (used by simple admin login)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database configuration: sqlite:///shop.db
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)


def ensure_db():
    """Create database file and tables if they do not exist."""
    if not os.path.exists(db_path):
        # This will create the SQLite file and the tables defined by models
        with app.app_context():
            db.create_all()
        print('Created database:', db_path)
    else:
        print('Database already exists:', db_path)


def seed_db():
    """Insert example products if the products table is empty."""
    with app.app_context():
        count = Product.query.count()
        if count == 0:
            samples = [
                Product(name='สินค้า A', price=790.00, image_url=''),
                Product(name='สินค้า B', price=1290.00, image_url=''),
                Product(name='สินค้า C', price=450.00, image_url=''),
                Product(name='สินค้า D', price=1990.00, image_url=''),
            ]
            db.session.bulk_save_objects(samples)
            db.session.commit()
            return True
        return False


# Simple API endpoints
@app.route('/products', methods=['GET'])
def list_products():
    with app.app_context():
        products = Product.query.all()
        result = []
        for p in products:
            result.append({
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'image_url': p.image_url,
            })
        return jsonify(result)


@app.route('/')
def index():
    with app.app_context():
        products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/seed', methods=['POST', 'GET'])
def seed_route():
    created = seed_db()
    if created:
        return jsonify({'status': 'seeded', 'message': 'Inserted sample products'})
    return jsonify({'status': 'skipped', 'message': 'Products already exist'})


# --- Simple admin / backend routes ---
def _is_logged_in():
    return bool(session.get('admin'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '1234':
            session['admin'] = True
            return redirect(url_for('index'))
        flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if not _is_logged_in():
        return redirect(url_for('login'))
    with app.app_context():
        products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin.html', products=products)


@app.route('/admin/add', methods=['POST'])
def admin_add():
    if not _is_logged_in():
        return redirect(url_for('login'))
    
    name = request.form.get('name') or ''
    price = request.form.get('price') or '0'
    image_url = ''
    
    # Handle file upload
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"images/{filename}"
        else:
            # Fall back to URL if file upload fails
            image_url = request.form.get('image_url') or ''
    else:
        # Use URL if no file uploaded
        image_url = request.form.get('image_url') or ''
    
    try:
        price_val = float(price)
    except ValueError:
        price_val = 0.0
    
    with app.app_context():
        p = Product(name=name, price=price_val, image_url=image_url)
        db.session.add(p)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete/<int:product_id>', methods=['POST'])
def admin_delete(product_id):
    if not _is_logged_in():
        return redirect(url_for('login'))
    with app.app_context():
        p = Product.query.get(product_id)
        if p:
            db.session.delete(p)
            db.session.commit()
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    ensure_db()
    seeded = seed_db()
    if seeded:
        print('✓ Inserted sample products into database.')
    else:
        print('✓ Products already exist in database.')
    print('Starting Flask server...')
    app.run(debug=True)
