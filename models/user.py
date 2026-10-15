from database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    meals = db.relationship("Meal", back_populates="user")