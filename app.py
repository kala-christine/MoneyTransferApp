from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Transaction

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return "Backend + Database working 🚀"

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "balance": user.balance
        })

    return jsonify(result)


@app.route('/send_money', methods=['POST'])
def send_money():
    data = request.get_json()

    sender = User.query.get(data['sender_id'])
    receiver = User.query.get(data['receiver_id'])
    amount = data['amount']

    if not sender or not receiver:
        return jsonify({"error": "User not found"}), 404

    if sender.id == receiver.id:
        return jsonify({"error": "Cannot send to yourself"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

    if sender.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    sender.balance -= amount
    receiver.balance += amount

    transaction = Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=amount
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "Transaction successful"})


@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()

    result = []

    for t in transactions:
        sender = User.query.get(t.sender_id)
        receiver = User.query.get(t.receiver_id)

        result.append({
            "id": t.id,
            "sender": sender.name,
            "receiver": receiver.name,
            "amount": t.amount
        })

    return jsonify(result)

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    user = User(
        name=data.get('name'),
        email=data.get('email'),
        balance=data.get('balance', 0)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User added successfully"})    

@app.route('/dashboard', methods=['GET'])
def dashboard():
    total_users = User.query.count()
    total_transactions = Transaction.query.count()

    transactions = Transaction.query.all()

    total_transferred = 0
    for t in transactions:
        total_transferred += t.amount

    users = User.query.all()

    total_balance = 0
    for user in users:
        total_balance += user.balance

    return jsonify({
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_transferred": total_transferred,
        "total_balance": total_balance
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)