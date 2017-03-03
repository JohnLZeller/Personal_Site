from flask.ext.wtf import Form

from wtforms import TextAreaField, TextField
from wtforms.validators import Email, Required


class ContactForm(Form):
    name = TextField('name', validators=[Required()])
    email = TextField('email', validators=[Required(), Email()])
    message = TextAreaField('message', validators=[Required()])
