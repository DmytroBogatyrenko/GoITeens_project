from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from online_restaurant_db import Session, Users, Menu, Orders, Reservation
from datetime import datetime
import os
import uuid
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
FILES_PATH = 'static/menu'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with Session() as db:
        return db.query(Users).get(int(user_id))


@app.before_request
def csrf_protect():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    
    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session["csrf_token"]:
            return "CSRF ERROR: Токен не дійсний", 403

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        email = request.form.get('email', f"{nickname}@rest.com") 

        with Session() as db:
            if db.query(Users).filter_by(nickname=nickname).first():
                flash("Цей псевдонім вже зайнятий!")
                return redirect(url_for('register'))

            user = Users(nickname=nickname, email=email)
            user.set_password(password)
            db.add(user)
            db.commit()
            login_user(user) 
            flash("Ласкаво просимо до ордену!")
            return redirect(url_for('home'))

    return render_template('register.html', csrf_token=session["csrf_token"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        with Session() as db:
            user = db.query(Users).filter_by(nickname=nickname).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f"Вітаємо, {nickname}!")
                return redirect(url_for('home'))
        
        flash("Невірне ім'я або пароль")
    return render_template('login.html', csrf_token=session["csrf_token"])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Ви залишили цитадель")
    return redirect(url_for('home'))

@app.route('/menu')
def menu():
    with Session() as db:
        all_positions = db.query(Menu).filter_by(active=True).all()
        return render_template('menu.html', all_positions=all_positions)

@app.route('/position/<name>', methods=['GET', 'POST'])
def position(name):
    with Session() as db:
        pos = db.query(Menu).filter_by(name=name, active=True).first()
        if not pos:
            return "Страву не знайдено", 404

        if request.method == 'POST':
            num = int(request.form.get('num', 1))
            basket = session.get('basket', {})
            basket[name] = basket.get(name, 0) + num
            session['basket'] = basket
            session.modified = True 
            flash(f"Додано {name} у торбу!")

        return render_template('position.html', position=pos, csrf_token=session["csrf_token"])

@app.route('/create_order', methods=['GET', 'POST'])
@login_required
def create_order():
    basket = session.get('basket', {})
    if request.method == 'POST':
        if not basket:
            flash("Ваша торба порожня!")
            return redirect(url_for('menu'))

        with Session() as db:
            new_order = Orders(
                order_list=basket,
                order_time=datetime.now(),
                user_id=current_user.id
            )
            db.add(new_order)
            db.commit()
            order_id = new_order.id
            
        session.pop('basket', None)
        flash("Замовлення прийнято!")
        return redirect(url_for('my_order', id=order_id))

    return render_template('create_order.html', basket=basket, csrf_token=session["csrf_token"])

@app.route('/reserved', methods=['GET', 'POST'])
@login_required
def reserved():
    message = ""
    if request.method == 'POST':
        table_type = request.form.get('table_type')
        time_str = request.form.get('time')

        try:
            with Session() as db:
                new_res = Reservation(
                    type_table=table_type,
                    time_start=datetime.strptime(time_str, "%Y-%m-%dT%H:%M"),
                    user_id=current_user.id
                )
                db.add(new_res)
                db.commit()
            message = "Місце в залі заброньовано!"
        except Exception as e:
            message = "Помилка дати. Спробуйте ще раз."

    return render_template('reserved.html', message=message, csrf_token=session["csrf_token"])

@app.route('/my_orders')
@login_required
def my_orders():
    with Session() as db:
        orders = db.query(Orders).filter_by(user_id=current_user.id).all()
        return render_template('my_orders.html', us_orders=orders)

@app.route('/my_order/<int:id>')
@login_required
def my_order(id):
    with Session() as db:
        order = db.query(Orders).filter_by(id=id, user_id=current_user.id).first()
        if not order:
            return "Замовлення не знайдено", 404

        total = 0
        detailed_items = []
        for name, qty in order.order_list.items():
            pos = db.query(Menu).filter_by(name=name).first()
            if pos:
                price = pos.price * int(qty)
                total += price
                detailed_items.append({'name': name, 'qty': qty, 'price': price})

        return render_template('my_order.html', order=order, items=detailed_items, total_price=total)

@app.route('/add_position', methods=['GET', 'POST'])
@login_required
def add_position():
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = f"{uuid.uuid4()}_{file.filename}"
            if not os.path.exists(FILES_PATH):
                os.makedirs(FILES_PATH)
            file.save(os.path.join(FILES_PATH, filename))

            with Session() as db:
                pos = Menu(
                    name=request.form['name'],
                    ingredients=request.form['ingredients'],
                    description=request.form['description'],
                    price=int(request.form['price']),
                    weight=request.form['weight'],
                    file_name=filename
                )
                db.add(pos)
                db.commit()
            flash("Нова страва викована!")
            return redirect(url_for('menu'))

    return render_template('add_position.html', csrf_token=session["csrf_token"])

if __name__ == '__main__':
    app.run(debug=True, port=8000)