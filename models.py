# from flask_sqlalchemy import SQLAlchemy
#
# from app import app
#
# db = SQLAlchemy(app)
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     login = db.Column(db.String(50))
#     password = db.Column(db.String(50))
#     name = db.Column(db.String(50))
#     surname = db.Column(db.String(50))
#     date_of_birth = db.Column(db.DateTime)
#     sex = db.Column(db.String(10))
#     max_calorie = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
#     weight = db.Column(db.Integer)
#     height = db.Column(db.Integer)
#     foods = db.relationship("Food", backref='user')
#
#     def __init__(self, login, password, name, surname, date_of_birth, sex, max_calorie, weight, height):
#         self.login = login
#         self.password = password
#         self.name = name
#         self.surname = surname
#         self.date_of_birth = date_of_birth
#         self.sex = sex
#         self.max_calorie = max_calorie
#         self.weight = weight
#         self.height = height
#
#     def __str__(self) -> str:
#         return f"login: {self.login}, password: {self.password}, name: {self.name}, surname: {self.surname}, " \
#                f"sex: {self.sex}, max_calorie: {self.max_calorie}, weight: {self.weight}, height: {self.height}"
#
#
# class Food(db.Model):
#     name = db.Column(db.String(50))
#     calories = db.Column(db.Integer)
#     protein = db.Column(db.Integer)
#     fat = db.Column(db.Integer)
#     carbohydrates = db.Column(db.Integer)
#     protein_calories = db.Column(db.Integer)
#     fat_calories = db.Column(db.Integer)
#     carbohydrates_calories = db.Column(db.Integer)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __init__(self, name, calories, protein, fat, carbohydrates, protein_calories, fat_calories,
#                  carbohydrates_calories):
#         self.name = name
#         self.calories = calories
#         self.protein = protein
#         self.fat = fat
#         self.carbohydrates = carbohydrates
#         self.protein_calories = protein_calories
#         self.fat_calories = fat_calories
#         self.carbohydrates_calories = carbohydrates_calories
#
#     def __str__(self) -> str:
#         return f"name: {self.name}, calories: {self.calories}, protein: {self.protein}, fat: {self.fat}, carbohydrates: {self.carbohydrates}"
#
#
# class Recipe(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     products = db.Column(db.String(500), nullable=False)
#     image = db.Column(db.String(500), nullable=False)
#     ingredients = db.Column(db.String(500), nullable=False)
#
#     def __init(self, products, image, ingredients):
#         self.products = products
#         self.image = image
#         self.ingredients = ingredients
