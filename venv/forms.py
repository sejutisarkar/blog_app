from flask_wtf import Form
from wtforms import (StringField, BooleanField,TextAreaField, PasswordField, ValidationError
                        )
from wtforms.validators import DataRequired,EqualTo,Length, Regexp,Email
from models import User


def name_exists(form,field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('username exists')
def email_exists(form ,field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('email exists')


class RegistrationForm(Form):
    username = StringField(
    'username',
    validators=[DataRequired(),
    Regexp(r'^[a-zA-Z0-9_]+$',message = ("username should be 1 word ,letter and _")),
    name_exists
    ])

    email = StringField(
    'email',
    validators=[
    DataRequired(),
    Email(),
    email_exists
    ])

    password = PasswordField(
    'password',
    validators=[
    DataRequired(),
    Length(min=7),
    EqualTo('password2',message='password must be equal')
    ])

    password2 = PasswordField(
    'confirm password',
    validators=[DataRequired()])

    is_admin = BooleanField(
    'admin',
    validators=[DataRequired()]
    )

class LoginForm(Form):
    email = StringField(
    'email',
    validators=[DataRequired(), Email()])
    password = PasswordField('password',validators=[DataRequired()])
class PostForm(Form):
    content = TextAreaField("hello",validators=[DataRequired()])
