from flask_wtf import FlaskForm

from wtforms import TextAreaField, TextField
from wtforms.validators import Email, Required


class ContactForm(FlaskForm):
    name = TextField('name', validators=[Required()])
    email = TextField('email', validators=[Required(), Email()])
    message = TextAreaField('message', validators=[Required()])
