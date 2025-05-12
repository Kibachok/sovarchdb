from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, BooleanField
from wtforms.validators import DataRequired, equal_to, length


class RegisterForm(FlaskForm):
    """Registration form class, includes:\n
    username [**uname**],\n
    password [**passwd**],\n
    password repeat [**passwd_r**]\n
    optional nickname [**nickname**],\n
    default submission field [**submit**]"""
    uname = StringField('Username (for system login)', validators=[DataRequired(),
                                                                   length(max=50,
                                                                          message='Too long username (limit is 50')])

    passwd = PasswordField('Password',
                           validators=[DataRequired(),
                                       length(min=8, max=50, message="Minimum requirement for length is 8, limit is 50")
                                       ])

    passwd_r = PasswordField('Repeat password',
                             validators=[DataRequired(),
                                         equal_to('passwd', 'Passwords are different')])

    nickname = StringField('Nickname (to be shown) (optional, username is used otherwise)',
                           validators=[length(max=50, message='Too long nickname (limit is 50)')])

    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User login form class, includes:\n
    username [**uname**],\n
    password [**passwd**],\n
    default submission field [**submit**]"""
    uname = StringField('Username (for system login)', validators=[DataRequired(),
                                                                   length(max=50, message='Too long username')])

    passwd = PasswordField('Password',
                           validators=[DataRequired(),
                                       length(min=8, max=50, message="Minimum requirement for length is 8, limit is 50")
                                       ])

    submit = SubmitField('Log in')
