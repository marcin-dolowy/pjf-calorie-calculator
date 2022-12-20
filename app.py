import json
import os
import urllib.request
from datetime import date

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegistrationForm, LoginForm, RecipeForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'models.db')
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
        return f"username: {self.username}, password: {self.password}, name: {self.firstname}, surname: {self.lastname}, " \
               f"sex: {self.sex}, max_calorie: {self.max_calorie}, weight: {self.weight}, height: {self.height}"


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

    def __init__(self, name, calories, protein, fat, carbohydrates, protein_calories, fat_calories,
                 carbohydrates_calories):
        self.name = name
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates
        self.protein_calories = protein_calories
        self.fat_calories = fat_calories
        self.carbohydrates_calories = carbohydrates_calories

    def __str__(self) -> str:
        return f"name: {self.name}, calories: {self.calories}, protein: {self.protein}, fat: {self.fat}, " \
               f"carbohydrates: {self.carbohydrates}"


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)

    def __init(self, products, image, ingredients):
        self.products = products
        self.image = image
        self.ingredients = ingredients


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def start():
    return render_template("base.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data,
                    date_of_birth=form.date_of_birth.data, sex=form.sex.data, max_calorie=None, weight=form.weight.data,
                    height=form.height.data)
        user.set_password(form.password1.data)
        user.max_calorie = max_calorie_per_day(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("registration.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():  # put application's code here
    if not db.engine.has_table('user'):
        db.create_all()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for("home", username=user.username))
        flash('Invalid username or password')
    return render_template("login.html", form=form)


@app.route("/home/<username>", methods=['GET', 'POST'])
def home(username):
    if not current_user.is_anonymous:
        user = User.query.filter_by(username=username).first()
        print(user)
        return render_template("newhome.html", username=username, calorie=user.max_calorie)


@app.route("/recipe", methods=['GET', 'POST'])
def recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        Recipe.query.delete()
        recipes = load_recipes(form.products.data)
        print(recipes["to"])
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

    return render_template("newrecipe.html", form=form, all_recipes=all_recipes)


def calculate_age(born):
    # born = datetime.datetime.strptime(date_of_born, '%Y-%m-%d')
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

    # products = load_recipes("chocolate, flour, cacao, egg")

    # jstr = json.dumps(productsa, ensure_ascii=True, indent=4)

    # print(jstr)

    # product = json.dumps(products)

    # print(product)

    # print(products)

    # json_encode = jstr.encode("ascii", "ignore")
    # json_decode = json_encode.decode()

    # products = json.loads(json_decode)

    # print(json_decode)

    # print(json_good)

    # products = json.loads(jstr)

    #
    # for x in range(products["to"]):
    #     print(products["hits"][x]["recipe"]["label"])
    #     print(products["hits"][x]["recipe"]["image"])
    #     print(products["hits"][x]["recipe"]["ingredientLines"])

    # food = load_food("100 grams of oatmeal")
    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(food, f, ensure_ascii=False, indent=4)

    # print(food["cautions"])

    # print(food["calories"])
    # print("fat = ", food["totalNutrients"]["FAT"])
    # print("wegle = ", food["totalNutrients"]["CHOCDF"])
    # print("bialko = ", food["totalNutrients"]["PROCNT"])
    #

    # user = User("admin", "admin", "abc", "abc", date(2000, 5, 14), "Male", None, 90, 178)
    # user.max_calorie = max_calorie_per_day(user)
    # print("wiek", calculate_age(user.date_of_birth))
    # print(user.max_calorie)
    # print(user)
    # print(max_calorie_per_day(60, 25, 165))

    # nutrient = [food["calories"], food["totalNutrients"]["FAT"], food["totalNutrients"]["CHOCDF"],
    #             food["totalNutrients"]["PROCNT"]]

    # plain_password = 'qwerty'
    # hashed_password = generate_password_hash(plain_password)
    # submitted_password = 'qwerty'
    # matching_password = check_password_hash(hashed_password, submitted_password)
    # print(matching_password)
    # print(hashed_password)
