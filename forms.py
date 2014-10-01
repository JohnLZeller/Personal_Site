from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import Required, Email

class ContactForm(Form):
    name = TextField('name', validators = [Required()])
    email = TextField('email', validators = [Required(), Email()])
    message = TextAreaField('message', validators = [Required()])