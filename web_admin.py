from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = "orders.json"


def load_orders():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_orders(orders):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)


@app.route('/')
def index():
    # Пагинация: 1 заявка на странице (для наглядности кнопок)
    orders = load_orders()
    page = int(request.args.get('page', 1))
    per_page = 1
    total = len(orders)
    start = (page - 1) * per_page
    end = start + per_page
    order = orders[start] if orders and start < total else None
    return render_template('admin.html', order=order, page=page, total=total, per_page=per_page)


@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    orders = load_orders()
    orders = [o for o in orders if o.get('id') != order_id]
    # перенумеровать id
    for i, o in enumerate(orders, 1):
        o['id'] = i
    save_orders(orders)
    return redirect(url_for('index', page=1))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
