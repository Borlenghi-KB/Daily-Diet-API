from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models.user import User
from models.meal import Meal
from database import db
from datetime import datetime
from flask_login import current_user
from flask_login import LoginManager, login_user, logout_user, login_required

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://kaique:kaka@localhost:3306/DailyDiet"

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    senha = data.get("senha")

    if not username or not senha:
        return jsonify({"message": "Missing required fields"}), 400

    user = User.query.filter_by(name=username).first()
    if user and user.senha == senha:
        login_user(user)
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username")
    senha = data.get("senha")
    
    if not username or not senha:
        return jsonify({"message": "Missing required fields"}), 400 
    
    user = User(name=username, senha=senha)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/user/<int:id>', methods=['GET'])
@login_required
def read_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({"id": user.id, "name": user.name}), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/user/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    username = data.get("username")
    senha = data.get("senha")

    if username:
        user.name = username
    if senha:
        user.senha = senha

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/user/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

#---------------------- MEAL ROUTES ----------------------# 

def parse_data_time(value):
    if not isinstance(value, str):
        raise ValueError("Invalid date and time")
    return datetime.fromisoformat(value)


@app.route("/meal", methods=["POST"])
@login_required
def create_meal():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    description = data.get("description")
    is_on_diet = data.get("is_on_diet")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"message": "name is required"}), 400
    if not isinstance(description, str) or not description.strip():
        return jsonify({"message": "description is required"}), 400
    if not isinstance(is_on_diet, bool):
        return jsonify({"message": "is_on_diet must be true or false"}), 400

    try:
        date_time = parse_data_time(data.get("date_time"))
    except ValueError:
        return jsonify({"message": "Invalid date_time. Use, for example, 2026-10-15T12:30:00"}), 400

    meal = Meal(
        name=name.strip(),
        description=description.strip(),
        date_time=date_time,
        is_on_diet=is_on_diet,
        user_id=current_user.id,
    )
    db.session.add(meal)
    db.session.commit()

    return jsonify({"message": "Meal created successfully", "id": meal.id}), 201


@app.route("/meal/<int:id>", methods=["GET"])
@login_required
def read_meal(id):
    meal = Meal.query.filter_by(id=id, user_id=current_user.id).first()
    if meal is None:
        return jsonify({"message": "Meal not found"}), 404

    return jsonify({
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "date_time": meal.date_time.isoformat(),
        "is_on_diet": meal.is_on_diet,
        "user_id": meal.user_id,
    }), 200

@app.route("/meals", methods=["GET"])
@login_required
def list_meals():
    meals = Meal.query.filter_by(user_id=current_user.id).all()

    return jsonify([{
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "date_time": meal.date_time.isoformat(),
        "is_on_diet": meal.is_on_diet,
        "user_id": meal.user_id,
    } for meal in meals]), 200

@app.route("/meal/<int:id>", methods=["PUT"])
@login_required
def update_meal(id):
    meal = Meal.query.filter_by(id=id, user_id=current_user.id).first()
    if meal is None:
        return jsonify({"message": "Meal not found"}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return jsonify({"message": "Invalid name"}), 400
        meal.name = data["name"].strip()

    if "description" in data:
        if not isinstance(data["description"], str) or not data["description"].strip():
            return jsonify({"message": "Invalid description"}), 400
        meal.description = data["description"].strip()

    if "date_time" in data:
        try:
            meal.date_time = parse_data_time(data["date_time"])
        except ValueError:
            return jsonify({"message": "Invalid date_time"}), 400

    if "is_on_diet" in data:
        if not isinstance(data["is_on_diet"], bool):
            return jsonify({"message": "is_on_diet must be true or false"}), 400
        meal.is_on_diet = data["is_on_diet"]

    db.session.commit()
    return jsonify({"message": "Meal updated successfully"}), 200

@app.route("/meal/<int:id>", methods=["DELETE"])
@login_required
def delete_meal(id):
    meal = Meal.query.filter_by(id=id, user_id=current_user.id).first()
    if meal is None:
        return jsonify({"message": "Meal not found"}), 404

    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Meal deleted successfully"}), 200

migrate = Migrate(app, db)
if __name__ == "__main__":
    app.run(debug=True)
