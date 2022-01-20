from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ChangeForm(FlaskForm):
    property = StringField("属性", validators=[DataRequired()])
    property_value = StringField("属性值")

