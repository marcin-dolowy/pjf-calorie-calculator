class User:
    id = None
    login = None
    password = None
    name = None
    surname = None
    date_of_birth = None
    sex = None
    max_calorie = None
    weight = None
    height = None

    def __init__(self, login, password, name, surname, date_of_birth, sex, max_calorie, weight, height):
        self.login = login
        self.password = password
        self.name = name
        self.surname = surname
        self.date_of_birth = date_of_birth
        self.sex = sex
        self.max_calorie = max_calorie
        self.weight = weight
        self.height = height

    # Do poprawy!!!!
    def __str__(self) -> str:
        return f"login: {self.login}, password: {self.password}, name: {self.name}, surname: {self.surname}, " \
               f"sex: {self.sex}, max_calorie: {self.max_calorie}, weight: {self.weight}, height: {self.height}"


class Food:
    name = None
    calories = None
    protein = None
    fat = None
    carbohydrates = None
    protein_calories = None
    fat_calories = None
    carbohydrates_calories = None

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
        return "a"


class Recipe:
    products = None
    image = None
    ingredients = None

    def __init(self, products, image, ingredients):
        self.products = products
        self.image = image
        self.ingredients = ingredients
