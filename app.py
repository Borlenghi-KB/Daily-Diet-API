from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models.user import User
from models.meal import Meal
from database import db
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

migrate = Migrate(app, db)
if __name__ == "__main__":
    app.run(debug=True)
