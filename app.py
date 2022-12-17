from datetime import date

from flask import Flask

import models

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return "Hello world"


def calculate_age(born):
    # born = datetime.datetime.strptime(date_of_born, '%Y-%m-%d')
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def max_calorie_per_day(user):
    if user.sex == "Female":
        return (665.09 + (9.56 * user.weight) + (1.85 * user.height) - (4.67 * calculate_age(user.date_of_birth))) * 1.8
    elif user.sex == "Male":
        return (66.47 + (13.75 * user.weight) + (5 * user.height) - (6.75 * calculate_age(user.date_of_birth))) * 1.8


if __name__ == '__main__':
    app.run()

user = models.User("admin", "admin", "abc", "abc", date(2000, 5, 14), "Female", None, 55, 171)
user.max_calorie = max_calorie_per_day(user)
print("wiek", calculate_age(user.date_of_birth))
print(user.max_calorie)
print(user)
# print(max_calorie_per_day(60, 25, 165))
