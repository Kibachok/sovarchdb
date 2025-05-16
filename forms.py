from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, FileField, SelectField
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
    remember me [**rmmb**],\n
    default submission field [**submit**]"""
    uname = StringField('Username (for system login)', validators=[DataRequired(),
                                                                   length(max=50, message='Too long username')])

    passwd = PasswordField('Password',
                           validators=[DataRequired(),
                                       length(min=8, max=50, message="Minimum requirement for length is 8, limit is 50")
                                       ])

    rmmb = BooleanField('Remember me')

    submit = SubmitField('Log in')


class UprofileForm(FlaskForm):
    """User login form class, includes:\n
    username [**uname**],\n
    password [**passwd**],\n
    remember me [**rmmb**],\n
    default submission field [**submit**]"""
    nickname = StringField('Nickname',
                           validators=[length(max=50, message='Too long nickname (limit is 50)')])

    rolecode = StringField('Role code [WIP]')

    save = BooleanField('Save changes', default=True)

    delete = BooleanField('Delete profile', default=False)

    submit = SubmitField('Submit')


class SerieForm(FlaskForm):
    """Serie form, includes:\n
    serie name [**name**],\n
    description [**desc**],\n
    material dropdown [**mat**],\n
    period dropdown [**period**],\n
    default submission field [**submit**]"""
    name = StringField('Serie name', validators=[DataRequired(), length(max=50, message='Too long name (limit is 50)')])

    mat = SelectField('Material', choices=('Panel', 'Brick', 'Block', 'Monolith'), validators=[DataRequired()])

    period = SelectField('Period', choices=('STAL', 'HRUSCH', 'BRZH', 'GORB', 'ELTS', 'PTN'),
                         validators=[DataRequired()])

    desc = StringField('Description', validators=[length(max=500, message='Too long description (limit is 500')])

    submit = SubmitField('Submit')


class TypeForm(FlaskForm):
    """Type form, includes:\n
    type suffix [**name**],\n
    description [**desc**],\n
    region dropdown [**region**],\n
    period dropdown [**period**],\n
    default submission field [**submit**]"""
    name = StringField('Type suffix', validators=[DataRequired(),
                                                  length(max=50, message='Too long name (limit is 50)')])

    region = SelectField('Region', choices=('I (North)', 'II (Moderate)', 'III (Warm)', 'IV (South)'),
                         validators=[DataRequired()])

    period = SelectField('Period', choices=('STAL', 'HRUSCH', 'BRZH', 'GORB', 'ELTS', 'PTN'),
                         validators=[DataRequired()])

    desc = StringField('Description', validators=[length(max=500, message='Too long description (limit is 500')])

    submit = SubmitField('Submit')
