import json
import os
import urllib.request
from datetime import date

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegistrationForm, LoginForm, RecipeForm, FoodForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'models.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(150))
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    date_of_birth = db.Column(db.DateTime())
    sex = db.Column(db.String(10))
    max_calorie = db.Column(db.Float(precision=2))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    foods = db.relationship("Food", backref='user')

    def __init__(self, username, firstname, lastname, date_of_birth, sex, max_calorie, weight, height):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.date_of_birth = date_of_birth
        self.sex = sex
        self.max_calorie = max_calorie
        self.weight = weight
        self.height = height

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self) -> str:
        return f"username: {self.username}, password: {self.password}, name: {self.firstname}, " \
               f"surname: {self.lastname},"f"sex: {self.sex}, max_calorie: {self.max_calorie}, " \
               f"weight: {self.weight}, height: {self.height}"


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    calories = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)
    protein_calories = db.Column(db.Integer)
    fat_calories = db.Column(db.Integer)
    carbohydrates_calories = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self) -> str:
        return f"name: {self.name}, calories: {self.calories}, protein: {self.protein_calories}, " \
               f"fat: {self.fat_calories}, "f"carbohydrates: {self.carbohydrates_calories}"


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def start_page():
    return render_template('start_page.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = FoodForm()
    if form.validate_on_submit():
        user_food = load_food(form.name.data)

        if user_food['totalNutrients']:
            food = Food(name=form.name.data, calories=user_food['calories'],
                        protein=round(user_food["totalNutrients"]["PROCNT"]['quantity'], 2),
                        fat=round(user_food["totalNutrients"]["FAT"]['quantity'], 2),
                        carbohydrates=round(user_food["totalNutrients"]["CHOCDF"]['quantity'], 2),
                        protein_calories=user_food['totalNutrientsKCal']['PROCNT_KCAL']['quantity'],
                        fat_calories=user_food['totalNutrientsKCal']['FAT_KCAL']['quantity'],
                        carbohydrates_calories=user_food['totalNutrientsKCal']['CHOCDF_KCAL']['quantity'],
                        user_id=current_user.id)

            db.session.add(food)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash("Food not found!")

    name_surname = " ".join([current_user.firstname, current_user.lastname])

    all_calories = Food.query.filter(Food.user_id == current_user.id).with_entities(
        func.sum(Food.calories).label('total')).first().total or 0

    remaining_calories = current_user.max_calorie - all_calories

    all_foods = Food.query.filter(Food.user_id == current_user.id)

    all_protein = Food.query.filter(Food.user_id == current_user.id).with_entities(
        func.sum(Food.protein).label('total')).first().total
    all_protein = 0 if all_protein is None else round(all_protein, 2)

    all_fat = Food.query.filter(Food.user_id == current_user.id).with_entities(
        func.sum(Food.fat).label('total')).first().total or 0
    all_fat = 0 if all_fat is None else round(all_fat, 2)

    all_carbohydrates = Food.query.filter(Food.user_id == current_user.id).with_entities(
        func.sum(Food.carbohydrates).label('total')).first().total or 0
    all_carbohydrates = 0 if all_carbohydrates is None else round(all_carbohydrates, 2)

    return render_template("home.html", form=form, name_surname=name_surname, max_calorie=current_user.max_calorie,
                           remaining_calories=remaining_calories, all_foods=all_foods, all_protein=all_protein,
                           all_fat=all_fat, all_carbohydrates=all_carbohydrates, user=current_user)


@app.route('/delete/<int:food_id>')
def delete(food_id):
    food_to_delete = Food.query.get_or_404(food_id)
    db.session.delete(food_to_delete)
    db.session.commit()
    flash("Food was removed successfully!")
    return redirect(url_for('home'))


@app.route('/delete_account')
@login_required
def delete_account():
    Food.query.filter(Food.user_id == current_user.id).delete()
    Recipe.query.delete()
    user = User.query.get(current_user.id)

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if not db.engine.has_table('user'):
        db.create_all()

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for("home"))
        flash('Invalid username or password')
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        if User.query.filter_by(username=form.username.data).first():
            flash("Account with this username already exists!")
            return render_template("registration.html", form=form)

        else:
            user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data,
                        date_of_birth=form.date_of_birth.data, sex=form.sex.data, max_calorie=None,
                        weight=form.weight.data, height=form.height.data)
            user.set_password(form.password1.data)
            user.max_calorie = max_calorie_per_day(user)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template("registration.html", form=form)


@app.route("/recipe", methods=['GET', 'POST'])
@login_required
def recipe():
    form = RecipeForm()

    if form.validate_on_submit():
        Recipe.query.delete()
        recipes = load_recipes(form.products.data)

        if recipes['count'] == 0:
            flash("Recipes not found! Try again")

        else:
            for x in range(recipes["to"]):
                ingredients_list = recipes["hits"][x]["recipe"]["ingredientLines"]
                ingredients_str = '\n'.join(str(x) for x in ingredients_list)
                ingredients_str = ingredients_str.replace('\n', '<br />')

                new_recipe = Recipe(name=recipes["hits"][x]["recipe"]["label"], products=form.products.data,
                                    image=recipes["hits"][x]["recipe"]["image"], ingredients=ingredients_str)
                db.session.add(new_recipe)
                db.session.commit()

            return redirect('/recipe')

    all_recipes = Recipe.query.all()

    return render_template("recipe.html", form=form, all_recipes=all_recipes)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def max_calorie_per_day(user):
    if user.sex == "Female":
        return round(
            (665.09 + (9.56 * user.weight) + (1.85 * user.height) - (4.67 * calculate_age(user.date_of_birth))) * 1.8)
    elif user.sex == "Male":
        return round(
            (66.47 + (13.75 * user.weight) + (5 * user.height) - (6.75 * calculate_age(user.date_of_birth))) * 1.8)


def load_food(food_name):
    food_name = food_name.replace(' ', '%20')
    with urllib.request.urlopen(
            f"https://api.edamam.com/api/nutrition-data?app_id=cc9363d5&app_key=65d968d3d2c6390ba832d79acc283221"
            f"&nutrition-type=cooking&ingr={food_name}") as url:
        return json.load(url)


def load_recipes(products):
    products = products.replace(' ', "%20").replace(',', '%2C')
    with urllib.request.urlopen(
            f"https://api.edamam.com/api/recipes/v2?type=public&q={products}&app_id=f1d7281d"
            "&app_key=817b53a2c50fcaff7a67b2609f4e7894&random=true") as url:
        return json.load(url)


if __name__ == '__main__':
    app.run(debug=True)
