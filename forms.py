import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, RadioField, IntegerField

from wtforms.validators import DataRequired, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    date_of_birth = DateField('Date of birth', format='%Y-%m-%d', validators=[DataRequired()])
    sex = RadioField('Gender', choices=["Male", "Female"], validators=[DataRequired()])
    weight = IntegerField('Weight', validators=[DataRequired()])
    height = IntegerField('Height', validators=[DataRequired()])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me', validators=[DataRequired()])
    submit = SubmitField('Login')


class RecipeForm(FlaskForm):
    products = StringField("Products", validators=[DataRequired()])
    submit = SubmitField('Search')


class FoodForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField('Add food')
