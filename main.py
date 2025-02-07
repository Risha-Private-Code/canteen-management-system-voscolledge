"""
⚠️ ВНИМАНИЕ: ДАННЫЙ КОД ЯВЛЯЕТСЯ КОНФИДЕНЦИАЛЬНЫМ И МОЖЕТ ИСПОЛЬЗОВАТЬСЯ ТОЛЬКО В ГБПОУ МО "ВОСКРЕСЕНСКИЙ КОЛЛЕДЖ" ⚠️

Этот исходный код защищен международным законодательством об авторском праве.
Он доступен только для использования в ГБПОУ МО "Воскресенский Колледж". 
Если у вас нет разрешения на использование этого кода, немедленно закройте файл и удалите его.

❗️ Открытая версия доступна на GitHub:  
https://github.com/isamirivers/canteen-management-system

🚫 НЕ РАСПРОСТРАНЯТЬ 🚫
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from functools import wraps
from werkzeug.exceptions import HTTPException
from license_check import check_license

check_license()

client = MongoClient('mongodb://localhost:27017/')
db = client.stolovaya
users_collection = db.users
dishes_collection = db.dishes
days_collection = db.days
orders_collection = db.orders  # Добавляем новую коллекцию

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'fj30fjn2-0n23f398fno3i2ufn2oipfjnh8&*#H78rh'  # Добавьте эту строку

@app.errorhandler(Exception)
def handle_exception(e):
    error_code = 500
    error_message = 'Вну&shyтре&shyнняя о&shyши&shyбка сер&shyве&shyра'
    if isinstance(e, HTTPException):
        error_code = e.code
        if e.code == 404:
            error_message = 'Стра&shyни&shyца не най&shyде&shyна'
        elif e.code == 403:
            error_message = 'До&shyступ за&shyпре&shyщен'
        elif e.code == 401:
            error_message = 'Тре&shyбу&shyется а&shyвто&shyри&shyза&shyци&shyя'
        elif e.code == 500:
            error_message = 'Вну&shyтре&shyнняя о&shyши&shyбка сер&shyве&shyра'
        else:
            error_message = 'Про&shyи&shyзо&shyшла о&shyши&shyбка'
    return render_template('error.html', error_code=error_code, error_message=error_message), error_code


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home'))
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if not user or not user.get('admin', False):
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if user and user.get('admin', False):
            return redirect(url_for('orders'))
    return render_template('home.html')

@app.route('/orders')
@admin_required
def orders():
    return render_template('orders.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']
    user = users_collection.find_one({'login': login})
    if user and check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        return 'OK'
    else:
        return 'Invalid login or password'

@app.route('/register', methods=['POST'])
def register():
    login = request.form['login']
    password = request.form['password']
    if users_collection.find_one({'login': login}):
        return 'Пользователь с таким логином уже существует', 400
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({'login': login, 'password': hashed_password, 'admin': False})
    return 'OK'

@app.route('/check_auth')
def check_auth():
    if 'user_id' in session:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        return {
            'authenticated': True,
            'username': user['login'],
            'admin': user['admin']
        }
    else:
        return {'authenticated': False}

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/edit', methods=['GET', 'POST'])
@admin_required
def edit():
    if request.method == 'POST':
        data = request.get_json()
        day = int(data['day'])
        dishes = data['dishes']
        days_collection.update_one({'day': day}, {'$set': {'dishes': dishes}}, upsert=True)
        return 'OK'
    return render_template('edit.html')

@app.route('/editDishes', methods=['GET', 'POST'])
@admin_required
def editDishes():
    if request.method == 'POST':
        # editing db
        return 'Не готово'
    return render_template('editDishes.html')

@app.route('/dishes')
@admin_required
def dishes():
    dishes = list(dishes_collection.find({}, {'_id': 1, 'name': 1, 'type': 1, 'price': 1}))
    for dish in dishes:
        dish['_id'] = str(dish['_id'])  # Преобразование ObjectId в строку
    return jsonify({'dishes': dishes})

@app.route('/dishes', methods=['POST'])
@admin_required
def add_dish():
    data = request.get_json()
    new_dish = {
        'name': data['name'],
        'type': data['type'],
        'price': data['price']
    }
    result = dishes_collection.insert_one(new_dish)
    new_dish['_id'] = str(result.inserted_id)
    return jsonify(new_dish)

@app.route('/dishes/<dish_id>', methods=['PUT'])
@admin_required
def update_dish(dish_id):
    data = request.get_json()
    dishes_collection.update_one(
        {'_id': ObjectId(dish_id)},
        {'$set': {'name': data['name'], 'type': data['type'], 'price': data['price']}}
    )
    return 'OK'

@app.route('/dishes/<dish_id>', methods=['DELETE'])
@admin_required
def delete_dish(dish_id):
    dishes_collection.delete_one({'_id': ObjectId(dish_id)})
    return 'OK'

@app.route('/days')
@admin_required
def days():
    days = list(days_collection.find({}))
    for day in days:
        day['_id'] = str(day['_id'])  # Преобразование ObjectId в строку
        day['dishes'] = [str(dish_id) for dish_id in day['dishes']]  # Преобразование ObjectId в строку
    print('Days data:', days)  # Отладочное сообщение
    return jsonify({'days': days})

@app.route('/current_day_dishes')
def current_day_dishes():
    from datetime import datetime, timedelta
    
    # Получаем завтрашнюю дату
    tomorrow = datetime.now() + timedelta(days=1)
    
    # Получаем номер дня недели для завтра (1-5)
    weekday = tomorrow.isoweekday()
    if weekday > 5:  # Если выходной, показываем следующий понедельник
        days_until_monday = 8 - weekday  # 8 вместо 7, так как нам нужен следующий понедельник
        tomorrow = datetime.now() + timedelta(days=days_until_monday)
        weekday = 1
    
    # Получаем четность недели
    week_number = tomorrow.isocalendar()[1]
    day_number = weekday if week_number % 2 == 1 else weekday + 5
    
    # Остальная логика получения блюд остается прежней
    day = days_collection.find_one({'day': day_number})
    if not day:
        return jsonify({'dishes': []})
    
    dishes = []
    for dish_id in day['dishes']:
        dish = dishes_collection.find_one({'_id': ObjectId(dish_id)})
        if dish:
            dish['_id'] = str(dish['_id'])
            dishes.append({
                '_id': str(dish['_id']),
                'name': dish['name'],
                'price': dish['price'],
                'type': dish['type']
            })
    
    return jsonify({'dishes': dishes, 'day_number': day_number})

@app.route('/create_order', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    dishes = data.get('dishes', [])
    
    from datetime import datetime, timedelta
    # Устанавливаем дату на завтра
    tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Если завтра выходной, устанавливаем дату на следующий понедельник
    if tomorrow.isoweekday() > 5:
        days_until_monday = 8 - tomorrow.isoweekday()
        tomorrow = tomorrow + timedelta(days=days_until_monday)
    
    # Проверяем наличие активного заказа на завтра
    existing_order = orders_collection.find_one({
        'user': user['login'],
        'date': tomorrow,
        'status': {'$ne': "completed"}
    })

    if existing_order:
        return jsonify({
            'success': False,
            'error': 'У вас уже есть активный заказ на завтра'
        }), 400

    last_order = orders_collection.find_one(sort=[('order_id', -1)])
    new_order_id = 1 if not last_order else last_order['order_id'] + 1
    
    order = {
        'order_id': new_order_id,
        'dishes': [ObjectId(dish_id) for dish_id in dishes],
        'date': tomorrow,
        'user': user['login'],
        'status': 'ordered'  # Initialize with 'ordered' status
    }
    
    result = orders_collection.insert_one(order)
    
    return jsonify({
        'success': True,
        'order_id': new_order_id
    })

@app.route('/get_orders')
@admin_required
def get_orders():
    from datetime import datetime, timedelta

    date_str = request.args.get('date', 'today')
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if date_str == 'tomorrow':
        target_date = today + timedelta(days=1)
        if target_date.isoweekday() > 5:  # Если завтра выходной
            days_until_monday = 8 - target_date.isoweekday()
            target_date = target_date + timedelta(days=days_until_monday)
    else:  # today
        target_date = today
        if target_date.isoweekday() > 5:  # Если сегодня выходной
            target_date = target_date + timedelta(days=(8 - target_date.isoweekday()))

    # Добавляем условие completed: {'$ne': True} для исключения выполненных заказов
    orders = list(orders_collection.find({
        'date': target_date,
        'status': {'$ne': 'completed'}  # Only show non-completed orders
    }))
    
    # Преобразуем данные для отправки
    formatted_orders = []
    for order in orders:
        dishes_info = []
        for dish_id in order['dishes']:
            dish = dishes_collection.find_one({'_id': dish_id})
            if dish:
                dishes_info.append({
                    'name': dish['name'],
                    'price': dish['price'],
                    'type': dish['type']
                })
                
        formatted_orders.append({
            'order_id': order['order_id'],
            'user': order['user'],
            'dishes': dishes_info,
            'total': sum(dish['price'] for dish in dishes_info),
            'status': order.get('status', 'ordered')  # Include status in response
        })
    
    return jsonify({'orders': formatted_orders})

@app.route('/mark_order_complete', methods=['POST'])
@admin_required
def mark_order_complete():
    data = request.get_json()
    order_id = data.get('order_id')
    
    result = orders_collection.update_one(
        {'order_id': order_id},
        {'$set': {'completed': True}}
    )
    
    if result.modified_count:
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/check_active_order')
def check_active_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from datetime import datetime, timedelta
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Если завтра выходной, корректируем дату
    if tomorrow.isoweekday() > 5:
        days_until_monday = 8 - tomorrow.isoweekday()
        tomorrow = tomorrow + timedelta(days=days_until_monday)
    
    user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    
    # Ищем активные заказы на сегодня и завтра
    active_orders = list(orders_collection.find({
        'user': user['login'],
        'status': {'$ne': 'completed'},
        'date': {'$in': [today, tomorrow]}
    }))
    
    if not active_orders:
        return jsonify({'has_active_order': False})
    
    # Сортируем заказы: сначала на сегодня, потом на завтра
    active_orders.sort(key=lambda x: x['date'])
    
    formatted_orders = []
    for order in active_orders:
        dishes_info = []
        total = 0
        for dish_id in order['dishes']:
            dish = dishes_collection.find_one({'_id': dish_id})
            if dish:
                dishes_info.append({
                    'name': dish['name'],
                    'price': dish['price'],
                    'type': dish['type']
                })
                total += dish['price']
        
        formatted_orders.append({
            'order_id': order['order_id'],
            'date': 'сегодня' if order['date'] == today else 'завтра',
            'dishes': dishes_info,
            'total': total,
            'status': order.get('status', 'ordered')
        })
    
    return jsonify({
        'has_active_order': True,
        'orders': formatted_orders
    })

@app.route('/update_order_status', methods=['POST'])
@admin_required
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    if new_status not in ['ordered', 'ready', 'completed']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    result = orders_collection.update_one(
        {'order_id': order_id},
        {'$set': {'status': new_status}}
    )
    
    if result.modified_count:
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

if __name__ == '__main__':
    app.run(debug=False, port=80, host="0.0.0.0")