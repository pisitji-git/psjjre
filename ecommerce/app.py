from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# สินค้าตัวอย่าง
PRODUCTS = [
    {
        'id': 1,
        'name': 'iPhone 15 Pro Max',
        'price': 35999,
        'category': 'อิเล็กทรอนิกส์',
        'description': 'สมาร์ทโฟนรุ่นล่าสุด ปี 2024',
        'image': 'product_1.png'
    },
    {
        'id': 2,
        'name': 'Samsung Galaxy S24',
        'price': 28999,
        'category': 'อิเล็กทรอนิกส์',
        'description': 'มือถือแฟลกชิปตัวท็อป',
        'image': 'product_2.png'
    },
    {
        'id': 3,
        'name': 'MacBook Pro M3',
        'price': 59999,
        'category': 'คอมพิวเตอร์',
        'description': 'แล็ปท็อปสำหรับมืออาชีพ',
        'image': 'product_3.png'
    },
    {
        'id': 4,
        'name': 'Dell XPS 15',
        'price': 49999,
        'category': 'คอมพิวเตอร์',
        'description': 'โน้ตบุ๊กพัฒนาแอปพลิเคชัน',
        'image': 'product_4.png'
    },
    {
        'id': 5,
        'name': 'Canon EOS R5',
        'price': 119999,
        'category': 'กล้อง',
        'description': 'กล้องมิลเรอร์เลสระดับมืออาชีพ',
        'image': 'product_5.png'
    },
    {
        'id': 6,
        'name': 'Sony Alpha A7 IV',
        'price': 99999,
        'category': 'กล้อง',
        'description': 'กล้องดิจิทัลเต็มเฟรม',
        'image': 'product_6.png'
    }
]

CATEGORIES = ['ทั้งหมด', 'อิเล็กทรอนิกส์', 'คอมพิวเตอร์', 'กล้อง']

def generate_product_images():
    """สร้างรูปภาพสินค้าอัตโนมัติ"""
    image_dir = os.path.join(app.static_folder, 'images')
    os.makedirs(image_dir, exist_ok=True)
    
    colors = [
        (255, 107, 107),  # Red
        (74, 144, 226),   # Blue
        (75, 192, 192),   # Teal
        (255, 193, 7),    # Gold
        (156, 39, 176),   # Purple
        (33, 150, 243)    # Light Blue
    ]
    
    for i, product in enumerate(PRODUCTS):
        image_path = os.path.join(image_dir, product['image'])
        
        if not os.path.exists(image_path):
            # สร้างรูปภาพสวยงาม
            img = Image.new('RGB', (400, 400), color=(240, 240, 245))
            draw = ImageDraw.Draw(img)
            
            # วาดพื้นหลังสี
            color = colors[i % len(colors)]
            draw.rectangle([(50, 50), (350, 350)], fill=color)
            
            # วาดสัญลักษณ์
            draw.ellipse([(120, 120), (280, 280)], fill=(255, 255, 255), outline=color, width=3)
            
            # เพิ่มข้อความ
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text = product['name'].split()[0]
            draw.text((200, 200), text, fill=color, font=font, anchor="mm")
            
            img.save(image_path)

def get_cart():
    """ดึงข้อมูลตะกร้าจาก session"""
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def save_cart(cart):
    """บันทึกตะกร้าลงใน session"""
    session['cart'] = cart
    session.modified = True

@app.before_request
def before_request():
    """สร้างรูปภาพสินค้าเมื่อเริ่มต้นแอป"""
    generate_product_images()

@app.route('/')
def index():
    """หน้าแรก"""
    category = request.args.get('category', 'ทั้งหมด')
    
    # กรองสินค้า
    if category == 'ทั้งหมด':
        filtered_products = PRODUCTS
    else:
        filtered_products = [p for p in PRODUCTS if p['category'] == category]
    
    cart = get_cart()
    cart_count = len(cart)
    
    return render_template('index.html', 
                         products=filtered_products, 
                         categories=CATEGORIES,
                         selected_category=category,
                         cart_count=cart_count)

@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    """เพิ่มสินค้าลงตะกร้า"""
    data = request.get_json()
    product_id = data.get('product_id')
    
    # หาสินค้า
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'ไม่พบสินค้า'}), 404
    
    cart = get_cart()
    
    # ตรวจสอบว่าสินค้าอยู่ในตะกร้าแล้วหรือไม่
    cart_item = next((item for item in cart if item['id'] == product_id), None)
    if cart_item:
        cart_item['quantity'] += 1
    else:
        cart.append({
            'id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': 1
        })
    
    save_cart(cart)
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/api/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """ลบสินค้าจากตะกร้า"""
    data = request.get_json()
    product_id = data.get('product_id')
    
    cart = get_cart()
    cart = [item for item in cart if item['id'] != product_id]
    
    save_cart(cart)
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/api/update-quantity', methods=['POST'])
def update_quantity():
    """อัปเดตจำนวนสินค้า"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    cart = get_cart()
    cart_item = next((item for item in cart if item['id'] == product_id), None)
    
    if cart_item:
        if quantity <= 0:
            cart = [item for item in cart if item['id'] != product_id]
        else:
            cart_item['quantity'] = quantity
    
    save_cart(cart)
    return jsonify({'success': True})

@app.route('/cart')
def view_cart():
    """หน้าตะกร้า"""
    cart = get_cart()
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('cart.html', cart=cart, total=total, cart_count=len(cart))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """หน้าชำระเงิน"""
    if request.method == 'POST':
        # บันทึกข้อมูลคำสั่งซื้อ
        cart = get_cart()
        if not cart:
            return redirect(url_for('index'))
        
        customer_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'postal_code': request.form.get('postal_code'),
            'payment_method': request.form.get('payment_method')
        }
        
        # บันทึก session
        session['order'] = {
            'customer': customer_data,
            'cart': cart,
            'total': sum(item['price'] * item['quantity'] for item in cart),
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        session.modified = True
        
        # เคลียร์ตะกร้า
        session['cart'] = []
        session.modified = True
        
        return redirect(url_for('order_success'))
    
    cart = get_cart()
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    if not cart:
        return redirect(url_for('index'))
    
    return render_template('checkout.html', 
                         cart=cart, 
                         total=total, 
                         cart_count=len(cart))

@app.route('/order-success')
def order_success():
    """หน้าสำเร็จการสั่งซื้อ"""
    order = session.get('order', {})
    if not order:
        return redirect(url_for('index'))
    
    return render_template('order_success.html', order=order)

@app.route('/api/cart-count')
def get_cart_count():
    """ดึงจำนวนสินค้าในตะกร้า"""
    cart = get_cart()
    return jsonify({'count': len(cart)})

if __name__ == '__main__':
    app.run(debug=True)
