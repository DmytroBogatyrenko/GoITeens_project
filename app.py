from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify, Response, stream_with_context
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import Session as FlaskSession
from online_restaurant_db import Session, Users, Menu, Orders, Reservation
from datetime import datetime
import os
import uuid
import secrets
import json
import random

from google.genai import types
from oracle_core.spirit import OracleManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super_secret_medieval_key_2026'
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
FlaskSession(app)

FILES_PATH = 'static/menu'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(FILES_PATH):
    os.makedirs(FILES_PATH)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with Session() as db:
        return db.get(Users, int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_menu_for_oracle():

    return "М'ясо, вино, хліб."


@app.before_request
def csrf_and_setup():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

    if request.path == '/ask_oracle':
        return 

    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session["csrf_token"]:
            return "CSRF ERROR: Оновіть сторінку", 403

@app.route('/ask_oracle', methods=['POST'])
def ask_oracle():
    try:
        data = request.get_json(silent=True) or {}
        user_text = data.get('message', '').strip()
        
        if not user_text:
            return jsonify({"reply": "Твої думки занадто тихі..."})

        current_menu = get_menu_for_oracle()
        history_data = session.get("chat_history", []) # виправити

        def generate():
            full_response_text = ""
            try:
                response = OracleManager.generate_response(history_data, user_text, current_menu)
                
                for chunk in response:
                    if chunk.text:
                        full_response_text += chunk.text
                        yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"

                history_data.append({"role": "user", "text": user_text})
                history_data.append({"role": "model", "text": full_response_text})
                session["chat_history"] = history_data[-4:] 
                session.modified = True

            except Exception as e:
                print(f"Streaming Error: {e}")
                error_string = str(e)
                yield f"data: {json.dumps({'error': error_string})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        print(f"ORACLE ERROR: {e}")
        return jsonify({"reply": "Магічний зв'язок перервано..."}), 500
    
@app.route('/reset_chat')
def reset_chat():
    session.pop('chat_history', None)
    flash("Пам'ять Оракула очищена!")
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def menu():
    with Session() as db:
        all_positions = db.query(Menu).filter_by(active=True).all()
        return render_template('menu.html', all_positions=all_positions)

@app.route('/position/<name>', methods=['GET', 'POST'])
def position(name):
    with Session() as db:
        pos = db.query(Menu).filter_by(name=name, active=True).first()
        if not pos: return "Страву не знайдено", 404
        if request.method == 'POST':
            num = int(request.form.get('num', 1))
            basket = session.get('basket', {})
            basket[name] = basket.get(name, 0) + max(1, num)
            session['basket'] = basket
            session.modified = True
            flash(f"Додано {name} у торбу!")
            return redirect(url_for('menu')) 
        return render_template('position.html', position=pos, csrf_token=session["csrf_token"])

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    name = request.form.get('name')
    num_str = request.form.get('num', 1)
    try:
        num = int(num_str)
    except ValueError:
        num = 1
    with Session() as db:
        pos = db.query(Menu).filter_by(name=name).first()
        if not pos:
            flash("Страву не знайдено!")
            return redirect(url_for('menu'))
    basket = session.get('basket', {})
    basket[name] = basket.get(name, 0) + max(1, num)
    session['basket'] = basket
    session.modified = True 
    flash(f"Додано {name} у торбу!")
    return redirect(url_for('menu'))

@app.route('/remove_from_basket/<name>')
def remove_from_basket(name):
    basket = session.get('basket', {})
    if name in basket:
        del basket[name]
        session['basket'] = basket
        session.modified = True
    return redirect(url_for('create_order'))

@app.route('/create_order', methods=['GET', 'POST'])
@login_required
def create_order():
    basket = session.get('basket', {})
    
    if request.method == 'POST':
        if not basket:
            flash("Торба порожня!")
            return redirect(url_for('menu'))
        with Session() as db:
            # Зберігаємо замовлення
            new_order = Orders(order_list=basket, order_time=datetime.now(), user_id=current_user.id)
            db.add(new_order)
            db.commit()
            order_id = new_order.id 
            session.pop('basket', None) 
            flash("Гінець полетів на кухню!")
            return redirect(url_for('my_order', id=order_id))

    # Логіка для GET (відображення торби)
    items_to_show = []
    total = 0
    all_times = []
    
    with Session() as db:
        for name, qty in basket.items():
            pos = db.query(Menu).filter_by(name=name).first()
            if pos:
                items_to_show.append({
                    'name': name, 
                    'qty': qty, 
                    'price': pos.price * qty,
                    'prep_time': pos.prep_time  # Додаємо час сюди
                })
                total += pos.price * qty
                all_times.append(pos.prep_time)
    
    # Визначаємо найдовшу страву
    max_time = max(all_times) if all_times else 0
    
    return render_template('create_order.html', 
                           basket=items_to_show, 
                           total=total, 
                           max_time=max_time, 
                           csrf_token=session["csrf_token"])

@app.route('/my_orders')
@login_required
def my_orders():
    with Session() as db:
        orders = db.query(Orders).filter_by(user_id=current_user.id).order_by(Orders.order_time.desc()).all()
        return render_template('my_orders.html', us_orders=orders)

@app.route('/my_order/<int:id>')
@login_required
def my_order(id):
    with Session() as db:
        order = db.query(Orders).filter_by(id=id, user_id=current_user.id).first()
        if not order: abort(404)
        
        total = 0
        items = []
        all_times = []
        
        for name, qty in order.order_list.items():
            pos = db.query(Menu).filter_by(name=name).first()
            if pos:
                price = pos.price * int(qty)
                total += price
                items.append({
                    'name': name, 
                    'qty': qty, 
                    'price': price, 
                    'prep_time': pos.prep_time  # Додаємо час
                })
                all_times.append(pos.prep_time)
        
        max_wait = max(all_times) if all_times else 0
        
        return render_template('my_order.html', 
                               order=order, 
                               items=items, 
                               total_price=total, 
                               max_wait=max_wait)

@app.route('/add_position', methods=['GET', 'POST'])
@login_required
def add_position():
    if current_user.nickname != 'Admin':
        flash("Доступ лише для Адміністратора!")
        return redirect(url_for('home'))
    if request.method == 'POST':
        file = request.files.get('file')
        image_url = request.form.get('image_url') 
        filename = "default.jpg"
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{file.filename}"
            file.save(os.path.join(FILES_PATH, filename))
        elif image_url: filename = image_url
        with Session() as db:
            pos = Menu(
                name=request.form.get('name'),
                ingredients=request.form.get('ingredients'),
                description=request.form.get('description'),
                price=int(request.form.get('price', 0)),
                weight=request.form.get('weight', '0'),
                prep_time=int(request.form.get('prep_time', 15)),
                file_name=filename,
                active=True
            )
            db.add(pos)
            db.commit()
        flash("Страву додано!")
        return redirect(url_for('menu')) 
    return render_template('add_position.html', csrf_token=session["csrf_token"])

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email']
        password = request.form['password']
        with Session() as cursor:
            if cursor.query(Users).filter_by(email=email).first() or cursor.query(Users).filter_by(nickname=nickname).first():
                flash('Користувач вже існує!')
                return render_template('register.html', csrf_token=session["csrf_token"])
            new_user = Users(nickname=nickname, email=email)
            new_user.set_password(password)
            cursor.add(new_user)
            cursor.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('register.html', csrf_token=session["csrf_token"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nick = request.form.get('nickname')
        pwd = request.form.get('password')
        with Session() as db:
            user = db.query(Users).filter_by(nickname=nick).first()
            if user and user.check_password(pwd):
                login_user(user)
                return redirect(url_for('menu'))
            flash("Невірне ім'я або закляття!")
    return render_template('login.html', csrf_token=session.get("csrf_token"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/reserved', methods=['GET', 'POST'])
@login_required
def reserved():
    message = ""
    if request.method == 'POST':
        table_type = request.form.get('table_type')
        time_str = request.form.get('time')
        try:
            formatted_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
            with Session() as db:
                new_res = Reservation(type_table=table_type, time_start=formatted_time, user_id=current_user.id)
                db.add(new_res)
                db.commit()
            message = "Бронювання підтверджено!"
        except: message = "Помилка дати."
    return render_template('reserved.html', message=message, csrf_token=session["csrf_token"])

@app.route('/admin_panel')
@login_required
def admin_panel():
    # Робимо перевірку незалежно від того, Admin чи admin написав користувач
    if current_user.nickname.lower() != 'admin':
        flash("Лише головний Лорд має доступ до цієї зали!")
        return redirect(url_for('home'))
    
    with Session() as db:
        # Завантажуємо замовлення
        all_orders = db.query(Orders).order_by(Orders.order_time.desc()).all()
        # Важливо: передаємо csrf_token, бо він потрібен для кнопки "Виконано"
        return render_template('admin_panel.html', 
                               all_orders=all_orders, 
                               csrf_token=session.get("csrf_token"))

@app.route('/delete_order/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    if current_user.nickname != 'Admin':
        abort(403)
        
    with Session() as db:
        order = db.query(Orders).filter_by(id=id).first()
        if order:
            db.delete(order)
            db.commit()
            flash(f"Замовлення №{id} успішно виконано та видалено!")
        else:
            flash("Замовлення не знайдено.")
            
    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
    
    