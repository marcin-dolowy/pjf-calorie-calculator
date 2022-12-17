from flask import Flask, render_template
from datetime import date
import urllib.request, json
import models

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    nutrient = [food["calories"], food["totalNutrients"]["FAT"], food["totalNutrients"]["CHOCDF"],
                food["totalNutrients"]["PROCNT"]]
    return nutrient


def calculate_age(born):
    # born = datetime.datetime.strptime(date_of_born, '%Y-%m-%d')
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def max_calorie_per_day(user):
    if user.sex == "Female":
        return (665.09 + (9.56 * user.weight) + (1.85 * user.height) - (4.67 * calculate_age(user.date_of_birth))) * 1.8
    elif user.sex == "Male":
        return (66.47 + (13.75 * user.weight) + (5 * user.height) - (6.75 * calculate_age(user.date_of_birth))) * 1.8


def load_food(food_name):
    food_name = food_name.replace(' ', '%20')
    with urllib.request.urlopen(
            f"https://api.edamam.com/api/nutrition-data?app_id=cc9363d5&app_key=65d968d3d2c6390ba832d79acc283221"
            f"&nutrition-type=cooking&ingr={food_name}") as url:
        return json.load(url)


if __name__ == '__main__':
    app.run()

food = load_food("78 grams of potato")
with open('data.json', 'w') as f:
    json.dump(food, f)

# for key, value in food.items():
#     print(key, value)

# print(food["calories"])
# print("fat = ", food["totalNutrients"]["FAT"])
# print("wegle = ", food["totalNutrients"]["CHOCDF"])
# print("bialko = ", food["totalNutrients"]["PROCNT"])


user = models.User("admin", "admin", "abc", "abc", date(2000, 5, 14), "Male", None, 90, 178)
user.max_calorie = max_calorie_per_day(user)
print("wiek", calculate_age(user.date_of_birth))
print(user.max_calorie)
print(user)
# print(max_calorie_per_day(60, 25, 165))
